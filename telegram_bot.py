import time
import feedparser
import telebot
from flask import Flask
import threading
import os

# --- CONFIGURATION ---
# We use os.environ to read the token from Render safely
BOT_TOKEN = os.environ.get("8540514459:AAE58lJVaQLxYvCQNtQSZx9W1flYJ5c6IyM") 
CHANNEL_USERNAME = os.environ.get("@stockmarketnewsofficiall") 
RSS_URL = "https://news.google.com/rss/search?q=stock+market+india+when:1h&ceid=IN:en&hl=en-IN&gl=IN"

bot = telebot.TeleBot("8540514459:AAE58lJVaQLxYvCQNtQSZx9W1flYJ5c6IyM")
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
        print(f"Error: {e}")
    return None, None

def send_to_telegram(title, link):
    try:
        msg = f"🚨 *MARKET UPDATE* 🚨\n\n{title}\n\n[Read Story]({link})"
        bot.send_message(@stockmarketnewsofficiall, msg, parse_mode='Markdown')
    except Exception as e:
        print(f"Send Error: {e}")

# --- THE BOT LOOP (Runs in Background) ---
def start_bot_loop():
    print("Bot loop started...")
    while True:
        title, link = get_latest_news()
        if title:
            send_to_telegram(title, link)
        time.sleep(300) # Check every 5 minutes

# Start bot in a separate thread so it doesn't block the web server
threading.Thread(target=start_bot_loop, daemon=True).start()

# --- THE FAKE WEB SERVER (To keep Render happy) ---
@app.route('/')
def home():
    return "Bot is running 24/7!"

if __name__ == "__main__":
    # Render assigns a port automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


