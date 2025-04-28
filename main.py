import os
import json
import random
import requests
import time
import pandas as pd
from pytrends.request import TrendReq
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# 🚨 Telegram Alert Sender
def send_telegram_alert(message):
    BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

# 🚀 Set up Google Service
SERVICE_ACCOUNT_INFO = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    SERVICE_ACCOUNT_INFO, scopes=scope)

client = gspread.authorize(credentials)

# 🚀 Connect to your Google Sheet
spreadsheet_id = os.environ['SPREADSHEET_ID']
sheet = client.open_by_key(spreadsheet_id).sheet1

# 🚀 Setup PyTrends
pytrends = TrendReq(hl='en-US', tz=360)

# Define countries and niches
countries = ['US', 'GB', 'AE', 'AU', 'IN']
niches = [
    'AI automation',
    'digital marketing',
    'AI tools',
    'real estate technology',
    'fintech innovations',
    'freelancer marketing',
    'medical technology',
    'biotech startups',
    'saas marketing',
    'cybersecurity',
    'law firms digital',
    'education technology',
    'logistics automation',
    'travel technology'
]

# 🚀 Start fetching
all_keywords = []

try:
    for country in countries:
        for niche in niches:
            pytrends.build_payload([niche], cat=0, timeframe='now 7-d', geo=country)
            raise Exception("💥 Simulated Crash for Testing Telegram Alert")
            related_queries = pytrends.related_queries()

            try:
                keywords = related_queries[niche]['top']
                if keywords is not None:
                    top_keywords = keywords.sort_values(by='value', ascending=False)['query'].tolist()
                    all_keywords.extend(top_keywords[:5])  # Fetch top 5 related keywords
                else:
                    print(f"No related keywords found for niche: {niche} in country: {country}")
            except Exception as e_inner:
                print(f"Error processing niche {niche} for country {country}: {e_inner}")
                send_telegram_alert(f"🚨 Error processing niche {niche} in {country}: {str(e_inner)}")

except Exception as e_outer:
    print(f"Error fetching related queries: {e_outer}")
    send_telegram_alert(f"🚨 Feeder crashed while fetching keywords: {str(e_outer)}")
    all_keywords = []

# 🚀 Remove duplicates and shuffle
all_keywords = list(set(all_keywords))
random.shuffle(all_keywords)

# 🚀 Upload to Google Sheet
if all_keywords:
    sheet.clear()
    for idx, keyword in enumerate(all_keywords, start=1):
        sheet.update_cell(idx, 1, keyword)
    print(f"✅ Successfully updated {len(all_keywords)} keywords to Google Sheet.")
else:
    print("⚠️ No keywords fetched to update.")
    
