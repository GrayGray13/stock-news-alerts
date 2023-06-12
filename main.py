import credentials
import requests
from datetime import date, timedelta
from twilio.rest import Client

AV_API_KEY = credentials.ALPHA_VANTAGE_API_KEY
NEWS_API_KEY = credentials.NEWS_API_KEY
TWILIO_ACC_SID = credentials.TWILIO_ACC_SID
TWILIO_AUTH_TOKEN = credentials.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUM = credentials.TWILIO_PHONE_NUM
PERSONAL_PHONE_NUM = credentials.PERSONAL_PHONE_NUM
STOCK = "TSLA"
COMPANY_NAME = "Tesla"
STOCK_UP = "🔺"
STOCK_DOWN = "🔻"


def check_stock_change():
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': STOCK,
        'apikey': AV_API_KEY
    }
    response = requests.get(url, params)
    response.raise_for_status()
    stock_data = response.json()

    today_date = date.today()
    yesterday_date = today_date - timedelta(days=1)
    # Checks if yesterday was a weekend
    while 4 < yesterday_date.weekday() < 7:
        yesterday_date -= timedelta(days=1)
    two_days_ago_date = yesterday_date - timedelta(days=1)

    yesterday = stock_data['Time Series (Daily)'][str(yesterday_date)]
    day_before_yesterday = stock_data['Time Series (Daily)'][str(two_days_ago_date)]
    open_price = float(yesterday['1. open'])
    close_price = float(day_before_yesterday['4. close'])
    percent_change = int(((open_price - close_price) / close_price) * 100)

    if abs(percent_change) >= 5:
        if percent_change > 0:
            get_news(STOCK_UP)
        else:
            get_news(STOCK_DOWN)


def get_news(emoji):
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "q": COMPANY_NAME,
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params)
    response.raise_for_status()
    news_data = response.json()

    if news_data['totalResults'] > 3:
        news_articles = news_data['articles'][:3]
    elif news_data['totalResults'] > 0:
        news_articles = news_data['articles']
    else:
        print(f"No Articles Found For '{COMPANY_NAME}'")
        return

    send_message(news_articles, emoji)


def send_message(articles, emoji):
    message_body = f"{STOCK}: {emoji}\n"
    for article in articles:
        message_body += f"Headline: {article['title']}\nBrief: {article['description']}\n"
    client = Client(TWILIO_ACC_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_body,
        from_=TWILIO_PHONE_NUM,
        to=PERSONAL_PHONE_NUM
    )


check_stock_change()
