import os
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pytrends.request import TrendReq

# Initialize pytrends
pytrends = TrendReq()

# Load environment variables
country = os.environ.get('COUNTRY', 'US')
niches = json.loads(os.environ.get('NICHES', '["travel technology"]'))
spreadsheet_id = os.environ.get('SPREADSHEET_ID')
worksheet_tab = os.environ.get('SPREADSHEET_TAB', 'Sheet1')

# Authenticate with Google Sheets
SERVICE_ACCOUNT_INFO = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
client = gspread.authorize(credentials)
sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_tab)

# 🚀 Start fetching
all_keywords = []

try:
    for niche in niches:
        pytrends.build_payload([niche], cat=0, timeframe='now 7-d', geo=country)
        related_queries = pytrends.related_queries()

        try:
            keywords = related_queries.get(niche, {}).get('top')
            if keywords is not None:
                top_keywords = keywords.sort_values(by='value', ascending=False)['query'].tolist()
                all_keywords.extend(top_keywords[:5])  # Fetch top 5 related keywords
            else:
                print(f"No related keywords found for niche: {niche} in country: {country}")
        except Exception as e_inner:
            print(f"Error processing niche {niche} for country {country}: {e_inner}")
except Exception as e_outer:
    print(f"Error fetching related queries: {e_outer}")
    all_keywords = []

# 🚀 Remove duplicates and shuffle
all_keywords = list(set(all_keywords))

# 🚀 Upload to Google Sheets
if all_keywords:
    sheet.update('A1', [["Keywords"]] + [[keyword] for keyword in all_keywords])
    print("✅ Successfully uploaded keywords to Google Sheets!")
else:
    print("⚠️ No keywords to upload.")
