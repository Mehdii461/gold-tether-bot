from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
import datetime
from telegram import Bot

# تنظیمات تلگرام
TOKEN = "7735514571:AAFwhrv2wb3GHkAZtI-BATc-D95G6hidcrc"
CHAT_ID = "593043026"
bot = Bot(token=TOKEN)

app = Flask(__name__)

def fetch_prices():
    try:
        response = requests.get("https://www.tgju.org/")
        soup = BeautifulSoup(response.content, "html.parser")

        # استخراج قیمت طلای ۱۸ عیار
        gold_tag = soup.find("tr", id="geram18")
        gold_price = gold_tag.find("td", class_="info").text.strip() if gold_tag else None

        # استخراج قیمت تتر
        tether_tag = soup.find("tr", id="usdt")
        tether_price = tether_tag.find("td", class_="info").text.strip() if tether_tag else None

        return gold_price, tether_price
    except Exception as e:
        print(f"خطا در دریافت قیمت: {e}")
        return None, None

def send_price_to_telegram():
    now = datetime.datetime.now()
    if 8 <= now.hour < 22:
        gold_price, tether_price = fetch_prices()
        if gold_price and tether_price:
            message = f"💰 قیمت لحظه‌ای:\n\n🔸 طلای 18 عیار: {gold_price} تومان\n🔹 تتر: {tether_price} تومان"
        else:
            message = "❌ خطا در دریافت قیمت طلا یا تتر. لطفاً بعداً دوباره تلاش کنید."
        bot.send_message(chat_id=CHAT_ID, text=message)

# زمان‌بندی ارسال (برای تست فعلاً هر ۲ دقیقه)
schedule.every(2).minutes.do(send_price_to_telegram)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# اجرای زمان‌بندی در ترد جدا
threading.Thread(target=run_schedule, daemon=True).start()

# روت تستی
@app.route('/')
def index():
    return '💡 ربات قیمت طلا و تتر از tgju.org فعال است.'

# روت ارسال دستی
@app.route('/send-now', methods=['GET'])
def send_now():
    send_price_to_telegram()
    return jsonify({'status': 'ok', 'message': 'قیمت به تلگرام ارسال شد.'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
