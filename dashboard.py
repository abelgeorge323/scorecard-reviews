import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from pathlib import Path
import re

# Import mappings
from mappings import account_to_vertical, account_name_variations

# Page configuration
st.set_page_config(
    page_title="Top 55 Accounts Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .account-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .account-card-no-data {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #cccccc;
        margin: 10px 0;
        text-align: center;
        color: #666;
    }
    .vertical-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px 0;
    }
    .score-high { color: #28a745; font-weight: bold; font-size: 24px; }
    .score-medium { color: #ffc107; font-weight: bold; font-size: 24px; }
    .score-low { color: #dc3545; font-weight: bold; font-size: 24px; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    
</style>
""", unsafe_allow_html=True)

def clean_text(text):
    """Clean up encoding issues in text"""
    if pd.isna(text) or not isinstance(text, str):
        return text
    
    # Replace common encoding issues with proper characters
    replacements = {
        '�': "'",  # Replace � with regular apostrophe
        '\x92': "'",  # Another apostrophe variant
        '\x93': '"',  # Opening smart quote
        '\x94': '"',  # Closing smart quote
        '\x96': '–',  # En dasha
        '\x97': '—',  # Em dash
        '\x91': "'",  # Left single quote
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2013': '–',  # En dash
        '\u2014': '—',  # Em dash
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def get_available_months():
    """Detect available month CSV files"""
    scorecards_dir = Path("Scorecards")
    months = []
    
    # Look for files matching pattern: MonthName_YYYY_Scorecards.csv
    pattern = re.compile(r'(\w+)_(\d{4})_Scorecards\.csv', re.IGNORECASE)
    
    for file in scorecards_dir.glob("*_*_Scorecards.csv"):
        match = pattern.match(file.name)
        if match:
            month_name, year = match.groups()
            months.append(f"{month_name}_{year}")
    
    # Also check for legacy files (current format) - assume it's November 2025
    legacy_files = list(scorecards_dir.glob("Scorecard Review Executive Summary*.csv"))
    if legacy_files:
        # Add November 2025 if not already in list
        if "November_2025" not in months:
            months.append("November_2025")
    
    return sorted(months, reverse=True)  # Most recent first

@st.cache_data(ttl=60)  # Cache for 60 seconds only
def load_data(month=None):
    """Load and process the CSV data with caching"""
    scorecards_dir = Path("Scorecards")
    
    if month:
        # Load specific month file
        if month == "November_2025":
            # Check for legacy file format first - try file (8) first, then (5), then new format
            legacy_path_8 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (8).csv")
            legacy_path_5 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (5).csv")
            if legacy_path_8.exists():
                csv_path = legacy_path_8
            elif legacy_path_5.exists():
                csv_path = legacy_path_5
            else:
                csv_path = scorecards_dir / f"{month}_Scorecards.csv"
        else:
            csv_path = scorecards_dir / f"{month}_Scorecards.csv"
    else:
        # Default: try to find latest month or fallback to current file
        available_months = get_available_months()
        if available_months:
            month_key = available_months[0]
            if month_key == "November_2025":
                # Check for legacy file format first - try file (8) first, then (5), then new format
                legacy_path_8 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (8).csv")
                legacy_path_5 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (5).csv")
                if legacy_path_8.exists():
                    csv_path = legacy_path_8
                elif legacy_path_5.exists():
                    csv_path = legacy_path_5
                else:
                    csv_path = scorecards_dir / f"{month_key}_Scorecards.csv"
            else:
                csv_path = scorecards_dir / f"{month_key}_Scorecards.csv"
        else:
            # Fallback to current file format - try file (8) first, then (5)
            legacy_path_8 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (8).csv")
            legacy_path_5 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (5).csv")
            if legacy_path_8.exists():
                csv_path = legacy_path_8
            else:
                csv_path = legacy_path_5
    
    if not csv_path.exists():
        # Return None if file doesn't exist (for blank state)
        return None
    
    # Try multiple encodings to handle special characters
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            
            # Clean all text columns to fix encoding issues
            for col in df.columns:
                if df[col].dtype == 'object':  # String columns
                    df[col] = df[col].apply(clean_text)
            
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return None
    
    st.error(f"Could not read CSV with any standard encoding. Please check the file.")
    return None

def normalize_account_name(account_name):
    """Normalize account name using fuzzy matching dictionary"""
    if pd.isna(account_name):
        return None
    
    account_str = str(account_name).strip()
    
    # Check if it should be omitted
    if account_str in account_name_variations and account_name_variations[account_str] is None:
        return None
    
    # Check variations dictionary
    if account_str in account_name_variations:
        return account_name_variations[account_str]
    
    # Check if exact match exists in account_to_vertical
    if account_str in account_to_vertical:
        return account_str
    
    # Case-insensitive check in account_to_vertical
    for key in account_to_vertical.keys():
        if key.lower() == account_str.lower():
            return key
    
    # If no match found, return original (will be filtered out later)
    return account_str

@st.cache_data(ttl=60)  # Cache for 60 seconds only
def process_data(df):
    """Process and enrich data with verticals"""
    if df is None or len(df) == 0:
        return pd.DataFrame()  # Return empty dataframe instead of None
    
    # Normalize account names
    df['Account_Normalized'] = df['Name of Account/Portfolio'].apply(normalize_account_name)
    
    # Filter out None values (omitted accounts)
    df = df[df['Account_Normalized'].notna()].copy()
    
    # Add vertical based on normalized account name
    df['Vertical'] = df['Account_Normalized'].map(account_to_vertical)
    
    # Filter out accounts not in our mapping
    df = df[df['Vertical'].notna()].copy()
    
    # Parse the score column - handle various formats
    def parse_score(score_str):
        if pd.isna(score_str):
            return None
        
        score_str = str(score_str).strip()
        
        # Handle N/A
        if score_str.upper() == 'N/A':
            return None
        
        # Handle formats like "4.68", "5", "4.0"
        try:
            return float(score_str)
        except:
            pass
        
        # Handle formats like "4.93/5.00" or "3.93/5.00"
        if '/' in score_str:
            try:
                numerator = float(score_str.split('/')[0])
                return numerator
            except:
                pass
        
        # Extract score from text like "Every site scored a 5 this month"
        score_patterns = [
            r'SBM\s+(\d+\.?\d*)',                # "SBM 4.25" or "SBM - 5."
            r'scored?\s+(?:a\s+)?(\d+\.?\d*)',  # "scored a 5" or "score 4.5"
            r'(\d+\.?\d*)\s+out\s+of',          # "5 out of 5"
            r'score[d]?\s+(?:of\s+)?(\d+\.?\d*)', # "score of 5"
            r'(\d+\.?\d*)/5',                    # "5/5"
            r'all\s+(?:sites?\s+)?(?:scored?\s+)?(?:a\s+)?(\d+\.?\d*)', # "all sites scored a 5"
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, score_str.lower())
            if match:
                try:
                    score = float(match.group(1))
                    # Validate score is reasonable (0-5 range)
                    if 0 <= score <= 5:
                        return score
                except:
                    pass
        
        # Extract multiple scores and average them (e.g., "Bloomfield – 4.0 St. Louis – 5.0")
        numbers = re.findall(r'(\d+\.?\d*)', score_str)
        if numbers:
            try:
                # Convert to floats and filter to valid score range (0-5)
                valid_scores = [float(n) for n in numbers if 0 <= float(n) <= 5]
                if valid_scores:
                    return sum(valid_scores) / len(valid_scores)  # Return average
            except:
                pass
        
        return None
    
    df['Score'] = df['What was the overall Scorecard Score?'].apply(parse_score)
    
    # Parse dates
    df['Review_Date'] = pd.to_datetime(df['Date/Time of Scorecard Review?'], errors='coerce')
    df['Completion_Date'] = pd.to_datetime(df['Completion time'], errors='coerce')
    
    return df

def build_summary_with_sites(account, latest_row, account_df):
    """Build summary with site-specific scores if multiple locations"""
    base_summary = latest_row.get('Summary of Review\nWhat did you cover during the review? Please provide a brief summary of what was covered.\n\n', 'N/A')
    
    # Check if score field contains multiple sites (like Cigna)
    score_field = str(latest_row.get('What was the overall Scorecard Score?', ''))
    
    # If multiple scores detected in the score field, add breakdown at the top
    if ('–' in score_field or '—' in score_field) and any(char.isdigit() for char in score_field):
        site_breakdown = f"**Site Scores:** {score_field}\n\n---\n\n"
        return site_breakdown + str(base_summary)
    
    return base_summary

def merge_multiple_reviews(account_df, account_name):
    """Merge multiple reviews for accounts with multiple entries (e.g., Gilead, Nike)"""
    if len(account_df) <= 1:
        return None  # No merging needed
    
    # Sort by completion date (most recent first)
    account_df = account_df.sort_values('Completion_Date', ascending=False)
    
    # Get all entries
    entries = []
    scores = []
    for idx, row in account_df.iterrows():
        original_name = row.get('Name of Account/Portfolio', account_name)
        score = row.get('Score')
        if pd.notna(score):
            scores.append(float(score))
        
        summary = row.get('Summary of Review\nWhat did you cover during the review? Please provide a brief summary of what was covered.\n\n', 'N/A')
        feedback = row.get('Customer Feedback\n\nWhat was the feedback from the client -- include any concerns and compliments shared and who shared it.\n', 'N/A')
        action_items = row.get('Action Items/Follow Ups\n\nWhat action items/follow ups came out of the meeting? Who owns them and agreed upon timelines?\n', 'N/A')
        date = row.get('Review_Date', 'N/A')
        
        entries.append({
            'name': original_name,
            'score': score,
            'date': date,
            'summary': summary,
            'feedback': feedback,
            'action_items': action_items
        })
    
    # Build merged summary
    merged_summary = f"**{len(entries)} Reviews Combined:**\n\n"
    for i, entry in enumerate(entries, 1):
        score_str = f"Score: {entry['score']}" if pd.notna(entry['score']) else "Score: N/A"
        merged_summary += f"**{i}. {entry['name']}** ({entry['date']}) - {score_str}\n\n{entry['summary']}\n\n---\n\n"
    
    # Build merged feedback
    merged_feedback = f"**Feedback from {len(entries)} Reviews:**\n\n"
    for i, entry in enumerate(entries, 1):
        merged_feedback += f"**{entry['name']}:**\n{entry['feedback']}\n\n---\n\n"
    
    # Build merged action items
    merged_action_items = f"**Action Items from {len(entries)} Reviews:**\n\n"
    for i, entry in enumerate(entries, 1):
        merged_action_items += f"**{entry['name']}:**\n{entry['action_items']}\n\n---\n\n"
    
    # Calculate average score
    avg_score = sum(scores) / len(scores) if scores else None
    
    # Get latest date
    latest_date = account_df['Review_Date'].max()
    latest_completion = account_df['Completion_Date'].max()
    
    return {
        'summary': merged_summary.strip(),
        'feedback': merged_feedback.strip(),
        'action_items': merged_action_items.strip(),
        'score': avg_score,
        'date': latest_date,
        'completion_date': latest_completion
    }

def get_all_accounts_with_data(processed_df):
    """Get dictionary of all accounts with their data"""
    accounts_data = {}
    
    # Accounts that should merge multiple reviews
    merge_accounts = ["Gilead Sciences", "Nike", "General Motors"]
    
    for account, vertical in account_to_vertical.items():
        if len(processed_df) == 0:
            # No data available, mark all accounts as having no data
            accounts_data[account] = {
                'vertical': vertical,
                'has_data': False,
                'score': None,
                'date': None,
                'completion_date': None,
                'response_count': 0
            }
            continue
            
        account_df = processed_df[processed_df['Account_Normalized'] == account]
        
        if len(account_df) > 0:
            # Check if this account should merge multiple reviews
            if account in merge_accounts and len(account_df) > 1:
                merged = merge_multiple_reviews(account_df, account)
                if merged:
                    accounts_data[account] = {
                        'vertical': vertical,
                        'has_data': True,
                        'score': merged['score'],
                        'date': merged['date'],
                        'completion_date': merged['completion_date'],
                        'response_count': len(account_df),
                        'account_director': account_df.iloc[0].get('Please Enter Your Name', 'N/A'),
                        'summary': merged['summary'],
                        'feedback': merged['feedback'],
                        'action_items': merged['action_items'],
                        'attendees': account_df.iloc[0].get('Who attended your Scorecard Review?\nNames and titles of all external and internal attendees.', 'N/A')
                    }
                    continue
            
            # Standard processing for single review or accounts not in merge list
            latest_idx = account_df['Completion_Date'].idxmax()
            latest = account_df.loc[latest_idx]
            
            accounts_data[account] = {
                'vertical': vertical,
                'has_data': True,
                'score': latest['Score'],
                'date': latest['Review_Date'],
                'completion_date': latest['Completion_Date'],
                'response_count': len(account_df),
                'account_director': latest.get('Please Enter Your Name', 'N/A'),
                'summary': build_summary_with_sites(account, latest, account_df),
                'feedback': latest.get('Customer Feedback\n\nWhat was the feedback from the client -- include any concerns and compliments shared and who shared it.\n', 'N/A'),
                'action_items': latest.get('Action Items/Follow Ups\n\nWhat action items/follow ups came out of the meeting? Who owns them and agreed upon timelines?\n', 'N/A'),
                'attendees': latest.get('Who attended your Scorecard Review?\nNames and titles of all external and internal attendees.', 'N/A')
            }
        else:
            accounts_data[account] = {
                'vertical': vertical,
                'has_data': False,
                'score': None,
                'date': None,
                'completion_date': None,
                'response_count': 0
            }
    
    return accounts_data

def get_vertical_color(vertical):
    """Get color for vertical badge"""
    colors = {
        'Aviation': '#FF6B6B',
        'Automotive': '#4ECDC4',
        'Manufacturing': '#45B7D1',
        'Technology': '#96CEB4',
        'Life Science': '#FFEAA7',
        'Finance': '#DFE6E9',
        'Distribution': '#A29BFE',
        'R&D / Education / Other': '#FD79A8'
    }
    return colors.get(vertical, '#B2BEC3')

def render_account_card(account, data):
    """Render a single account card with clickable button"""
    vertical_color = get_vertical_color(data['vertical'])
    
    if data['has_data']:
        score = data['score']
        if score is not None:
            if score >= 4.5:
                score_class = "score-high"
            elif score >= 3.5:
                score_class = "score-medium"
            else:
                score_class = "score-low"
            score_display = f'<span class="{score_class}">{score:.2f}</span>'
        else:
            score_display = '<span style="color: #999;">N/A</span>'
        
        date_display = data['date'].strftime('%m/%d/%Y') if pd.notna(data['date']) else 'N/A'
        
        st.markdown(f"""
        <div class="account-card">
            <h3 style="margin: 0 0 10px 0; color: #1a1a1a;">{account}</h3>
            <div class="vertical-badge" style="background-color: {vertical_color};">{data['vertical']}</div>
            <div style="margin-top: 15px;">
                <div style="font-size: 14px; color: #666;">Latest Score</div>
                <div>{score_display}</div>
            </div>
            <div style="margin-top: 10px; font-size: 14px; color: #666;">
                Review Date: {date_display}
            </div>
            <div style="margin-top: 5px; font-size: 14px; color: #666;">
                Total Responses: {data['response_count']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add "View Details" button
        if st.button("📄 View Details", key=f"btn_{account}", use_container_width=True):
            st.session_state['selected_account'] = account
            st.session_state['switch_to_data_tab'] = True
            st.rerun()
    else:
        st.markdown(f"""
        <div class="account-card-no-data">
            <h3 style="margin: 0 0 10px 0; color: #1a1a1a;">{account}</h3>
            <div class="vertical-badge" style="background-color: {vertical_color};">{data['vertical']}</div>
            <div style="margin-top: 15px; font-size: 16px; font-style: italic;">
                📋 Data Not Collected Yet
            </div>
        </div>
        """, unsafe_allow_html=True)

# Main app
def main():
    st.title("📊 Top 55 Accounts Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.markdown("### 🧭 Quick Navigation")
    
    if st.sidebar.button("→ Account Cards", key="sidebar_nav_cards", use_container_width=True):
        st.session_state['current_view'] = 'cards'
        st.session_state['selected_account'] = None
        # Reset filters when going back to Account Cards
        st.session_state.just_cleared_filters = True
        st.rerun()
    
    if st.sidebar.button("→ Data Table", key="sidebar_nav_data", use_container_width=True):
        st.session_state['current_view'] = 'data'
        st.rerun()
    
    if st.sidebar.button("→ No Data List", key="sidebar_nav_nodata", use_container_width=True):
        st.session_state['current_view'] = 'no_data'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Month selector
    st.sidebar.header("📅 Select Month")
    
    # Get available months
    available_months = get_available_months()
    
    # Always include December 2025 for blank state
    if "December_2025" not in available_months:
        available_months.append("December_2025")
        available_months = sorted(available_months, reverse=True)
    
    # Format for display
    month_display = {m: m.replace("_", " ").title() for m in available_months}
    month_options = list(month_display.values())
    
    # Initialize selected month in session state
    if 'selected_month' not in st.session_state:
        st.session_state['selected_month'] = month_options[0] if month_options else "November 2025"
    
    # Month selector
    selected_month_display = st.sidebar.selectbox(
        "Choose Month",
        month_options,
        index=0,
        key='month_select'
    )
    
    # Convert back to file format
    selected_month_key = [k for k, v in month_display.items() if v == selected_month_display][0]
    
    # Store in session state for use in main processing
    st.session_state['selected_month_key'] = selected_month_key
    st.session_state['selected_month_display'] = selected_month_display
    
    st.sidebar.markdown("---")
    
    # Load and process data for selected month
    raw_df = load_data(month=selected_month_key)
    
    # Handle blank state (no data for selected month)
    if raw_df is None:
        # Create empty dataframe to show blank state
        processed_df = pd.DataFrame()
        # Set flag to show message in main area
        st.session_state['show_blank_state_message'] = True
        st.session_state['blank_state_month'] = selected_month_display
    else:
        processed_df = process_data(raw_df)
        st.session_state['show_blank_state_message'] = False
    
    # Get all accounts data
    all_accounts = get_all_accounts_with_data(processed_df)
    
    # Check if IFM column exists in raw data
    has_ifm_column = False
    ifm_column_name = None
    if raw_df is not None:
        # Look for IFM-related column names (case-insensitive)
        for col in raw_df.columns:
            if 'ifm' in str(col).lower() or 'directly contracted' in str(col).lower() or 'third party' in str(col).lower():
                has_ifm_column = True
                ifm_column_name = col
                break
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Get unique verticals
    all_verticals = sorted(list(set(account_to_vertical.values())))
    vertical_options = ['All'] + all_verticals
    
    selected_vertical = st.sidebar.selectbox(
        "Select Vertical",
        vertical_options,
        index=0,  # Always default to 'All'
        key='vertical_select'
    )
    
    # Filter accounts by vertical
    if selected_vertical == 'All':
        filtered_accounts = all_accounts
    else:
        filtered_accounts = {k: v for k, v in all_accounts.items() if v['vertical'] == selected_vertical}
    
    # Account filter (dynamically based on vertical)
    account_options = ['All'] + sorted(list(filtered_accounts.keys()))
    selected_account = st.sidebar.selectbox(
        "Select Account",
        account_options,
        index=0,  # Always default to 'All'
        key='account_select'
    )
    
    # Further filter by account if selected
    if selected_account != 'All':
        filtered_accounts = {selected_account: all_accounts[selected_account]}
    
    # Score range filter
    st.sidebar.markdown("---")  # Separator line
    st.sidebar.subheader("📈 Filter by Score")
    
    # Get all available scores for slider range
    all_scores = [v['score'] for v in all_accounts.values() if v['has_data'] and v['score'] is not None]
    
    if all_scores:
        # Score category filter (radio - pick one)
        score_options = ["📊 All Scores", "🟢 4.5+", "🟡 3.5-4.5", "🔴 <3.5", "⚪ No Score"]
        score_filter = st.sidebar.radio(
            "Show Accounts:",
            options=score_options,
            index=0,  # Always default to 'All Scores'
            horizontal=False,
            key='score_radio'
        )
        
        # Helper function to check if score matches selected category
        def score_in_category(score):
            if score_filter == "📊 All Scores":
                return True  # Show all scores
            elif score_filter == "⚪ No Score":
                return score is None
            elif score_filter == "🟢 4.5+":
                return score is not None and score >= 4.5
            elif score_filter == "🟡 3.5-4.5":
                return score is not None and 3.5 <= score < 4.5
            elif score_filter == "🔴 <3.5":
                return score is not None and score < 3.5
            return True
        
        # Apply score filter
        filtered_accounts = {
            k: v for k, v in filtered_accounts.items() 
            if v['has_data'] and score_in_category(v.get('score'))
        }
    else:
        st.sidebar.info("No score data available")
    
    # IFM filter (if column exists)
    if has_ifm_column and raw_df is not None:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🏢 Filter by Contract Type")
        
        # Get unique IFM values
        ifm_values = raw_df[ifm_column_name].dropna().unique().tolist()
        ifm_options = ['All'] + sorted([str(v) for v in ifm_values if str(v).strip()])
        
        selected_ifm = st.sidebar.selectbox(
            "Contract Type",
            ifm_options,
            index=0,
            key='ifm_filter'
        )
        
        # Apply IFM filter (will be applied later when processing account data)
        st.session_state['selected_ifm'] = selected_ifm
        st.session_state['ifm_column_name'] = ifm_column_name
    else:
        st.session_state['selected_ifm'] = 'All'
        st.session_state['ifm_column_name'] = None
    
    # Calculate metrics
    accounts_with_data = {k: v for k, v in filtered_accounts.items() if v['has_data']}
    # For "no data" view, always use all_accounts to show true missing data
    accounts_without_data = {k: v for k, v in all_accounts.items() if not v['has_data']}
    
    total_accounts = len(filtered_accounts)
    total_responses = sum(v['response_count'] for v in accounts_with_data.values())
    
    scores = [v['score'] for v in accounts_with_data.values() if v['score'] is not None and pd.notna(v['score'])]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Get latest date
    dates = [v['completion_date'] for v in accounts_with_data.values() if pd.notna(v.get('completion_date'))]
    latest_date = max(dates).strftime('%m/%d/%Y') if dates else 'N/A'
    
    # Show blank state message if needed
    if st.session_state.get('show_blank_state_message', False):
        st.info(f"📋 **No data available for {st.session_state.get('blank_state_month', 'selected month')}.** All accounts will show as 'Data Not Collected Yet'.")
        st.markdown("---")
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Accounts", total_accounts)
    
    with col2:
        st.metric("Accounts with Data", len(accounts_with_data))
    
    with col3:
        st.metric("Average Score", f"{avg_score:.2f}" if avg_score > 0 else "N/A")
    
    with col4:
        st.metric("Total Responses", total_responses)
    
    # Initialize navigation state
    if 'current_view' not in st.session_state:
        st.session_state['current_view'] = 'cards'
    
    # Check if we should switch to data table view
    if st.session_state.get('switch_to_data_tab'):
        st.session_state['current_view'] = 'data'
        st.session_state['switch_to_data_tab'] = False
    
    # Navigation buttons with sticky positioning
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📇 Account Cards", use_container_width=True, type="primary" if st.session_state['current_view'] == 'cards' else "secondary", key="nav_cards"):
            st.session_state['current_view'] = 'cards'
            st.session_state['selected_account'] = None
            # Reset filters when going back to Account Cards
            st.session_state.just_cleared_filters = True
            st.rerun()
    with col2:
        if st.button("📋 Data Table", use_container_width=True, type="primary" if st.session_state['current_view'] == 'data' else "secondary", key="nav_data"):
            st.session_state['current_view'] = 'data'
            st.rerun()
    with col3:
        if st.button("🚫 Accounts Without Data", use_container_width=True, type="primary" if st.session_state['current_view'] == 'no_data' else "secondary", key="nav_nodata"):
            st.session_state['current_view'] = 'no_data'
            st.session_state['selected_account'] = None
            st.rerun()
    
    st.markdown("---")
    
    # Show content based on current view
    if st.session_state['current_view'] == 'cards':
        st.subheader("Account Overview")
        
        if len(accounts_with_data) == 0:
            st.info("No accounts with data for the selected filters.")
        else:
            # Display account cards in 3 columns
            cols_per_row = 3
            accounts_list = list(accounts_with_data.items())
            
            for i in range(0, len(accounts_list), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(accounts_list):
                        account, data = accounts_list[i + j]
                        with col:
                            render_account_card(account, data)
    
    elif st.session_state['current_view'] == 'data':
        st.subheader("Detailed Data Table")
        
        # Check if we should show a message about selected account
        selected_account = st.session_state.get('selected_account', None)
        if selected_account and selected_account in accounts_with_data:
            st.info(f"📍 Showing details for: **{selected_account}**")
        elif selected_account and selected_account not in accounts_with_data:
            # Account was selected but is now filtered out - clear it
            st.session_state['selected_account'] = None
        
        if len(accounts_with_data) == 0:
            st.info("No data available.")
        else:
            # Prepare table data
            table_data = []
            for account, data in accounts_with_data.items():
                table_data.append({
                    'Account': account,
                    'Vertical': data['vertical'],
                    'Score': f"{data['score']:.2f}" if data['score'] is not None else 'N/A',
                    'Review Date': data['date'].strftime('%m/%d/%Y') if pd.notna(data['date']) else 'N/A',
                    'Account Director': data.get('account_director', 'N/A')
                })
            
            table_df = pd.DataFrame(table_data)
            st.dataframe(table_df, use_container_width=True, hide_index=True)
            
            # Expandable detailed view
            st.markdown("### Detailed Information")
            
            # Get selected account from session state
            selected_account = st.session_state.get('selected_account', None)
            
            for account, data in sorted(accounts_with_data.items()):
                # Auto-expand if this is the selected account
                is_expanded = (account == selected_account)
                
                with st.expander(f"📄 {account} - {data['vertical']}", expanded=is_expanded):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Score:** {data['score']:.2f}" if data['score'] else "**Score:** N/A")
                        st.markdown(f"**Review Date:** {data['date'].strftime('%m/%d/%Y') if pd.notna(data['date']) else 'N/A'}")
                        st.markdown(f"**Responses:** {data['response_count']}")
                    with col2:
                        st.markdown(f"**Account Director:** {data.get('account_director', 'N/A')}")
                    
                    st.markdown("**Summary:**")
                    st.write(data.get('summary', 'N/A'))
                    
                    st.markdown("**Customer Feedback:**")
                    st.write(data.get('feedback', 'N/A'))
                    
                    st.markdown("**Action Items:**")
                    st.write(data.get('action_items', 'N/A'))
            
            # Clear selected account after rendering
            if selected_account:
                # Add a button to clear the selection
                if st.button("🔄 Clear Selection"):
                    st.session_state['selected_account'] = None
                    st.rerun()
    
    elif st.session_state['current_view'] == 'no_data':
        st.subheader("Accounts Without Data")
        
        if len(accounts_without_data) == 0:
            st.success("All accounts have data!")
        else:
            st.info(f"**{len(accounts_without_data)}** accounts are awaiting data collection.")
            
            # Group by vertical
            by_vertical = {}
            for account, data in accounts_without_data.items():
                vertical = data['vertical']
                if vertical not in by_vertical:
                    by_vertical[vertical] = []
                by_vertical[vertical].append(account)
            
            # Display by vertical
            for vertical in sorted(by_vertical.keys()):
                with st.expander(f"**{vertical}** ({len(by_vertical[vertical])} accounts)"):
                    for account in sorted(by_vertical[vertical]):
                        st.markdown(f"- {account}")

if __name__ == "__main__":
    main()

