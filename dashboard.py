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
    page_title="SBM Scorecard Review",
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
    
    # Also check for legacy files (current format)
    legacy_files = list(scorecards_dir.glob("Scorecard Review Executive Summary*.csv"))
    if legacy_files:
        # Check for file (10) - December 2025
        file_10 = scorecards_dir / "Scorecard Review Executive Summary(Sheet1) (10).csv"
        if file_10.exists() and "December_2025" not in months:
            months.append("December_2025")
        # Check for file (8) - November 2025
        file_8 = scorecards_dir / "Scorecard Review Executive Summary(Sheet1) (8).csv"
        if file_8.exists() and "November_2025" not in months:
            months.append("November_2025")
        # Fallback: if no specific files found, add November 2025
        elif "November_2025" not in months and "December_2025" not in months:
            months.append("November_2025")
    
    return sorted(months, reverse=True)  # Most recent first

@st.cache_data(ttl=60)  # Cache for 60 seconds only
def load_data(month=None):
    """Load and process the CSV data with caching"""
    scorecards_dir = Path("Scorecards")
    
    if month:
        # Load specific month file
        if month == "December_2025":
            # Check for file (10) first, then new format
            legacy_path_10 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (10).csv")
            if legacy_path_10.exists():
                csv_path = legacy_path_10
            else:
                csv_path = scorecards_dir / f"{month}_Scorecards.csv"
        elif month == "November_2025":
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
                if month_key == "December_2025":
                    # Check for file (10) first, then new format
                    legacy_path_10 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (10).csv")
                    if legacy_path_10.exists():
                        csv_path = legacy_path_10
                    else:
                        csv_path = scorecards_dir / f"{month_key}_Scorecards.csv"
                elif month_key == "November_2025":
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
                # Fallback to current file format - try file (10) first, then (8), then (5)
                legacy_path_10 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (10).csv")
                legacy_path_8 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (8).csv")
                legacy_path_5 = Path("Scorecards/Scorecard Review Executive Summary(Sheet1) (5).csv")
                if legacy_path_10.exists():
                    csv_path = legacy_path_10
                elif legacy_path_8.exists():
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
def process_data(df, month=None):
    """Process and enrich data with verticals - handles both original and new column sets"""
    if df is None or len(df) == 0:
        return pd.DataFrame()  # Return empty dataframe instead of None
    
    # For December 2025, filter to only entries with Id >= 62
    if month == "December_2025" and 'Id' in df.columns:
        df = df[df['Id'] >= 62].copy()
        if len(df) == 0:
            return pd.DataFrame()
    
    # Detect which column set to use for each row
    # Check if original account column (index 7) is empty, if so use new columns (index 16+)
    original_account_col = 'Name of Account/Portfolio'
    new_account_col = 'Name of Account/Portfolio1'
    
    # Determine which column set to use for each row
    # For December 2025, always use new columns (Id >= 62 entries)
    # For other months, detect based on which column has data
    is_december = (month == "December_2025")
    
    def get_account_name(row):
        # For December, always use new column
        if is_december:
            return row.get(new_account_col)
        # For other months, check which column has data
        if pd.notna(row.get(new_account_col)) and str(row.get(new_account_col)).strip():
            return row.get(new_account_col)
        # Otherwise use original column
        return row.get(original_account_col)
    
    def get_column_value(row, original_col, new_col):
        """Get value from appropriate column set"""
        # For December, always use new column set
        if is_december:
            if new_col in df.columns:
                return row.get(new_col)
            return None
        # For other months, detect based on which column has data
        new_account_val = row.get(new_account_col)
        if pd.notna(new_account_val) and str(new_account_val).strip():
            # Use new column set
            if new_col in df.columns:
                return row.get(new_col)
        # Use original column set
        if original_col in df.columns:
            return row.get(original_col)
        return None
    
    # Create unified columns
    df['Account_Name'] = df.apply(get_account_name, axis=1)
    
    # Normalize account names
    df['Account_Normalized'] = df['Account_Name'].apply(normalize_account_name)
    
    # Filter out None values (omitted accounts)
    df = df[df['Account_Normalized'].notna()].copy()
    
    # Extract IFM field from "Who is Your FM" column (index 15) - do this before creating composite key
    if 'Who is Your FM' in df.columns:
        df['IFM'] = df['Who is Your FM'].fillna('')
        df['IFM'] = df['IFM'].apply(lambda x: str(x).strip() if pd.notna(x) else '')
    else:
        df['IFM'] = ''
    
    # Create composite account identifier that includes IFM for December entries
    # This allows separate scorecards for same account with different IFM types (e.g., Merck Sodexo vs Merck Direct)
    def create_account_identifier(row):
        base_account = row['Account_Normalized']
        ifm = row.get('IFM', '')
        
        # For December entries or when IFM is present, append IFM to create unique identifier
        if is_december and ifm and ifm != '':
            # Clean up IFM value for display
            ifm_clean = ifm.replace('(None)', '').strip()
            if ifm_clean:
                return f"{base_account} ({ifm_clean})"
        
        return base_account
    
    df['Account_Identifier'] = df.apply(create_account_identifier, axis=1)
    
    # Add vertical based on normalized account name (not the composite identifier)
    # This ensures vertical assignment is based on the base account name
    df['Vertical'] = df['Account_Normalized'].map(account_to_vertical)
    df['Vertical'] = df['Vertical'].fillna('Other')  # Assign "Other" to unmapped accounts
    
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
    
    # Get score from appropriate column
    original_score_col = 'What was the overall Scorecard Score?'
    new_score_col = 'What was the overall Scorecard Score?1'
    df['Score_Raw'] = df.apply(lambda row: get_column_value(row, original_score_col, new_score_col), axis=1)
    df['Score'] = df['Score_Raw'].apply(parse_score)
    
    # Get date from appropriate column
    original_date_col = 'Date/Time of Scorecard Review?'
    new_date_col = 'Date/Time of Scorecard Review?1'
    df['Review_Date'] = pd.to_datetime(
        df.apply(lambda row: get_column_value(row, original_date_col, new_date_col), axis=1),
        errors='coerce'
    )
    df['Completion_Date'] = pd.to_datetime(df['Completion time'], errors='coerce')
    
    # Store all CSV fields for detail view - create unified columns for display
    def get_unified_column(row, original_col, new_col, default=''):
        """Get value from appropriate column set with fallback"""
        val = get_column_value(row, original_col, new_col)
        if pd.isna(val) or str(val).strip() == '':
            return default
        return str(val).strip()
    
    # Map original column names to new column names
    column_mapping = {
        'Name of Account/Portfolio': 'Name of Account/Portfolio1',
        'Date/Time of Scorecard Review?': 'Date/Time of Scorecard Review?1',
        'Who attended your Scorecard Review?\nNames and titles of all external and internal attendees.': 'Who attended your Scorecard Review?\nNames and titles of all external and internal attendees.1',
        'What was the overall Scorecard Score?': 'What was the overall Scorecard Score?1',
        'Summary of Review\nWhat did you cover during the review? Please provide a brief summary of what was covered.\n\n': 'Summary of Review\nWhat did you cover during the review? Please provide a brief summary of what was covered.\n\n1',
        'Customer Feedback\n\nWhat was the feedback from the client -- include any concerns and compliments shared and who shared it.\n': 'Customer Feedback\n\nWhat was the feedback from the client -- include any concerns and compliments shared and who shared it.\n1',
        'Action Items/Follow Ups\n\nWhat action items/follow ups came out of the meeting? Who owns them and agreed upon timelines?\n': 'Action Items/Follow Ups\n\nWhat action items/follow ups came out of the meeting? Who owns them and agreed upon timelines?\n1',
        'Date of Next Scorecard Review': 'Date of Next Scorecard Review1'
    }
    
    # Create unified columns for all fields
    for orig_col, new_col in column_mapping.items():
        unified_name = orig_col.replace('\n', ' ').replace('?', '').replace(':', '').strip()
        if unified_name.startswith('Summary'):
            unified_name = 'Summary'
        elif unified_name.startswith('Customer Feedback'):
            unified_name = 'Customer Feedback'
        elif unified_name.startswith('Action Items'):
            unified_name = 'Action Items'
        elif unified_name.startswith('Who attended'):
            unified_name = 'Attendees'
        elif unified_name.startswith('Date of Next'):
            unified_name = 'Next Review Date'
        elif unified_name.startswith('Date/Time'):
            unified_name = 'Review Date'
        elif unified_name.startswith('What was the overall'):
            unified_name = 'Score_Raw'  # Use Score_Raw to avoid conflict with parsed Score column
        
        # Only create unified column if it doesn't already exist or if it's a different column
        if unified_name not in df.columns or unified_name == 'Score_Raw':
            df[unified_name] = df.apply(
                lambda row: get_unified_column(row, orig_col, new_col),
                axis=1
            )
    
    # Also store raw CSV row data for detail view
    df['_raw_row_data'] = df.apply(lambda row: row.to_dict(), axis=1)
    
    return df

