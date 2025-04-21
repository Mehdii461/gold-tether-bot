import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
from telegram import Bot
import asyncio

# 🔐 اطلاعات ربات تلگرام
TOKEN = "7735514571:AAFwhrv2wb3GHkAZtI-BATc-D95G6hidcrc"
CHAT_ID = "593043026"
bot = Bot(token=TOKEN)

# 📊 دریافت قیمت تتر از نوبیتکس
def get_tether_price():
    try:
        url = "https://api.nobitex.ir/market/stats/"
        data = {"srcCurrency": "usdt", "dstCurrency": "rls"}
        response = requests.post(url, data=data)
        price = response.json()["stats"]["usdt-rls"]["latest"]
        return f"{int(price):,}"
    except Exception:
        return None

# 📊 دریافت قیمت طلای ۱۸ عیار از سایت میهن‌سیگنال
def get_gold_price():
    try:
        url = "https://mihansignal.com/gold/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        gold_price = soup.find("td", text="طلای 18 عیار").find_next("td").text.strip()
        return gold_price
    except Exception:
        return None

# ✉️ تابع ارسال پیام به تلگرام
async def send_price_to_telegram():
    now = datetime.datetime.now()
    if 8 <= now.hour < 22:
        gold = get_gold_price()
        tether = get_tether_price()

        if gold and tether:
            message = (
                "📢 *گزارش لحظه‌ای قیمت‌ها*\n"
                f"🕰 ساعت: {now.strftime('%H:%M')}  |  📅 تاریخ: {now.strftime('%Y/%m/%d')}\n\n"
                f"🏆 *طلای ۱۸ عیار:* `{gold}` تومان\n"
                f"💵 *تتر (USDT):* `{tether}` تومان\n\n"
                "📡 اطلاعات از میهن‌سیگنال و نوبیتکس\n"
                "♻️ بروزرسانی خودکار هر ۳۰ دقیقه"
            )
        else:
            message = "❌ خطا در دریافت قیمت طلا یا تتر. لطفاً بعداً دوباره تلاش کنید."

        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# 📅 زمان‌بندی ارسال پیام
def job():
    asyncio.run(send_price_to_telegram())

schedule.every(2).minutes.do(job)
job()  # اجرای فوری

while True:
    schedule.run_pending()
    time.sleep(1)
