import os
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from pytrends.request import TrendReq

# Define Google credentials
SERVICE_ACCOUNT_INFO = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
credentials = Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
client = gspread.authorize(credentials)

# Define Google Sheet details
spreadsheet_id = os.environ['SPREADSHEET_ID']
worksheet_name = os.environ.get('WORKSHEET_NAME', 'Sheet1')  # Default to 'Sheet1'

# Get worksheet
sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)

# Fetch keywords from pytrends
all_rising_keywords = []

# Set up pytrends
pytrends = TrendReq()

# Load countries and niches from environment variables
COUNTRIES = os.environ.get('COUNTRY', 'US,GB,IN').split(',')
NICHES = os.environ.get('NICHES', 'technology,marketing').split(',')

# Loop through all combinations
for country in COUNTRIES:
    for niche in NICHES:
        search_topic = f"{niche} {country}"
        pytrends.build_payload([search_topic], timeframe='now 7-d', geo=country)
        try:
            related_queries = pytrends.related_queries()
            if (related_queries and 
                'default' in related_queries and 
                'rankedList' in related_queries['default'] and
                len(related_queries['default']['rankedList']) > 0 and
                'rankedKeyword' in related_queries['default']['rankedList'][0]):
                print(f"Related keywords found for {search_topic}.")
            else:
                print(f"No related keywords found for {search_topic}.")
                continue  # Skip if no related keywords
        except Exception as e:
            print(f"Error fetching related queries for {search_topic}: {e}")
            continue

        if search_topic in related_queries and 'rising' in related_queries[search_topic]:
            rising = related_queries[search_topic]['rising']
            if rising is not None:
                all_rising_keywords.extend(rising['query'].tolist())

# Remove duplicates
all_rising_keywords = list(set(all_rising_keywords))

# Push to Google Sheet
for keyword in all_rising_keywords:
    sheet.append_row([keyword])

print(f"✅ Successfully updated {len(all_rising_keywords)} keywords to Google Sheet.")
