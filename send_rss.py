import os
import requests
import feedparser
import json

# Telegram bot settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# 定义 RSS 源网址
RSS_FEEDS = [
    'https://rsshub.app/guancha/headline',
    'https://rsshub.app/zaobao/znews/china',
    'https://www.freedidi.com/feed',
    'https://p3terx.com/feed',
    'https://sspai.com/feed',
    'https://www.digihubs.xyz/feeds/posts/default?alt=rss',
    'https://blog.090227.xyz/atom.xml',
    'https://hunsh.net/atom.xml',
    'https://www.112114.xyz/rss',
    'https://rsshub.app/youtube/playlist/PLRQMDFCUMjJW_R29PyDKbILE2Nj6mC3X3',
    'https://rsshub.app/youtube/playlist/PLvrTMNP6Iw6oTPlmRHvjAWiCeQpwHK6yG',
    'https://www.youtube.com/@bulianglin/videos',
    'https://www.youtube.com/@IamJackLiu/videos',
    'https://www.youtube.com/@TchLiyongle/videos',
    'https://www.youtube.com/@%E4%B8%AD%E6%8C%87%E9%80%9A/videos',
    'https://rsshub.app/fortunechina'
]

# Load sent entries from a JSON file
def load_sent_entries():
    if os.path.exists('sent_entries.json'):
        with open('sent_entries.json', 'r') as f:
            return json.load(f)
    return []

# Save sent entries to a JSON file
def save_sent_entries(sent_entries):
    with open('sent_entries.json', 'w') as f:
        json.dump(sent_entries, f)

def send_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, json=payload)

def main():
    sent_entries = load_sent_entries()
    new_entries = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            if entry.link not in sent_entries:
                send_message(entry.title + ' ' + entry.link)
                new_entries.append(entry.link)

    # Update sent entries
    sent_entries.extend(new_entries)
    save_sent_entries(sent_entries)

if __name__ == "__main__":
    main()
