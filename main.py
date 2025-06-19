
import requests
import time
from bs4 import BeautifulSoup
from telegram import Bot
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)

# ENV variables (normally set in hosting)
SEVEN1TEL_USERNAME = os.getenv("SEVEN1TEL_USERNAME", "Tamim0987")
SEVEN1TEL_PASSWORD = os.getenv("SEVEN1TEL_PASSWORD", "81548154")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://94.23.120.156/ints/client/SMSCDRStats")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7924281956:AAFC4J5pfm1bFeXev7neWhTNMDrKH_abEnM")
GROUP_ID = int(os.getenv("GROUP_ID", "-4900913534"))

bot = Bot(token=BOT_TOKEN)
session = requests.Session()

last_otp_id = ""

def login_to_seven1tel():
    login_url = "http://94.23.120.156/ints/client/login.php"
    payload = {
        "user": SEVEN1TEL_USERNAME,
        "password": SEVEN1TEL_PASSWORD
    }
    session.post(login_url, data=payload)

def fetch_last_otp():
    res = session.get(DASHBOARD_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.find_all("tr")[1:]
    if not rows:
        return None

    cells = rows[0].find_all("td")
    if len(cells) < 6:
        return None

    otp_info = {
        "time": cells[0].text.strip(),
        "number": cells[2].text.strip(),
        "service": cells[3].text.strip(),
        "otp": cells[4].text.strip(),
        "msg": cells[5].text.strip()
    }

    return otp_info

def format_message(info, first_run=False):
    header = "🚀 বট চালু হয়েছে!\n\n✨ সর্বশেষ OTP:" if first_run else "✨ OTP এসেছে! ✨"
    message = f"""{header}

⏰ সময়: {info['time']}
📞 নাম্বার: {info['number']}
🛠️ সার্ভিস: {info['service']}
🔐 কোড: {info['otp']}
💬 বার্তা: {info['msg']}"""
    return message

def main():
    global last_otp_id
    login_to_seven1tel()
    time.sleep(2)

    first_otp = fetch_last_otp()
    if first_otp:
        last_otp_id = first_otp['otp'] + first_otp['time']
        bot.send_message(chat_id=GROUP_ID, text=format_message(first_otp, first_run=True))

    while True:
        try:
            otp = fetch_last_otp()
            if otp:
                otp_id = otp['otp'] + otp['time']
                if otp_id != last_otp_id:
                    last_otp_id = otp_id
                    bot.send_message(chat_id=GROUP_ID, text=format_message(otp))
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
