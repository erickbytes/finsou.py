import argparse
import re
import time
import traceback
import urllib
import requests
from bs4 import BeautifulSoup
import pandas as pd
from decimal import Decimal
from rich import print as rprint


def earnings_date_fallback(table_tags):
    
    earnings_date_tag = [span for span in table_tags if ", " in str(span)]
    if "DIVIDEND" in str(earnings_date_tag[0]):
        return "N/A"
    span = '<td class="Ta(end) Fw(600) Lh(14px)" data-test="EARNINGS_DATE-value"><span>'
    earnings_date = (
        str(earnings_date_tag[0])
        .replace(span, "")
        .replace("</span> - <span>", " - ")
        .replace("</span></td>", "")
    )
    return earnings_date

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
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/43.0.845.0 Safari/534.1"
    headers = {
        "Cache-Control": "no-cache",
        "User-Agent": user_agent,
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
        if "+" in span.string or "-" in span.string or "0.0" in span.string
    ]
    daily_price_change = price_change_tags[0].replace("(", "").replace(")", "").strip()
    daily_pct_change = price_change_tags[1].replace("(", "").replace(")", "").strip()
    percent = (
        daily_pct_change.replace("-", "").replace("+", "").replace("%", "").strip()
    )
    info = list()
    # Display message if stock had a big daily move.
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
    # table_tags is a reference to the table of stats below the chart.
    table_tags = soup.find_all(class_=re.compile("Ta\(end\) Fw\(600\) Lh\(14px\)"))
    try:
        earnings_date_tags = [span for span in table_tags if ", " in str(span.string)]
        # This is a fallback for some stocks because beautiful soup doesn't work for tags with multiple spans.
        if "EARNING" not in str(earnings_date_tags[0]):
            earnings_date = earnings_date_fallback(table_tags)
        else:
            earnings_date = earnings_date_tags[0].string
    except TypeError:
        earnings_date = earnings_date_fallback(table_tags)
    except IndexError:
        earnings_date = "N/A"
    ex_dividend_date_tag = [span for span in table_tags if ", " in str(span.string)]
    if ex_dividend_date_tag and "DIVIDEND" in str(ex_dividend_date_tag[0]):
        ex_dividend_date = ex_dividend_date_tag[0].string                        
    else:
        try:
            ex_dividend_date = ex_dividend_date_tag[1].string
        except:
            ex_dividend_date = "N/A"
    alerts = "\n".join(info)
    summary = f"""{alerts}
    Market Price $ Open: {open_price}
    Regular Market $ Close: {mkt_close_price}
    Daily % Change: {daily_pct_change}
    Daily $ Change: {daily_price_change}
    -----------------------------
    After Hours % Change: {ah_pct_change}
    After Hours $ Change: {ah_price_change}
    Post Market $ Close: {post_mkt_price}
    -----------------------------
    Earnings Date: {earnings_date}
    Ex-Dividend Date: {ex_dividend_date}"""
    lines = [line.strip() for line in summary.splitlines() if not line.isspace()]
    summary = "\n".join(lines)
    rprint(f"[dark_cyan]{summary}[/dark_cyan]", sep="\n")
    return summary, ah_pct_change


def research(url):
    """Parse HTML with Python's html.parser and bs4.
    Select all nodes with an href value, print the urls and
    filter the file object urls with list comprehensions for download.

    The urllib urlretrieve function copies a network object to local file.
    The second argument, if present, specifies the file location to copy to.
    If filename is absent, the location will be a tempfile with a generated name.
    
    Note: this will only return files if the website lists them as links, 
    so it will not work on every stock.

    https://docs.python.org/3/library/urllib.request.html#urllib.request.urlretrieve
    """
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    urls = list(set([node.get("href") for node in soup.find_all(href=True)]))
    # Normalize trailing backslash in urls.
    urls = [url[0:-1] for url in urls if url.endswith("/") is True]
    rprint("\n[dark_cyan]INVESTOR LINKS\n--------------[/dark_cyan]")
    for url in sorted(set(urls)):
        rprint(f"[deep_sky_blue2]{url}[/deep_sky_blue2]")
    pdfs = [url for url in urls if url.endswith(".pdf")]
    csvs = [url for url in urls if url.endswith(".csv")]
    mp4s = [url for url in urls if url.endswith(".mp4")]
    docs = [url for url in urls if url.endswith(".docx")]
    xls = [url for url in urls if url.endswith(".xlsx")]
    objects = pdfs + csvs + mp4s + docs + xls
    if len(objects) == 0:
        rprint("[deep_sky_blue2]No media found to download.[/deep_sky_blue2]")
        return None
    for obj_url in objects:
        try:
            obj = obj_url.split("/")[-1]
            urllib.request.urlretrieve(url, filename=obj)
            rprint(f"[deep_sky_blue2]New network object saved: {obj}[/deep_sky_blue2]")
        except urllib.error.HTTPError:
            traceback.print_exc()
            rprint(f"[deep_sky_blue2]Forbidden to download file: {obj}[/deep_sky_blue2]")
        except ValueError:
            traceback.print_exc()
            rprint(f"[deep_sky_blue2]Failed due to invalid url: {obj}[/deep_sky_blue2]")
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
try:
    if ".txt" in args.stocks:
        with open(args.stocks, "r") as f:
            stocks = f.readlines()
        stocks = [line.strip() for line in stocks if line.isspace() is not True]
        rprint("[deep_sky_blue2]Loaded stocks from portfolio.txt.[/deep_sky_blue2]")
    else:
        stocks = args.stocks.split(",")
except TypeError:
    stocks = []
prices = list()
for stock in stocks:
    rprint(f"\n[deep_sky_blue2]------\n|{stock}|\n------[/deep_sky_blue2]")
    url = f"https://finance.yahoo.com/quote/{stock}/"
    summary, ah_pct_change = yahoo_finance_prices(url, stock)
    prices.append([stock, summary, url, ah_pct_change])
    rprint(f"[deep_sky_blue2]{url}[/deep_sky_blue2]")
    # Added time delay between each request to avoid too many hits too fast.
    time.sleep(2)
if args.csv:
    cols = ["Stock", "Price_Summary", "URL", "AH_%_Change"]
    stock_prices = pd.DataFrame(prices, columns=cols)
    stock_prices["Percent_Change"] = (
        stock_prices["AH_%_Change"]
        .str.replace("-", "")
        .str.replace("%", "")
        .str.replace("+", "")
        .apply(lambda num: Decimal(num))
    )
    moving_up = stock_prices[
        stock_prices["AH_%_Change"].str.contains("+", regex=False)
    ].sort_values(by="Percent_Change", ascending=False)
    flat = stock_prices[stock_prices["AH_%_Change"].str.contains("0.00", regex=False)]
    moving_down = stock_prices[
        stock_prices["AH_%_Change"].str.contains("-", regex=False)
    ].sort_values(by="Percent_Change", ascending=True)
    stock_prices = pd.concat([moving_up, flat, moving_down]).drop(
        "Percent_Change", axis=1
    )
    stock_prices.to_csv(args.csv, index=False)
if args.research:
    url = args.research
    research(url)
