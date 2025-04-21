from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
import datetime
import logging
from telegram import Bot

# تنظیمات تلگرام
TOKEN = "7735514571:AAFwhrv2wb3GHkAZtI-BATc-D95G6hidcrc"
CHAT_ID = "593043026"
bot = Bot(token=TOKEN)

app = Flask(__name__)

def fetch_prices():
    try:
        # دریافت قیمت طلا از tala.ir
        response_gold = requests.get("https://www.tala.ir/")
        soup_gold = BeautifulSoup(response_gold.content, "html.parser")
        gold_td = soup_gold.find("td", string="طلای 18 عیار")
        gold_price = gold_td.find_next("td").text.strip() if gold_td else None

        # دریافت قیمت تتر از arzdigital
        response_tether = requests.get("https://arzdigital.com/price/tether/")
        soup_tether = BeautifulSoup(response_tether.content, "html.parser")
        tether_div = soup_tether.find("div", class_="price")
        tether_price = tether_div.text.strip() if tether_div else None

        return gold_price, tether_price
    except Exception as e:
        print(f"خطا در دریافت قیمت: {e}")
        return None, None

def send_price_to_telegram():
    now = datetime.datetime.now()
    if 8 <= now.hour < 22:
        gold_price, tether_price = fetch_prices()
        if gold_price and tether_price:
            message = f"💰 قیمت لحظه‌ای:\n\n🔸 طلای 18 عیار: {gold_price}\n🔹 تتر: {tether_price}"
        else:
            message = "❌ خطا در دریافت قیمت طلا یا تتر. لطفاً بعداً دوباره تلاش کنید."
        bot.send_message(chat_id=CHAT_ID, text=message)

# زمان‌بندی هر ۳۰ دقیقه (برای تست موقتاً هر 2 دقیقه)
schedule.every(2).minutes.do(send_price_to_telegram)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# راه‌اندازی در یک ترد جدا
threading.Thread(target=run_schedule, daemon=True).start()

# روت اصلی برای تست زنده بودن سرور
@app.route('/')
def index():
    return '💡 ربات قیمت طلا و تتر فعال است.'

# روت برای ارسال دستی قیمت‌ها
@app.route('/send-now', methods=['GET'])
def send_now():
    send_price_to_telegram()
    return jsonify({'status': 'ok', 'message': 'قیمت به تلگرام ارسال شد.'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
