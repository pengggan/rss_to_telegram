name: RSS to Telegram

on:
  workflow_dispatch:
  schedule:
    - cron: '6 * * * *'  # 每6小时运行一次
  push:
    branches:
      - main  # 在主分支代码更新时触发

jobs:
  send_rss:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'  # 或者你需要的其他版本

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests
          pip install feedparser
          pip install aiohttp

      - name: Run RSS to Telegram script
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python send_rss.py
          
      - name: Commit sent entries
        run: |
          git config --global user.name 'github-actions'
          git config --global user.email 'action@github.com'
          git add sent_entries.json
          if ! git diff --cached --quiet; then  # 检查是否有变化
            git commit -m 'Update sent entries'
            git push
          else
            echo "No changes to commit"
          fi