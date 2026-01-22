import time
import feedparser
import telebot
from flask import Flask
import threading
import os
import sys

# --- CONFIGURATION ---
# 1. We get the variables from Render (Secure)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME")
RSS_URL = "https://news.google.com/rss/search?q=stock+market+india+when:1h&ceid=IN:en&hl=en-IN&gl=IN"

# 2. Safety Check: If variables are missing, warn us instead of crashing
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN is missing in Render Environment Variables.")
    # Fallback for testing (only if you really need it, but better to use Render vars)
    # BOT_TOKEN = "8540514459:AAE58lJVaQLxYvCQNtQSZx9W1flYJ5c6IyM" 

if not CHANNEL_USERNAME:
    print("❌ ERROR: CHANNEL_USERNAME is missing.")
    # Fallback
    # CHANNEL_USERNAME = "@stockmarketnewsofficiall"

# 3. Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
last_title = None

def get_latest_news():
    global last_title
    try:
        feed = feedparser.parse(RSS_URL)
        if feed.entries:
            latest = feed.entries[0]
            if latest.title != last_title:
                last_title = latest.title
                return latest.title, latest.link
    except Exception as e:
        print(f"Error fetching news: {e}")
    return None, None

def send_to_telegram(title, link):
    try:
        msg = f"🚨 *MARKET UPDATE* 🚨\n\n{title}\n\n[Read Story]({link})"
        # 4. FIXED: Use the variable CHANNEL_USERNAME
        bot.send_message(CHANNEL_USERNAME, msg, parse_mode='Markdown')
        print(f"✅ Sent message to {CHANNEL_USERNAME}")
    except Exception as e:
        print(f"❌ Send Error: {e}")

# --- THE BOT LOOP ---
def start_bot_loop():
    print("Bot loop started...")
    while True:
        title, link = get_latest_news()
        if title:
            send_to_telegram(title, link)
        time.sleep(300) # 5 minutes

threading.Thread(target=start_bot_loop, daemon=True).start()

# --- WEB SERVER ---
@app.route('/')
def home():
    return "Bot is running 24/7!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
