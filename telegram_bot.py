import time
import feedparser
import telebot
from flask import Flask
import threading
import os
import sys

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")

# 🔍 NEW SEARCH QUERY: We search specifically for results, profit, and loss
RSS_URL = "https://news.google.com/rss/search?q=India+corporate+results+OR+net+profit+OR+quarterly+earnings+when:1h&ceid=IN:en&hl=en-IN&gl=IN"

# 🛑 SMART FILTERS: The bot will ONLY send news containing these words
FILTER_KEYWORDS = [
    "net profit", "net loss", "quarterly results", "q1", "q2", "q3", "q4", 
    "earnings", "revenue", "dividend", "ebitda", "margin"
]

# Security Check
if not BOT_TOKEN or not CHANNEL_USERNAME:
    print("❌ ERROR: Missing Keys. Please check Render Environment Variables.")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- STARTUP BASELINE (Prevents Spam on Restart) ---
print("⏳ Establishing baseline... (ignoring old news)")
try:
    initial_feed = feedparser.parse(RSS_URL)
    if initial_feed.entries:
        last_title = initial_feed.entries[0].title
        print(f"✅ Baseline set: {last_title}")
    else:
        last_title = None
except Exception as e:
    print(f"Error setting baseline: {e}")
    last_title = None

def is_profit_loss_news(title):
    """
    Returns True ONLY if the news is about financial results.
    Case-insensitive check against our FILTER_KEYWORDS list.
    """
    title_lower = title.lower()
    for word in FILTER_KEYWORDS:
        if word in title_lower:
            return True
    return False

def get_latest_news():
    global last_title
    try:
        feed = feedparser.parse(RSS_URL)
        if feed.entries:
            latest = feed.entries[0]
            
            # 1. Check if it is NEW
            if latest.title != last_title:
                last_title = latest.title # Update memory
                
                # 2. Check if it is about PROFIT/LOSS (The Filter)
                if is_profit_loss_news(latest.title):
                    return latest.title, latest.link
                else:
                    print(f"🗑️ Skipped irrelevent news: {latest.title}")
                    
    except Exception as e:
        print(f"Error fetching news: {e}")
    return None, None

def send_to_telegram(title, link):
    try:
        # I added a nice emoji 💰 for money news
        msg = f"💰 *EARNINGS ALERT* 💰\n\n{title}\n\n[Read Report]({link})"
        bot.send_message(CHANNEL_USERNAME, msg, parse_mode='Markdown')
        print(f"✅ Sent: {title}")
    except Exception as e:
        print(f"❌ Send Error: {e}")

# --- BOT LOOP ---
def start_bot_loop():
    print("Bot loop started...")
    while True:
        time.sleep(10) # Short wait before first run
        
        title, link = get_latest_news()
        if title:
            send_to_telegram(title, link)
            
        time.sleep(300) # Check every 5 minutes

threading.Thread(target=start_bot_loop, daemon=True).start()

# --- WEB SERVER ---
@app.route('/')
def home():
    return "Earnings Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
