import argparse
import time
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd


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
    mkt_close_price = mkt_close_price.replace(",", "")
    price_change_tags = soup.find_all(class_=re.compile("Fw\(500\)"))
    price_change_tags = [span.string for span in price_change_tags]
    daily_price_change = price_change_tags[2].replace("(", "").replace(")", "").strip()
    daily_pct_change = price_change_tags[3].replace("(", "").replace(")", "").strip()
    # Display message if stonk had a big daily move.
    percent = (
        daily_pct_change.replace("-", "")
        .replace("+", "")
        .replace("(", "")
        .replace(")", "")
        .replace("%", "")
        .strip()
    )
    info = list()
    if "+" in daily_pct_change and float(percent) > 4:
        info.append("MONSTER BREAKOUT DAY!")
    elif "-" in daily_pct_change and float(percent) > 4:
        info.append("SELL-OFF ALERT!")
    post_mkt_tags = soup.find_all(class_=re.compile("Mstart\(4px\)"))
    post_mkt_tags = [span.string for span in post_mkt_tags]
    ah_price_change = post_mkt_tags[0]
    ah_pct_change = post_mkt_tags[1].replace("(", "").replace(")", "").strip()
    ah_decimal_pct = float(
        ah_pct_change.replace("-", "").replace("%", "").replace("+", "")
    )
    # Display message if a stock shows activity after hours.
    if "+" in ah_pct_change and ah_decimal_pct > 3:
        info.append("AFTER HOURS MOVER!")
    elif "-" in ah_pct_change and ah_decimal_pct > 3:
        info.append("AFTER HOURS SELL-OFF!")
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
        open_price = float(mkt_close_price) - delta
    if "-" in daily_price_change:
        delta = float(daily_price_change.replace("-", "").strip())
        open_price = float(mkt_close_price) + delta
    try:
        open_price = round(open_price, 2)
    except UnboundLocalError:
        # Catch flat 0 change stocks. Attempting to round zero error.
        open_price = mkt_close_price
    alerts = "\n".join(info)
    summary = f"""{alerts}
    Market Price $ Open: {open_price}
    Regular Market $ Close: {mkt_close_price}
    Daily % Change: {daily_pct_change}
    Daily $ Change: {daily_price_change}
    Post Market $ Close: {post_mkt_price}
    After Hours % Change: {ah_pct_change}
    After Hours $ Change: {ah_price_change}"""
    lines = [line.strip() for line in summary.splitlines() if not line.isspace()]
    summary = "\n".join(lines)
    print(summary)
    return summary


parser = argparse.ArgumentParser(
    prog="finsou.py",
    description="Summarize prices from Yahoo website.",
    epilog="fin soup... yum yum yum yum",
)
parser.add_argument("-s", "--stocks", help="comma delited string of stocks or portfolio.txt")
parser.add_argument("-c", "--csv", help='"CSVNAME.csv"')
args = parser.parse_args()
if ".txt" in args.stocks:
    with open(args.stocks, "r") as f:
        stocks = f.readlines()
    stocks = [line.strip() for line in stocks if line.isspace() is not True]
    print("Loaded stocks from portfolio.txt.")
else:
    stocks = args.stocks.split(",")
prices = list()
for stock in stocks:
    print(f"\n{stock}\n")
    url = f"https://finance.yahoo.com/quote/{stock}/"
    try:
        summary = yahoo_finance_prices(url, stock)
    except IndexError:
        print(f"Error getting summary for {stock}")
        summary = "N/A"
    except AttributeError:
        print(f"Failed to get stock price for {stock}")
        continue
    prices.append([stock, summary, url])
    print(url)
    # Added time delay between each request to avoid too many hits too fast.
    time.sleep(2)
if args.csv:
    stock_prices = pd.DataFrame(prices, columns=["Stock", "Post_Market_Close", "URL"])
    stock_prices.to_csv(args.csv, index=False)