def build_summary_with_sites(account, latest_row, account_df):
    """Build summary with site-specific scores if multiple locations"""
    base_summary = latest_row.get('Summary', 'N/A')
    
    # Check if score field contains multiple sites (like Cigna)
    score_field = str(latest_row.get('Score_Raw', ''))
    
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
        original_name = row.get('Account_Name', account_name)
        score = row.get('Score')
        if pd.notna(score):
            scores.append(float(score))
        
        summary = row.get('Summary', 'N/A')
        feedback = row.get('Customer Feedback', 'N/A')
        action_items = row.get('Action Items', 'N/A')
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
        
        # Check if we have composite identifiers (December entries with IFM)
        # If so, get all entries for this base account (including all IFM variations)
        if 'Account_Identifier' in processed_df.columns:
            # Get all entries where the base account matches (could be multiple IFM variations)
            account_df = processed_df[processed_df['Account_Normalized'] == account]
            
            if len(account_df) > 0:
                # Group by Account_Identifier to create separate entries per IFM type
                for account_id in account_df['Account_Identifier'].unique():
                    id_df = account_df[account_df['Account_Identifier'] == account_id]
                    
                    # Use the composite identifier as the key
                    display_account = account_id if account_id != account else account
                    
                    # Check if this account should merge multiple reviews
                    if account in merge_accounts and len(id_df) > 1:
                        merged = merge_multiple_reviews(id_df, display_account)
                        if merged:
                            accounts_data[display_account] = {
                                'vertical': vertical,
                                'has_data': True,
                                'score': merged['score'],
                                'date': merged['date'],
                                'completion_date': merged['completion_date'],
                                'response_count': len(id_df),
                                'account_director': id_df.iloc[0].get('Please Enter Your Name', 'N/A'),
                                'summary': merged['summary'],
                                'feedback': merged['feedback'],
                                'action_items': merged['action_items'],
                                'attendees': id_df.iloc[0].get('Attendees', 'N/A'),
                                'ifm': id_df.iloc[0].get('IFM', ''),
                                'raw_data': id_df.iloc[0].get('_raw_row_data', {})
                            }
                            continue
                    
                    # Standard processing for single review or accounts not in merge list
                    latest_idx = id_df['Completion_Date'].idxmax()
                    latest = id_df.loc[latest_idx]
                    
                    accounts_data[display_account] = {
                        'vertical': vertical,
                        'has_data': True,
                        'score': latest['Score'],
                        'date': latest['Review_Date'],
                        'completion_date': latest['Completion_Date'],
                        'response_count': len(id_df),
                        'account_director': latest.get('Please Enter Your Name', 'N/A'),
                        'summary': build_summary_with_sites(display_account, latest, id_df),
                        'feedback': latest.get('Customer Feedback', 'N/A'),
                        'action_items': latest.get('Action Items', 'N/A'),
                        'attendees': latest.get('Attendees', 'N/A'),
                        'ifm': latest.get('IFM', ''),
                        'raw_data': latest.get('_raw_row_data', {})
                    }
            else:
                # No data for this account
                accounts_data[account] = {
                    'vertical': vertical,
                    'has_data': False,
                    'score': None,
                    'date': None,
                    'completion_date': None,
                    'response_count': 0
                }
        else:
            # Original logic for non-December entries
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
                            'attendees': account_df.iloc[0].get('Attendees', 'N/A'),
                            'ifm': account_df.iloc[0].get('IFM', ''),
                            'raw_data': account_df.iloc[0].get('_raw_row_data', {})
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
                    'feedback': latest.get('Customer Feedback', 'N/A'),
                    'action_items': latest.get('Action Items', 'N/A'),
                    'attendees': latest.get('Attendees', 'N/A'),
                    'ifm': latest.get('IFM', ''),
                    'raw_data': latest.get('_raw_row_data', {})
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
    
    # Also include accounts outside Top 55 (Other vertical)
    # Use Account_Identifier to get separate entries per IFM for December
    if len(processed_df) > 0:
        other_accounts_df = processed_df[processed_df['Vertical'] == 'Other']
        if len(other_accounts_df) > 0:
            # Group by Account_Identifier to maintain separate entries for different IFM types
            identifier_col = 'Account_Identifier' if 'Account_Identifier' in other_accounts_df.columns else 'Account_Normalized'
            for account_identifier in other_accounts_df[identifier_col].unique():
                account_df = other_accounts_df[other_accounts_df[identifier_col] == account_identifier]
                latest_idx = account_df['Completion_Date'].idxmax()
                latest = account_df.loc[latest_idx]
                
                accounts_data[account_identifier] = {
                    'vertical': 'Other',
                    'has_data': True,
                    'score': latest['Score'],
                    'date': latest['Review_Date'],
                    'completion_date': latest['Completion_Date'],
                    'response_count': len(account_df),
                    'account_director': latest.get('Please Enter Your Name', 'N/A'),
                    'summary': latest.get('Summary', 'N/A'),
                    'feedback': latest.get('Customer Feedback', 'N/A'),
                    'action_items': latest.get('Action Items', 'N/A'),
                    'attendees': latest.get('Attendees', 'N/A'),
                    'ifm': latest.get('IFM', ''),
                    'raw_data': latest.get('_raw_row_data', {})
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
        'R&D / Education / Other': '#FD79A8',
        'Other': '#95A5A6'
    }
    return colors.get(vertical, '#B2BEC3')

