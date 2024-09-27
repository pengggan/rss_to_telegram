import feedparser
import requests
import os
import concurrent.futures
import time
from html import escape

# 直接在代码中配置RSS URL列表
RSS_URLS = [
    "https://rsshub.app/zaobao/znews/china",
    "https://rsshub.app/guancha/headline",
    "https://blog.090227.xyz/atom.xml",
    "https://www.freedidi.com/feed",
    "https://www.digihubs.xyz/feeds/posts/default?alt=rss",
    "https://p3terx.com/feed",
    "https://rsshub.app/fortunechina",
    "https://www.youtube.com/@bulianglin/videos",
    "https://www.youtube.com/@IamJackLiu/videos",
    "https://www.youtube.com/@%E4%B8%AD%E6%8C%87%E9%80%9A/videos",
    "https://www.youtube.com/@TchLiyongle/videos",
    "https://rsshub.app/youtube/playlist/PLRQMDFCUMjJW_R29PyDKbILE2Nj6mC3X3",
    "https://rsshub.app/youtube/playlist/PLvrTMNP6Iw6oTPlmRHvjAWiCeQpwHK6yG",
    "https://sspai.com/feed",
    "https://hunsh.net/atom.xml"
]

# 从环境变量中读取敏感信息
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# 记录已发送的消息，避免重复
sent_entries = set()

# 获取RSS条目
def fetch_rss_entries(url):
    entries = []

    for attempt in range(3):  # 增加重试机制
        try:
            feed = feedparser.parse(url)
            if feed.bozo:
                print(f"Failed to parse feed from {url}: {feed.bozo_exception}")
                return []

            for entry in feed.entries:
                if entry.link not in sent_entries:
                    entries.append(entry)
                    sent_entries.add(entry.link)

            print(f"Fetched {len(entries)} entries from {url}.")  # 调试信息
            break  # 如果成功，退出重试循环
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to fetch RSS from {url}: {e}")
            if attempt == 2:
                print(f"Giving up on {url} after 3 attempts.")
            time.sleep(2)  # 等待后重试
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
    # 获取所有RSS条目
    entries = get_all_rss_entries()
    if entries:
        for entry in entries:
            message = f"{escape(entry.title)}\n{escape(entry.link)}"  # 确保标题和链接转义
            send_to_telegram(message)
            time.sleep(0)  # 每发送一条消息，等待2秒
    else:
        print("No new RSS entries found.")

    # 增加额外等待时间，确保所有任务完成后才退出
    print("All messages sent, waiting before exit...")
    time.sleep(50)  # 脚本结束前额外等待30秒
