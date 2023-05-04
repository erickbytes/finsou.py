import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def yahoo_finance_prices(url, stock):
    """Parse Yahoo Finance HTML price and after hours price info.
    Use Beautiful Soup + regex compile to select span tags with price values.
    
    The re.compile function accepts a str, class value to match if contained in any tag.
    4 regex matches are used to get HTML tags and ( ) $ - are escaped with \
    returns summary, str containing regular hours stock market + after hours prices
    
    Beautiful Soup Docs:
    https://beautiful-soup-4.readthedocs.io/en/latest/#searching-by-css-class
    """
    # TODO: get after hours price in real time during after hour session
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    price_tags = soup.find_all(
        class_=re.compile("Fw\(b\) Fz\(36px\) Mb\(\-4px\) D\(ib\)")
    )
    mkt_close_price = price_tags[0].string
    price_change_tags = soup.find_all(class_=re.compile("Fw\(500\)"))
    price_change_tags = [span.string for span in price_change_tags]
    daily_price_change = price_change_tags[2]
    daily_pct_change = price_change_tags[3]
    post_mkt_tags = soup.find_all(class_=re.compile("Mstart\(4px\)"))
    post_mkt_tags = [span.string for span in post_mkt_tags]
    ah_price_change = post_mkt_tags[0]
    ah_pct_change = post_mkt_tags[1]
    try:
        post_mkt_price_tags = soup.find_all(
            class_=re.compile("C\(\$primaryColor\) Fz\(24px\) Fw\(b\)")
        )
        post_mkt_price = post_mkt_price_tags[0].string
    except IndexError:
        print("Market still in progress, check back later for after hours prices.")
        post_mkt_price = "N/A"
    # Calculate market open price from day change and close price.
    if "+" in daily_price_change:
        delta = float(daily_price_change.replace("+", "").strip())
        # open_price = sum([mkt_close_price, daily_price_change])
        print((mkt_close_price, delta))
        open_price = float(mkt_close_price) - delta
    if "-" in daily_price_change:
        delta = float(daily_price_change.replace("-", "").strip())
        open_price = float(mkt_close_price) + delta
    summary = f"""Market Price $ Open: {round(open_price, 2)}
    Regular Market $ Close: {mkt_close_price}
    Daily % Change: {daily_pct_change}
    Daily $ Change: {daily_price_change}
    Post Market $ Close: {post_mkt_price}
    After Hours % Change: {ah_pct_change}
    After Hours $ Change: {ah_price_change}"""
    lines = [line.strip() for line in summary.splitlines() if not line.isspace()]
    summary = "\n".join(lines)
    print(summary)
    time.sleep(2)  # Added time delay between each request.
    return summary


stocks = [
    "OKTA",
    "NVDA",
    "TSLA",
    "MSFT",
    "NKE",
]
prices = list()
for stock in stocks:
    print(stock)
    url = f"https://finance.yahoo.com/quote/{stock}/"
    try:
        summary = yahoo_finance_prices(url, stock)
    except IndexError:
        print(f"Error getting summary for {stock}")
        summary = "N/A"
    prices.append([stock, summary, url])
stock_prices = pd.DataFrame(prices, columns=["Stock", "Post_Market_Close", "URL"])
stock_prices.to_csv("Yahoo Stock Prices.csv", index=False)
