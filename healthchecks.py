import requests
import os
import time

API_KEY = os.getenv("HEALTH_BOT_API")
ID = os.getenv("GROUP_ID")
MSG = ""

url = 'https://api.telegram.org/bot' + API_KEY + \
    '/sendMessage?chat_id=' + ID + '&parse_mode=Markdown&text='

while True:

    # YouTube Statistics Telegram Bot
    try:
        requests.get(
            "https://hc-ping.com/1152cf9e-9522-460b-af8e-d2ba5dc7025f", timeout=30)
        MSG += "🟢 YOUTUBE STATISTICS BOT\n\n"
    except:
        MSG += "🔴 YOUTUBE STATISTICS BOT\n\n"

    requests.get(url=(url+MSG))
    MSG = ""
    time.sleep(3600)
