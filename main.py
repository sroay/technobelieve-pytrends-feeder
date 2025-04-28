import os
import json
import time
from pytrends.request import TrendReq
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Setup pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])

credentials = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
client = gspread.authorize(credentials)

# Define Google Sheet details
spreadsheet_id = os.environ['SPREADSHEET_ID']
worksheet_name = os.environ.get('WORKSHEET_NAME', 'Sheet1')  # Default to 'Sheet1'

# Get worksheet
sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)

# Fetch keywords from pytrends
all_rising_keywords = []

# Read your environment variables
seed_topics = os.environ.get('NICHES', 'technology,finance,health').split(',')
countries = os.environ.get('COUNTRY', 'US').split(',')
spreadsheet_tab = os.environ.get('SPREADSHEET_TAB', 'Sheet1')

for topic in seed_topics:
    pytrends.build_payload([topic], timeframe='now 7-d')

    try:
        related_queries = pytrends.related_queries()

        if related_queries and 'default' in related_queries and 'rankedList' in related_queries['default']:
            ranked_list = related_queries['default']['rankedList']
            if ranked_list and len(ranked_list) > 0 and 'rankedKeyword' in ranked_list[0]:
                print("Related keywords found.")
                # Your logic here (optional if needed)
            else:
                print("No related keywords found for this search.")
        else:
            print("No data found for this keyword in this region.")

    except Exception as e:
        print(f"Error fetching related queries: {e}")
        related_queries = pytrends.related_queries()
        if related_queries and topic in related_queries:
            rising = related_queries[topic].get('rising')
            if rising is not None:
                all_rising_keywords.extend(rising['query'].tolist())

# Remove duplicates
all_rising_keywords = list(set(all_rising_keywords))

# Push to Google Sheet
for keyword in all_rising_keywords:
    sheet.append_row([keyword])
