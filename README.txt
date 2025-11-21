Telegram Kino Bot - Package for Abu oka

Files:
- bot.py         : Main bot script. Edit TOKEN, ADMIN_ID, CHANNEL_ID at top.
- movies.json    : Auto-created DB file (empty array).
- requirements.txt

How to run locally:
1) Create virtual env (recommended)
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate    # Windows

2) Install deps:
   pip install -r requirements.txt

3) Run:
   python bot.py

Notes:
- Make sure the bot token and ADMIN_ID are correct.
- Add the bot as admin to your channel.
- Use /addmovie with format: name|link|image_url(optional)
  Example: /addmovie My Movie|https://example.com|https://example.com/poster.jpg
- For inline search, type @YourBotUsername <search term> in any chat.