def render_december_detail_view(account, data):
    """Render detailed view for December account"""
    vertical_color = get_vertical_color(data['vertical'])
    
    # Back button
    if st.button("← Back to Account Cards", key="back_to_cards"):
        st.session_state['selected_account'] = None
        st.rerun()
    
    st.markdown("---")
    
    # Account header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"## {account}")
    with col2:
        st.markdown(f'<div class="vertical-badge" style="background-color: {vertical_color}; text-align: center; padding: 10px;">{data["vertical"]}</div>', unsafe_allow_html=True)
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        score = data['score']
        if score is not None:
            st.metric("Score", f"{score:.2f}")
        else:
            st.metric("Score", "N/A")
    
    with col2:
        date_display = data['date'].strftime('%m/%d/%Y') if pd.notna(data['date']) else 'N/A'
        st.metric("Review Date", date_display)
    
    with col3:
        st.metric("Responses", data['response_count'])
    
    with col4:
        ifm = data.get('ifm', '')
        ifm_display = ifm if ifm else 'N/A'
        st.metric("IFM", ifm_display)
    
    st.markdown("---")
    
    # Detailed sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Account Director")
        st.write(data.get('account_director', 'N/A'))
        
        st.markdown("### Attendees")
        st.write(data.get('attendees', 'N/A'))
    
    with col2:
        st.markdown("### Completion Date")
        completion_date = data.get('completion_date')
        if pd.notna(completion_date):
            st.write(completion_date.strftime('%m/%d/%Y %I:%M %p'))
        else:
            st.write('N/A')
        
        st.markdown("### Next Review Date")
        raw_data = data.get('raw_data', {})
        next_review = raw_data.get('Date of Next Scorecard Review1', '')
        if not next_review or str(next_review).strip() == '':
            next_review = raw_data.get('Date of Next Scorecard Review', 'N/A')
        st.write(next_review if next_review else 'N/A')
    
    st.markdown("---")
    
    # Summary
    st.markdown("### Summary")
    st.write(data.get('summary', 'N/A'))
    
    st.markdown("---")
    
    # Customer Feedback
    st.markdown("### Customer Feedback")
    st.write(data.get('feedback', 'N/A'))
    
    st.markdown("---")
    
    # Action Items
    st.markdown("### Action Items")
    st.write(data.get('action_items', 'N/A'))

