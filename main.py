import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import telegram

# تنظیمات ربات تلگرام
bot_token = '7735514571:AAFwhrv2wb3GHkAZtI-BATc-D95G6hidcrc'
chat_id = '593043026'
bot = telegram.Bot(token=bot_token)

def get_prices():
    url = 'https://www.tala.ir/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # استخراج قیمت طلا ۱۸ عیار
    gold_price = soup.find('td', text='هر گرم طلای ۱۸ عیار').find_next_sibling('td').text.strip()

    # استخراج قیمت تتر
    tether_price = soup.find('td', text='تتر').find_next_sibling('td').text.strip()

    return gold_price, tether_price

def send_prices():
    gold_price, tether_price = get_prices()
    message = f"قیمت طلا ۱۸ عیار: {gold_price}\nقیمت تتر: {tether_price}"
    bot.send_message(chat_id=chat_id, text=message)

while True:
    current_hour = datetime.now().hour
    if 8 <= current_hour < 22:
        send_prices()
    time.sleep(1800)  # ۳۰ دقیقه
