import os
import json
import requests
from feedparser import parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

RSS_FEEDS = [
    'https://www.youtube.com/@bulianglin/videos',
    'https://www.youtube.com/@IamJackLiu/videos',
    'https://www.youtube.com/@TchLiyongle/videos',
    'https://www.youtube.com/@%E4%B8%AD%E6%8C%87%E9%80%9A/videos',
    'https://rsshub.app/youtube/playlist/PLRQMDFCUMjJW_R29PyDKbILE2Nj6mC3X3',
    'https://rsshub.app/youtube/playlist/PLvrTMNP6Iw6oTPlmRHvjAWiCeQpwHK6yG',
    # 添加更多 RSS 源
]

TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_YOUTUBE']}/sendMessage"

def load_sent_entries():
    try:
        with open('sent_entries.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_sent_entries(entries):
    with open('sent_entries.json', 'w') as f:
        json.dump(entries, f)

def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    requests.post(TELEGRAM_API_URL, json=payload)

def fetch_feed(feed):
    try:
        response = requests.get(feed, timeout=59)  # 增加超时时间
        response.raise_for_status()  # 检查请求是否成功
        return parse(response.content)  # 返回解析的内容
    except Exception as e:
        print(f"Error fetching {feed}: {e}")
        return None

def process_feed(feed, sent_entries, chat_id):
    feed_data = fetch_feed(feed)
    if feed_data is None:
        return []

    new_entries = []
    for entry in feed_data.entries:
        if entry.link not in sent_entries:
            message = f"*{entry.title}*\n{entry.link}"
            send_message(chat_id, message)
            new_entries.append(entry.link)
            time.sleep(1)  # 添加延迟以避免 Telegram API 限制
    return new_entries

def main():
    sent_entries = load_sent_entries()
    new_entries = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_feed, feed, sent_entries, os.environ['TELEGRAM_CHAT_ID']): feed for feed in RSS_FEEDS}
        for future in as_completed(futures):
            new_entries.extend(future.result() or [])

    sent_entries.extend(new_entries)
    save_sent_entries(sent_entries)

if __name__ == "__main__":
    main()