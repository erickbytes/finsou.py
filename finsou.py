import argparse
import re
import time
import traceback
import urllib
import requests
from bs4 import BeautifulSoup
import pandas as pd


def yahoo_finance_prices(url, stock):
    """Parse Yahoo Finance HTML price and after hours price info.
    Use Beautiful Soup + regex compile to select span tags with price values.

    The re.compile function accepts a str, css class str to match if contained in any tag.
    4 regex matches are used to get HTML tags with ( ) $ - escaped with \ in each.
    returns summary, str containing regular hours stock market + after hours prices

    Beautiful Soup Docs:
    https://beautiful-soup-4.readthedocs.io/en/latest/#searching-by-css-class
    https://docs.python.org/3/library/re.html#re.compile
    """
    # TODO: get after hours price in real time during after hour session
    headers = {
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/43.0.845.0 Safari/534.1",
    }
    page = requests.get(url, headers=headers).text
    soup = BeautifulSoup(page, "html.parser")
    price_tags = soup.find_all(
        class_=re.compile("Fw\(b\) Fz\(36px\) Mb\(\-4px\) D\(ib\)")
    )
    mkt_close_price = price_tags[0].string.replace(",", "")
    price_change_tags = soup.find_all(class_=re.compile("Fw\(500\)"))
    price_change_tags = [span for span in price_change_tags if span.string is not None]
    price_change_tags = [
        span.string
        for span in price_change_tags
        if "+" in span.string or "-" in span.string
    ]
    daily_price_change = price_change_tags[0].replace("(", "").replace(")", "").strip()
    daily_pct_change = price_change_tags[1].replace("(", "").replace(")", "").strip()
    percent = (
        daily_pct_change.replace("-", "").replace("+", "").replace("%", "").strip()
    )
    info = list()
    # Display message if stpck had a big daily move.
    if "+" in daily_pct_change and float(percent) > 4:
        info.append("MONSTER BREAKOUT!")
    elif "+" in daily_pct_change and float(percent) >= 1 and float(percent) <= 4:
        info.append("SOLID GREEN DAY!")
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


def research(url):
    """Parse HTML with Python's html.parser and bs4.
    Select all nodes with an href value, print the urls and
    filter the file object urls with list comprehensions for download.

    The urllib urlretrieve function copies a network object to local file.
    The second argument, if present, specifies the file location to copy to.
    If filename is absent, the location will be a tempfile with a generated name.

    https://docs.python.org/3/library/urllib.request.html#urllib.request.urlretrieve
    """
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    urls = list(set([node.get("href") for node in soup.find_all(href=True)]))
    # Normalize trailing backslash in urls.
    urls = [
        f"{url}/" for url in urls if url.endswith("/") is not True
    ]
    print("\nINVESTOR LINKS\n--------------")
    for url in sorted(urls):
        print(url)
    pdfs = [url for url in urls if url.endswith(".pdf")]
    csvs = [url for url in urls if url.endswith(".csv")]
    mp4s = [url for url in urls if url.endswith(".mp4")]
    docs = [url for url in urls if url.endswith(".docx")]
    xls = [url for url in urls if url.endswith(".xlsx")]
    objects = pdfs + csvs + mp4s + docs + xls
    if len(objects) == 0:
        print("No media found to download.")
        return None
    for obj_url in objects:
        try:
            obj = obj_url.split("/")[-1]
            urllib.request.urlretrieve(url, filename=obj)
            print(f"New network object saved: {obj}")
        except urllib.error.HTTPError:
            traceback.print_exc()
            print(f"Forbidden to download file: {obj}")
        except ValueError:
            traceback.print_exc()
            print(f"Failed due to invalid url: {obj}")
        return None


parser = argparse.ArgumentParser(
    prog="finsou.py",
    description="Beautiful Financial Soup",
    epilog="fin soup... yum yum yum yum",
)
parser.add_argument("-s", "--stocks", help="comma sep. stocks or portfolio.txt")
parser.add_argument("-c", "--csv", help='set csv export with "your_csv.csv"')
parser.add_argument("-r", "--research", help="accepts investor relations website url")
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
    stock_prices = pd.DataFrame(prices, columns=["Stock", "Price_Summary", "URL"])
    stock_prices.to_csv(args.csv, index=False)
if args.research:
    url = args.research
    research(url)