def render_account_card(account, data, month=None):
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
        
        # For December, make the entire card clickable
        if month == "December_2025":
            # For December, display card with clickable button below it
            st.markdown(f"""
            <div class="account-card" style="cursor: pointer;">
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
            
            # Visible button below the card
            button_key = f"card_btn_{account.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('.', '_')}"
            if st.button(f"View Details", key=button_key, use_container_width=True, help=f"Click to view details for {account}"):
                st.session_state['selected_account'] = account
                st.rerun()
        else:
            # Original card rendering for non-December
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
            if st.button("View Details", key=f"btn_{account}", use_container_width=True):
                st.session_state['selected_account'] = account
                st.session_state['switch_to_data_tab'] = True
                st.rerun()
    else:
        st.markdown(f"""
        <div class="account-card-no-data">
            <h3 style="margin: 0 0 10px 0; color: #1a1a1a;">{account}</h3>
            <div class="vertical-badge" style="background-color: {vertical_color};">{data['vertical']}</div>
            <div style="margin-top: 15px; font-size: 16px; font-style: italic;">
                Data Not Collected Yet
            </div>
        </div>
        """, unsafe_allow_html=True)

# Main app
def main():
    st.title("SBM Scorecard Review")
    st.markdown("---")
    
    # Get available months and set default to December 2025
    available_months = get_available_months()
    
    # Always include December 2025 for blank state
    if "December_2025" not in available_months:
        available_months.append("December_2025")
        available_months = sorted(available_months, reverse=True)
    
    # Format for display
    month_display = {m: m.replace("_", " ").title() for m in available_months}
    month_options = list(month_display.values())
    
    # Initialize selected month in session state - default to December 2025
    if 'selected_month' not in st.session_state:
        # Try to find December 2025, otherwise use first available
        if "December 2025" in month_options:
            st.session_state['selected_month'] = "December 2025"
        else:
            st.session_state['selected_month'] = month_options[0] if month_options else "November 2025"
    
    # Get the selected month key (use session state or default to December)
    if 'selected_month_key' not in st.session_state:
        if "December 2025" in month_options:
            selected_month_display = "December 2025"
        else:
            selected_month_display = month_options[0] if month_options else "November 2025"
        selected_month_key = [k for k, v in month_display.items() if v == selected_month_display][0]
        st.session_state['selected_month_key'] = selected_month_key
        st.session_state['selected_month_display'] = selected_month_display
    else:
        selected_month_key = st.session_state['selected_month_key']
        selected_month_display = st.session_state['selected_month_display']
    
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
        processed_df = process_data(raw_df, month=selected_month_key)
        st.session_state['show_blank_state_message'] = False
    
    # Get all accounts data
    all_accounts = get_all_accounts_with_data(processed_df)
    
    # Check if IFM data exists in processed data
    has_ifm_data = False
    if len(processed_df) > 0:
        # Check if any row has non-empty IFM field
        ifm_values = processed_df['IFM'].fillna('').astype(str).str.strip()
        has_ifm_data = (ifm_values != '').any()
    
    # Initialize filter defaults
    if 'vertical_select' not in st.session_state:
        st.session_state['vertical_select'] = 'All'
    if 'account_select' not in st.session_state:
        st.session_state['account_select'] = 'All'
    if 'ifm_select' not in st.session_state:
        st.session_state['ifm_select'] = 'All'
    if 'score_radio' not in st.session_state:
        st.session_state['score_radio'] = "All Scores"
    
    # Get unique verticals
    all_verticals = sorted(list(set(account_to_vertical.values())))
    vertical_options = ['All'] + all_verticals
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Month selector
    current_month_display = st.session_state.get('selected_month_display', "December 2025")
    month_index = 0
    if current_month_display in month_options:
        month_index = month_options.index(current_month_display)
    elif "December 2025" in month_options:
        month_index = month_options.index("December 2025")
    
    selected_month_display = st.sidebar.selectbox(
        "Month",
        month_options,
        index=month_index,
        key='month_select_sidebar'
    )
    
    # Convert back to file format and update session state
    new_selected_month_key = [k for k, v in month_display.items() if v == selected_month_display][0]
    
    # Reload data if month changed
    if new_selected_month_key != selected_month_key:
        st.session_state['selected_month_key'] = new_selected_month_key
        st.session_state['selected_month_display'] = selected_month_display
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Vertical filter - use key to let Streamlit manage state
    if 'vertical_select_sidebar' not in st.session_state:
        st.session_state['vertical_select_sidebar'] = 'All'
    
    selected_vertical = st.sidebar.selectbox(
        "Vertical",
        vertical_options,
        index=vertical_options.index(st.session_state['vertical_select_sidebar']) if st.session_state['vertical_select_sidebar'] in vertical_options else 0,
        key='vertical_select_sidebar'
    )
    
    # IFM filter (only show if IFM data exists)
    # Filter IFM options based on selected vertical
    if has_ifm_data:
        ifm_values = set()
        
        # If a vertical is selected, only show IFM options for that vertical
        if selected_vertical != 'All':
            for account_name, account_data in all_accounts.items():
                # Check if account belongs to selected vertical
                if account_data.get('vertical') == selected_vertical:
                    ifm_val = account_data.get('ifm', '')
                    if ifm_val and str(ifm_val).strip():
                        ifm_values.add(str(ifm_val).strip())
        else:
            # If "All" verticals selected, show all IFM options
            for account_data in all_accounts.values():
                ifm_val = account_data.get('ifm', '')
                if ifm_val and str(ifm_val).strip():
                    ifm_values.add(str(ifm_val).strip())
        
        if ifm_values:
            ifm_options = ['All'] + sorted(list(ifm_values))
            
            # Initialize IFM select state if not exists
            if 'ifm_select_sidebar' not in st.session_state:
                st.session_state['ifm_select_sidebar'] = 'All'
            
            # If vertical changed, reset IFM to 'All' if current selection not available
            if st.session_state['ifm_select_sidebar'] not in ifm_options:
                st.session_state['ifm_select_sidebar'] = 'All'
            
            selected_ifm = st.sidebar.selectbox(
                "IFM",
                ifm_options,
                index=ifm_options.index(st.session_state['ifm_select_sidebar']),
                key='ifm_select_sidebar'
            )
        else:
            selected_ifm = 'All'
            # Reset state if no IFM options available
            st.session_state['ifm_select_sidebar'] = 'All'
    else:
        selected_ifm = 'All'
    
    # Score filter - get from session state (will be updated on main page)
    all_scores = [v['score'] for v in all_accounts.values() if v['has_data'] and v['score'] is not None]
    score_filter = st.session_state.get('score_radio', "All Scores")
    
    # Update legacy session state keys for backward compatibility
    st.session_state['vertical_select'] = selected_vertical
    st.session_state['ifm_select'] = selected_ifm
    
    # Start with all accounts - filters will be applied below
    filtered_accounts = all_accounts
    
    # Apply filters using the selectbox values directly
    if selected_vertical != 'All':
        filtered_accounts = {k: v for k, v in filtered_accounts.items() if v['vertical'] == selected_vertical}
    
    if has_ifm_data and selected_ifm != 'All':
        filtered_accounts = {
            k: v for k, v in filtered_accounts.items()
            if str(v.get('ifm', '')).strip() == selected_ifm
        }
    
    # Apply score filter early in the filter chain
    if all_scores:
        def score_in_category(score):
            if score_filter == "All Scores":
                return True
            elif score_filter == "No Score":
                return score is None
            elif score_filter == "4.5+":
                return score is not None and score >= 4.5
            elif score_filter == "3.5-4.5":
                return score is not None and 3.5 <= score < 4.5
            elif score_filter == "<3.5":
                return score is not None and score < 3.5
            return True
        
        filtered_accounts = {
            k: v for k, v in filtered_accounts.items() 
            if v['has_data'] and score_in_category(v.get('score'))
        }
    
    # Show blank state message if needed
    if st.session_state.get('show_blank_state_message', False):
        st.info(f"**No data available for {st.session_state.get('blank_state_month', 'selected month')}.** All accounts will show as 'Data Not Collected Yet'.")
        st.markdown("---")
    
    
    # Calculate metrics AFTER filters are applied
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
    
    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Accounts with Data", len(accounts_with_data))
    
    with col2:
        st.metric("Average Score", f"{avg_score:.2f}" if avg_score > 0 else "N/A")
    
    with col3:
        st.metric("Total Responses", total_responses)
    
    st.markdown("---")
    
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
        if st.button("Account Cards", use_container_width=True, type="primary" if st.session_state['current_view'] == 'cards' else "secondary", key="nav_cards"):
            st.session_state['current_view'] = 'cards'
            st.session_state['selected_account'] = None
            # Reset filters when going back to Account Cards
            st.session_state.just_cleared_filters = True
            st.rerun()
    with col2:
        if st.button("Data Table", use_container_width=True, type="primary" if st.session_state['current_view'] == 'data' else "secondary", key="nav_data"):
            st.session_state['current_view'] = 'data'
            st.rerun()
    with col3:
        if st.button("Accounts Without Data", use_container_width=True, type="primary" if st.session_state['current_view'] == 'no_data' else "secondary", key="nav_nodata"):
            st.session_state['current_view'] = 'no_data'
            st.session_state['selected_account'] = None
            st.rerun()
    
    st.markdown("---")
    
    # Show content based on current view
    if st.session_state['current_view'] == 'cards':
        # Check if December and account is selected
        is_december = (selected_month_key == "December_2025")
        selected_account = st.session_state.get('selected_account', None)
        
        if is_december and selected_account and selected_account in accounts_with_data:
            # Show detailed view for December
            render_december_detail_view(selected_account, accounts_with_data[selected_account])
        else:
            # Show account cards grid
            # Score filter near Account Overview
            col_title, col_score = st.columns([3, 1])
            with col_title:
                st.subheader("Account Overview")
            with col_score:
                if all_scores:
                    score_options = ["All Scores", "4.5+", "3.5-4.5", "<3.5", "No Score"]
                    current_score = st.session_state.get('score_radio', "All Scores")
                    score_index = 0 if current_score == "All Scores" else (score_options.index(current_score) if current_score in score_options else 0)
                    
                    new_score_filter = st.selectbox(
                        "Score",
                        score_options,
                        index=score_index,
                        key='score_select_main'
                    )
                    
                    # If score filter changed, update session state and rerun
                    if new_score_filter != score_filter:
                        st.session_state['score_radio'] = new_score_filter
                        st.rerun()
            
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
                                render_account_card(account, data, month=selected_month_key)
    
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
                
                with st.expander(f"{account} - {data['vertical']}", expanded=is_expanded):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Score:** {data['score']:.2f}" if data['score'] else "**Score:** N/A")
                        st.markdown(f"**Review Date:** {data['date'].strftime('%m/%d/%Y') if pd.notna(data['date']) else 'N/A'}")
                        st.markdown(f"**Responses:** {data['response_count']}")
                    with col2:
                        st.markdown(f"**Account Director:** {data.get('account_director', 'N/A')}")
                    
                    st.markdown("**Attendees:**")
                    st.write(data.get('attendees', 'N/A'))
                    
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
    
    elif st.session_state['current_view'] == 'detail':
        st.subheader("Complete Scorecard Detail View")
        st.markdown("View all questions and answers from the CSV for a specific account.")
        
        # Account selector for detail view
        detail_account_options = ['Select an account...'] + sorted([k for k, v in accounts_with_data.items()])
        selected_detail_account = st.selectbox(
            "Select Account to View Details",
            detail_account_options,
            index=0,
            key='detail_account_select'
        )
        
        if selected_detail_account and selected_detail_account != 'Select an account...':
            account_data = accounts_with_data[selected_detail_account]
            raw_data = account_data.get('raw_data', {})
            
            if raw_data:
                st.markdown(f"### Complete Data for: **{selected_detail_account}**")
                st.markdown("---")
                
                # Display all CSV fields
                st.markdown("#### All Fields from CSV")
                
                # Group fields logically
                basic_info = {}
                review_info = {}
                other_fields = {}
                
                for key, value in raw_data.items():
                    if pd.isna(value) or str(value).strip() == '':
                        continue
                    
                    key_lower = str(key).lower()
                    if any(x in key_lower for x in ['id', 'start time', 'completion time', 'email', 'name', 'please enter']):
                        basic_info[key] = value
                    elif any(x in key_lower for x in ['account', 'date', 'time', 'score', 'summary', 'feedback', 'action', 'attend', 'ifm', 'fm']):
                        review_info[key] = value
                    else:
                        other_fields[key] = value
                
                # Display basic info
                if basic_info:
                    with st.expander("Basic Information", expanded=False):
                        for key, value in basic_info.items():
                            st.markdown(f"**{key}:**")
                            st.write(str(value))
                            st.markdown("---")
                
                # Display review info
                if review_info:
                    with st.expander("Review Information", expanded=True):
                        for key, value in review_info.items():
                            st.markdown(f"**{key}:**")
                            st.write(str(value))
                            st.markdown("---")
                
                # Display other fields
                if other_fields:
                    with st.expander("Additional Fields", expanded=False):
                        for key, value in other_fields.items():
                            st.markdown(f"**{key}:**")
                            st.write(str(value))
                            st.markdown("---")
                
                # Also show as raw JSON for debugging
                with st.expander("🔧 Raw Data (JSON)", expanded=False):
                    import json
                    # Convert to JSON-serializable format
                    json_data = {}
                    for k, v in raw_data.items():
                        if pd.notna(v):
                            try:
                                json_data[k] = str(v)
                            except:
                                json_data[k] = "Unable to serialize"
                    st.json(json_data)
            else:
                st.warning("No raw data available for this account.")
        else:
            st.info("👆 Please select an account from the dropdown above to view complete details.")

if __name__ == "__main__":
    main()

