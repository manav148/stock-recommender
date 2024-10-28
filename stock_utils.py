import yfinance as yf
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import random

def delay():
    time.sleep(random.uniform(1, 3))

def get_stock_price(ticker):
    delay()
    if "." in ticker:
        ticker = ticker.split(".")[0]
    print("Ticker: is " + ticker)
    stock = yf.Ticker(ticker.strip())
    df = stock.history(period="1y")
    df = df[["Close", "Volume"]]
    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
    df.index.name = "Date"
    return df.to_string()

def google_query(search_term):
    if "news" not in search_term:
        search_term = search_term + " stock news"
    url = f"https://www.google.com/search?q={search_term}"
    url = re.sub(r"\s", "+", url)
    return url

def get_recent_stock_news(company_name):
    delay()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    g_query = google_query(company_name)
    try:
        res = requests.get(g_query, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching news: {str(e)}"

    soup = BeautifulSoup(res.text, "html.parser")
    news = []
    for n in soup.find_all("div", "n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.text)
    for n in soup.find_all("div", "IJl0Z"):
        news.append(n.text)

    if len(news) > 6:
        news = news[:4]
    
    news_string = ""
    for i, n in enumerate(news):
        news_string += f"{i+1}. {n}\n"
    top5_news = "Recent News:\n\n" + news_string
    
    return top5_news

def get_financial_statements(ticker):
    delay()
    if "." in ticker:
        ticker = ticker.split(".")[0]
    else:
        ticker = ticker
    company = yf.Ticker(ticker.strip())
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1] > 3:
        balance_sheet = balance_sheet.iloc[:, :3]
    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    return balance_sheet