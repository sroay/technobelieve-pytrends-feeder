from pytrends.request import TrendReq
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import os

# Setup PyTrends
pytrends = TrendReq(hl='en-US', tz=360)

# Define your seed topics here
seed_topics = [
    "AI marketing for real estate",
    "automation for fintech companies",
    "AI lead generation for ecommerce stores",
    "automation tools for freelancers",
    "AI bots for healthcare clinics",
    "automation CRM for dentists",
    "AI marketing for lawyers",
    "AI automation for online courses",
    "AI tools for marketing agencies",
    "AI customer service for hotels",
    "AI CRM for insurance agents",
    "industrial automation using AI",
    "AI marketing for construction businesses",
    "AI onboarding automation for SaaS",
    "AI marketing automation for SMEs",
    "latest AI trends",
    "GPT-4 Turbo updates",
    "LLM models for businesses",
    "AI automation agents"
]

# Connect to Google Sheets
SERVICE_ACCOUNT_INFO = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=scopes)
client = gspread.authorize(credentials)

# Define Google Sheet details
spreadsheet_id = os.environ['SPREADSHEET_ID']
worksheet_name = os.environ.get('WORKSHEET_NAME', 'Sheet1')  # Default to 'Sheet1'

# Get worksheet
sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)

# Fetch keywords from pytrends
all_rising_keywords = []

for topic in seed_topics:
    pytrends.build_payload([topic], timeframe='now 7-d')
    related_queries = pytrends.related_queries()
    if topic in related_queries:
        rising = related_queries[topic]['rising']
        if rising is not None:
            all_rising_keywords.extend(rising['query'].tolist())

# Remove duplicates
all_rising_keywords = list(set(all_rising_keywords))

# Push to Google Sheet
for keyword in all_rising_keywords:
    sheet.append_row([keyword, "Pending", "", "", ""])

print(f"Inserted {len(all_rising_keywords)} new keywords successfully!")
