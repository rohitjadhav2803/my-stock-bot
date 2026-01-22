import time
import feedparser
import telebot

# --- CONFIGURATION ---
BOT_TOKEN = "8540514459:AAF7-RCzKAfaVfloAZqVn2SkSzMeWkJUiMo"
CHANNEL_USERNAME = "@livestockmarketnewbot" # Example: @rohit_market_news
RSS_URL = "https://news.google.com/rss/search?q=stock+market+india+when:1h&ceid=IN:en&hl=en-IN&gl=IN"

# Initialize Bot
bot = telebot.TeleBot(BOT_TOKEN)

# Store last title to avoid duplicates
last_title = None

def get_latest_news():
    global last_title
    print("Checking news...")
    
    try:
        # Parse Google News RSS
        feed = feedparser.parse(RSS_URL)
        
        if feed.entries:
            latest = feed.entries[0]
            title = latest.title
            link = latest.link
            
            # If the news is different from the last one we sent
            if title != last_title:
                last_title = title
                return title, link
                
    except Exception as e:
        print(f"Error fetching news: {e}")
        
    return None, None

def send_to_telegram(title, link):
    try:
        # Create a nice message format
        message = f"🚨 *MARKET UPDATE* 🚨\n\n**{title}**\n\n[Read Full Story]({link})"
        
        # Send to Channel (parse_mode='Markdown' makes it bold)
        bot.send_message(CHANNEL_USERNAME, message, parse_mode='Markdown')
        print(f"✅ Sent: {title}")
        
    except Exception as e:
        print(f"❌ Error sending message: {e}")

# --- MAIN LOOP ---
print("Bot is running...")
send_to_telegram("Bot Started! Waiting for news...", "https://google.com")

while True:
    new_title, new_link = get_latest_news()
    
    if new_title:
        send_to_telegram(new_title, new_link)
    
    # Check every 5 minutes (300 seconds)
    time.sleep(300)