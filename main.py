import os
import json
import requests
import pandas as pd
from pytrends.request import TrendReq

# Initialize pytrends
pytrends = TrendReq()

# Telegram alert setup
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        try:
            requests.post(url, data=payload)
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")

# Load environment variables
countries = json.loads(os.environ.get('COUNTRIES', '["US"]'))
niches = json.loads(os.environ.get('NICHES', '["travel technology"]'))

# 🚀 Start fetching
all_keywords = []

try:
    # 💥 Force Crash Immediately INSIDE try-block
    raise Exception("💥 Simulated Crash for Fast Testing Telegram Alert")

    for country in countries:
        for niche in niches:
            pytrends.build_payload([niche], cat=0, timeframe='now 7-d', geo=country)
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

# 🚀 (Later parts: uploading to sheet, etc.)
