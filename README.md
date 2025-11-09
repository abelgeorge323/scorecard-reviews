# Top 55 Accounts Dashboard

A Streamlit dashboard for tracking and visualizing scorecard reviews across 55 key accounts, organized by vertical.

## Features

- **Account Cards**: Visual cards showing each account's status, score, and vertical
- **Fuzzy Matching**: Automatically maps CSV account name variations to canonical names
- **Sidebar Filters**: Filter by vertical and account
- **Summary Metrics**: View total accounts, average scores, and response counts
- **Interactive Charts**: Bar charts for scores, pie charts for vertical distribution
- **Detailed Data Table**: Expandable view with full scorecard details
- **Missing Data Tracking**: Separate section showing accounts without data yet

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Ensure your CSV file is in the `Scorecards` folder:
   - `Scorecards/Scorecard Review Executive Summary(Sheet1) (1) (1).csv`

2. Run the dashboard:

```bash
streamlit run dashboard.py
```

3. The dashboard will open in your browser at `http://localhost:8501`

## Data Structure

The dashboard uses `mappings.py` as the single source of truth for all 55 accounts and their assigned verticals:

- **Aviation** (1 account)
- **Automotive** (5 accounts)
- **Manufacturing** (14 accounts)
- **Technology** (13 accounts)
- **Life Science** (17 accounts)
- **Finance** (5 accounts)
- **Distribution** (5 Nike accounts)
- **R&D / Education / Other** (1 account)

## Fuzzy Matching

The dashboard automatically maps CSV account name variations to their canonical names:

- "Merck Sodexo" → "Merck"
- "GM Milford" → "General Motors"
- "P&G(JLL)" → "Procter & Gamble Company"
- "Microsoft Puget Sound" → "Microsoft"
- And many more...

Accounts marked as "Omit" (Omnicom, JLL Northrop Grumman) are automatically filtered out.

## Dashboard Sections

### 1. Account Cards
- Grid layout showing all accounts
- Color-coded by vertical
- Shows score, date, and response count
- "Data Not Collected Yet" for accounts without data

### 2. Charts
- **Bar Chart**: Average Score by Account (sorted)
- **Pie Chart**: Response Count by Vertical

### 3. Data Table
- Sortable table with all account data
- Expandable details showing summary, feedback, and action items

### 4. Accounts Without Data
- Lists all accounts from mappings.py that don't have scorecard data yet
- Grouped by vertical

## Updating Data

To update the dashboard with new responses:

1. Replace the CSV file in the `Scorecards` folder with the updated version
2. Refresh the dashboard in your browser (hit 'R' or click "Rerun")
3. Data is cached for performance - if you need to force reload, click "Clear cache" in the Streamlit menu

## Customization

### Adding New Accounts

1. Edit `mappings.py`
2. Add the account to the `account_to_vertical` dictionary
3. Add any name variations to `account_name_variations` if needed

### Modifying Verticals

Update the vertical assignment in `account_to_vertical` dictionary in `mappings.py`

## Notes

- The dashboard ensures all 55 accounts from mappings.py appear, even if they have no data
- Scores are parsed from various formats: "5", "4.68", "4.93/5.00"
- Dates are automatically parsed from multiple formats
- The dashboard uses caching for optimal performance

