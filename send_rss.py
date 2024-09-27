import feedparser
import requests
import os
import time
from datetime import datetime, timedelta

# 直接在代码中配置RSS URL列表
RSS_URLS = [
    "https://rsshub.app/guancha/headline",
    "https://rsshub.app/zaobao/znews/china",
    "https://www.freedidi.com/feed",
    "https://p3terx.com/feed",
    "https://sspai.com/feed",
    "https://www.digihubs.xyz/feeds/posts/default?alt=rss",
    "https://blog.090227.xyz/atom.xml",
    "https://hunsh.net/atom.xml",
    "https://www.112114.xyz/rss",
    "https://rsshub.app/youtube/playlist/PLRQMDFCUMjJW_R29PyDKbILE2Nj6mC3X3",
    "https://rsshub.app/youtube/playlist/PLvrTMNP6Iw6oTPlmRHvjAWiCeQpwHK6yG",
    "https://www.youtube.com/@bulianglin/videos",
    "https://www.youtube.com/@IamJackLiu/videos",
    "https://www.youtube.com/@TchLiyongle/videos",
    "https://www.youtube.com/@%E4%B8%AD%E6%8C%87%E9%80%9A/videos",
    "https://rsshub.app/fortunechina"
]

# 从环境变量中读取敏感信息
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# 记录已发送的消息，避免重复
sent_entries = set()

# 获取过去24小时的RSS条目
def get_rss_entries():
    entries = []
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            entry_time = datetime(*entry.published_parsed[:6])
            if yesterday <= entry_time <= now:
                if entry.link not in sent_entries:
                    entries.append(entry)
                    sent_entries.add(entry.link)
    return entries

# 发送消息到Telegram
def send_to_telegram(text):
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'disable_web_page_preview': True
    }
    requests.post(TELEGRAM_URL, data=payload)

# 分批发送，避免一次性大量发送
def send_in_batches(entries, batch_size=5, delay=5):
    for i in range(0, len(entries), batch_size):
        batch = entries[i:i + batch_size]
        for entry in batch:
            message = f"{entry.title}\n{entry.link}"
            send_to_telegram(message)
        time.sleep(delay)  # 延迟，避免一次性发送太多

if __name__ == "__main__":
    # 获取24小时内的RSS条目
    entries = get_rss_entries()
    if entries:
        send_in_batches(entries)
    else:
        print("No new RSS entries found in the last 24 hours.")
