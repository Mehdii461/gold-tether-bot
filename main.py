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
        url = "https://www.tala.ir"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # یافتن قیمت طلا 18 عیار
        gold_td = soup.find("td", string=lambda text: text and "طلا 18" in text)
        gold_price = gold_td.find_next("td").text.strip() if gold_td else None

        # یافتن قیمت تتر
        tether_td = soup.find("td", string=lambda text: text and "تتر" in text)
        tether_price = tether_td.find_next("td").text.strip() if tether_td else None

        return gold_price, tether_price
    except Exception as e:
        print(f"خطا: {e}")
        return None, None

def send_price_to_telegram():
    now = datetime.datetime.now()
    if 8 <= now.hour < 22:
        gold_price, tether_price = fetch_prices()
        if gold_price and tether_price:
            message = f"💰 قیمت لحظه‌ای:\n\n🔸 طلا 18 عیار: {gold_price}\n🔹 تتر: {tether_price}"
        else:
            message = "❌ خطا در دریافت قیمت طلا یا تتر. لطفاً بعداً دوباره تلاش کنید."
        bot.send_message(chat_id=CHAT_ID, text=message)

# زمان‌بندی (هر ۳۰ دقیقه - برای تست موقتاً هر ۲ دقیقه)
schedule.every(2).minutes.do(send_price_to_telegram)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_schedule, daemon=True).start()

@app.route('/')
def index():
    return '💡 ربات قیمت طلا و تتر فعال است.'

@app.route('/send-now', methods=['GET'])
def send_now():
    send_price_to_telegram()
    return jsonify({'status': 'ok', 'message': 'قیمت به تلگرام ارسال شد.'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
