import feedparser
import requests
import os
import concurrent.futures
from datetime import datetime, timedelta
import time

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
def fetch_rss_entries(url):
    entries = []
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            entry_time = datetime(*entry.published_parsed[:6])
            if yesterday <= entry_time <= now:
                if entry.link not in sent_entries:
                    entries.append(entry)
                    sent_entries.add(entry.link)
    except Exception as e:
        print(f"Failed to fetch RSS from {url}: {e}")
    
    return entries

# 多线程获取所有RSS源的内容
def get_all_rss_entries():
    all_entries = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(fetch_rss_entries, url): url for url in RSS_URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                entries = future.result()
                all_entries.extend(entries)
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")
        executor.shutdown(wait=True)  # 确保所有线程完成
    return all_entries

# 发送消息到Telegram
def send_to_telegram(text):
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(TELEGRAM_URL, data=payload)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    # 获取24小时内的RSS条目
    entries = get_all_rss_entries()
    if entries:
        for entry in entries:
            message = f"{entry.title}\n{entry.link}"
            send_to_telegram(message)
            time.sleep(1)  # 每发送一条消息，等待2秒，防止过快发送
    else:
        print("No new RSS entries found in the last 24 hours.")
    
    # 增加额外等待时间，确保所有任务完成后才退出
    print("All messages sent, waiting before exit...")
    time.sleep(50)  # 脚本结束前额外等待30秒
