import os
import requests
import feedparser
import json
import time

# Telegram bot settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# 定义 RSS 源网址
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
    response = requests.post(url, json=payload)
    
    # 打印发送的消息和响应
    print(f'Sending message: {message}')
    print(f'Response Status Code: {response.status_code}, Response Body: {response.text}')
    
    if response.status_code != 200:
        print("Failed to send message.")

def fetch_feed(feed_url):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f'Attempt {attempt + 1} to fetch feed: {feed_url}')
            feed = feedparser.parse(feed_url)
            if feed.bozo:  # 检查是否解析失败
                raise Exception('Failed to parse feed')
            return feed
        except Exception as e:
            print(f'Error fetching {feed_url}: {e}')
            time.sleep(2)  # 等待 2 秒再重试
    return None

def main():
    sent_entries = load_sent_entries()
    new_entries = []

    for feed_url in RSS_FEEDS:
        print(f'Fetching feed: {feed_url}')
        
        # 添加延迟
        time.sleep(2)  # 等待 2 秒

        feed = fetch_feed(feed_url)
        if feed is None:
            print(f'Failed to fetch feed after multiple attempts: {feed_url}')
            continue
        
        print(f'Entries found: {len(feed.entries)}')
        
        for entry in feed.entries:
            print(f'Entry title: {entry.title}, Entry link: {entry.link}')
            
            if entry.link not in sent_entries:
                send_message(entry.title + ' ' + entry.link)
                new_entries.append(entry.link)

    # Update sent entries
    sent_entries.extend(new_entries)
    save_sent_entries(sent_entries)

if __name__ == "__main__":
    main()
