import time
import threading
from flask import Flask
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot

# توکن و چت آیدی تلگرام
TOKEN = "7735514571:AAFwhrv2wb3GHkAZtI-BATc-D95G6hidcrc"
CHAT_ID = "593043026"
bot = Bot(token=TOKEN)

# تابع برای دریافت قیمت طلا و تتر از سایت tala.ir
def get_prices():
    try:
        response = requests.get("https://www.tala.ir/")
        soup = BeautifulSoup(response.text, "html.parser")

        gold_tag = soup.find("li", {"id": "lSeque_0_0"})
        gold_price = gold_tag.find("span", class_="info").text.strip()

        tether_tag = soup.find("li", {"id": "lSeque_0_6"})
        tether_price = tether_tag.find("span", class_="info").text.strip()

        return gold_price, tether_price
    except Exception as e:
        return None, None

# تابعی برای ارسال پیام به تلگرام
def send_telegram_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print("Error sending message:", e)

# تابع اصلی برای اجرا در پس‌زمینه
def start_bot_loop():
    while True:
        now = datetime.now()
        current_hour = now.hour
        if 8 <= current_hour <= 22:
            gold, tether = get_prices()
            if gold and tether:
                msg = f"💰 قیمت طلا ۱۸ عیار: {gold} تومان\n💵 قیمت تتر: {tether} تومان\n🕒 {now.strftime('%H:%M')}"
                send_telegram_message(msg)
            else:
                print("❌ خطا در دریافت قیمت‌ها")
        else:
            print("⏰ خارج از ساعت مجاز ارسال پیام")
        time.sleep(1800)  # 30 دقیقه

# اجرای حلقه در ترد جدا
threading.Thread(target=start_bot_loop).start()

# وب سرور ساده برای فعال موندن Render
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is running..."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
