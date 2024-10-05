import os
import json
import requests
from feedparser import parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# RSS 源列表
RSS_FEEDS = [
    # 'https://36kr.com/feed',
    # 'https://rsshub.app/guancha/headline',
    'https://rsshub.app/zaobao/znews/china',
    'https://rsshub.app/fortunechina',
    'https://www.freedidi.com/feed',
    # 'https://p3terx.com/feed',
    # 'https://sspai.com/feed',
    # 'https://www.digihubs.xyz/feeds/posts/default?alt=rss',
    'https://blog.090227.xyz/atom.xml',
    # 'https://hunsh.net/atom.xml',
    'http://blog.caixin.com/feed',
    # 'http://news.stockstar.com/rss/xml.aspx?file=xml/stock/2.xml',
    # 'http://cn.reuters.com/rssfeed/cnintlbiznews',
    # 'https://qks.sufe.edu.cn/J/CJYJ/RSS/CN',
    # 'https://www.economist.com/sections/china/rss.xml',
    # 添加更多 RSS 源
]

# Telegram API URL
TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN_RSS']}/sendMessage"

def load_sent_entries():
    try:
        # 使用相对路径加载已发送条目
        with open('sent_entries.json', 'r') as f:
            return set(json.load(f))  # 使用集合存储已发送条目
    except FileNotFoundError:
        return set()

def save_sent_entries(entries):
    # 使用相对路径保存已发送条目
    with open('sent_entries.json', 'w') as f:
        json.dump(list(entries), f)  # 保存为列表格式

def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        response.raise_for_status()  # 检查请求是否成功
        print(f"Message sent: {text}")  # 日志记录
    except Exception as e:
        print(f"Error sending message: {e}")

def fetch_feed(feed):
    try:
        response = requests.get(feed, timeout=119)
        response.raise_for_status()
        return parse(response.content)
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
            sent_entries.add(entry.link)  # 立即更新 sent_entries
            time.sleep(3)  # 处理每个条目的额外延迟
    return new_entries

def main():
    sent_entries = load_sent_entries()
    new_entries = []

    max_workers = 5  # 根据需要调整线程数量
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_feed, feed, sent_entries, os.environ['TELEGRAM_CHAT_ID']): feed for feed in RSS_FEEDS}
        for future in as_completed(futures):
            new_entries.extend(future.result() or [])

    save_sent_entries(sent_entries)

if __name__ == "__main__":
    main()
