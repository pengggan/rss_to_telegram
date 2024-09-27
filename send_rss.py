import feedparser
import requests
import os
import concurrent.futures
import time
import json

# RSS URL列表
RSS_URLS = [
    "https://rsshub.app/zaobao/znews/china",
    "https://rsshub.app/guancha/headline",
    "https://rsshub.app/youtube/playlist/PLRQMDFCUMjJW_R29PyDKbILE2Nj6mC3X3",
    "https://blog.090227.xyz/atom.xml",
    "https://rsshub.app/youtube/playlist/PLvrTMNP6Iw6oTPlmRHvjAWiCeQpwHK6yG",
    "https://www.freedidi.com/feed",
    "https://www.digihubs.xyz/feeds/posts/default?alt=rss",
    "https://p3terx.com/feed",
    "https://www.youtube.com/@bulianglin/videos",
    "https://www.youtube.com/@IamJackLiu/videos",
    "https://rsshub.app/fortunechina",
    "https://www.youtube.com/@%E4%B8%AD%E6%8C%87%E9%80%9A/videos",
    "https://www.youtube.com/@TchLiyongle/videos",
    "https://sspai.com/feed",
    "https://hunsh.net/atom.xml"
]

# 环境变量
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# 检查是否存在 sent_entries.json 文件，不存在则创建
if not os.path.exists('sent_entries.json'):
    with open('sent_entries.json', 'w') as f:
        json.dump([], f)  # 创建一个空的 JSON 文件（列表）
        
# 记录文件
SENT_ENTRIES_FILE = 'sent_entries.json'

# 读取已发送的消息
def load_sent_entries():
    if os.path.exists(SENT_ENTRIES_FILE):
        with open(SENT_ENTRIES_FILE, 'r') as f:
            return set(json.load(f))
    return set()

# 保存已发送的消息
def save_sent_entries(entries):
    try:
        with open(SENT_ENTRIES_FILE, 'w') as f:
            json.dump(list(entries), f)
        print(f"Saved sent entries to {SENT_ENTRIES_FILE}.")  # 调试信息
    except Exception as e:
        print(f"Error saving sent entries: {e}")

# 获取RSS条目
def fetch_rss_entries(url, sent_entries):
    entries = []
    max_attempts = 2  # 最大重试次数
    wait_time = 100   # 每次重试之间的等待时间（秒）

    for attempt in range(max_attempts): 
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
            if attempt == max_attempts - 1:
                print(f"Giving up on {url} after {max_attempts} attempts.")
            time.sleep(wait_time)  # 等待后重试
    return entries

# 多线程获取所有RSS源的内容
def get_all_rss_entries(sent_entries):
    all_entries = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(fetch_rss_entries, url, sent_entries): url for url in RSS_URLS}
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
    # 加载已发送的消息
    sent_entries = load_sent_entries()
    
    # 获取所有RSS条目
    entries = get_all_rss_entries(sent_entries)
    if entries:
        for entry in entries:
            message = f"{entry.title}\n{entry.link}"
            send_to_telegram(message)
            time.sleep(1)  # 每发送一条消息，等待2秒
    
    # 保存已发送的消息
    save_sent_entries(sent_entries)

    print("All messages sent, waiting before exit...")
    time.sleep(5)  # 脚本结束前额外等待30秒
