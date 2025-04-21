import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import asyncio
from telegram import Bot

# 🔐 اطلاعات ربات تلگرام
TOKEN = "7735514571:AAFwhrv2wb3GHkAZtI-BATc-D95G6hidcrc"
CHAT_ID = "593043026"
bot = Bot(token=TOKEN)

# 📊 تابع دریافت قیمت طلا و تتر از tala.ir
def get_prices():
    try:
        url = "https://www.tala.ir/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"⛔️ خطا در دریافت سایت: کد وضعیت {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")

        gold_element = soup.find("li", {"id": "l-1"})
        tether_element = soup.find("li", {"id": "l-41"})

        if not gold_element or not tether_element:
            print("⛔️ المنت‌های قیمت طلا یا تتر پیدا نشدند.")
            return None, None

        gold_price = gold_element.find("span", {"class": "nl"})
        tether_price = tether_element.find("span", {"class": "nl"})

        if not gold_price or not tether_price:
            print("⛔️ قیمت داخل span پیدا نشد.")
            return None, None

        return gold_price.text.strip(), tether_price.text.strip()

    except Exception as e:
        print(f"❌ خطای کلی در get_prices: {e}")
        return None, None


# ✉️ تابع ارسال پیام تلگرام با فرمت شیک
async def send_price_to_telegram():
    now = datetime.datetime.now()
    if 8 <= now.hour < 22:
        gold, tether = get_prices()
        if gold and tether:
            message = (
                "📢 *گزارش لحظه‌ای قیمت‌ها*\n"
                f"🕰 ساعت: {now.strftime('%H:%M')}  |  📅 تاریخ: {now.strftime('%Y/%m/%d')}\n\n"
                f"🏆 *طلای ۱۸ عیار:* `{gold}` تومان\n"
                f"💵 *تتر (USDT):* `{tether}` تومان\n\n"
                "📡 اطلاعات دریافت‌شده از [tala.ir](https://www.tala.ir/)\n"
                "♻️ بروزرسانی خودکار هر ۳۰ دقیقه"
            )
        else:
            message = "❌ خطا در دریافت قیمت طلا یا تتر. لطفاً بعداً دوباره تلاش کنید."

        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# ⏰ زمان‌بندی هر ۳۰ دقیقه بین ساعت ۸ تا ۲۲
def job():
    asyncio.create_task(send_price_to_telegram())

schedule.every(2).minutes.do(job)

# 🚀 اجرای اولیه برای تست سریع
asyncio.run(send_price_to_telegram())

# 🔁 حلقه‌ی بررسی زمان‌بندی
while True:
    schedule.run_pending()
    time.sleep(1)
