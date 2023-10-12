import argparse
import re
import time
import traceback
import urllib
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from rich import print as rprint
from tqdm import tqdm
# lazy import only if csv argument given: import pandas as pd


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
    # user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.1 (KHTML, like Gecko) Chrome/43.0.845.0 Safari/534.1"
    user_agent = "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"
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
    post_mkt_tags = soup.find_all(class_=re.compile("Mstart\(4px\)"))
    post_mkt_tags = [span.string for span in post_mkt_tags]
    ah_price_change = post_mkt_tags[0]
    ah_pct_change = post_mkt_tags[1].replace("(", "").replace(")", "").strip()
    ah_decimal_pct = float(
        ah_pct_change.replace("-", "").replace("%", "").replace("+", "")
    )
    info = list()
    # Display message if stock had a big daily move + didn't lose gains after hours and vice versa.
    if (
        "+" in daily_pct_change
        and float(percent) > 4
        and float(daily_price_change) + float(ah_price_change) > 0
    ):
        info.append("(!) MONSTER BREAKOUT")
    elif (
        "+" in daily_pct_change
        and float(percent) >= 1
        and float(percent) <= 4
        and float(daily_price_change) + float(ah_price_change) > 0
    ):
        info.append("(+) SOLID GREEN DAY")
    elif (
        "-" in daily_pct_change
        and float(percent) > 4
        and float(daily_price_change) + float(ah_price_change) < 0
    ):
        info.append("(!) SELL-OFF ALERT")
    # Display message if a stock shows activity after hours.
    if "+" in ah_pct_change and ah_decimal_pct > 3:
        info.append("(+) AFTER HOURS MOVER")
    elif "-" in ah_pct_change and ah_decimal_pct > 3:
        info.append("(!) AFTER HOURS SELL-OFF")  
    notice = soup.find_all(
        class_=re.compile("LineClamp\(2\) Va\(m\) Tov\(e\)")
    )
    # Include special stock notices like dividend rate if shown.
    if notice:
        message = f"($) Announcement: {notice[0].string}"
        info.append(message)
    try:
        post_mkt_price_tags = soup.find_all(
            class_=re.compile("C\(\$primaryColor\) Fz\(24px\) Fw\(b\)")
        )
        post_mkt_price = post_mkt_price_tags[0].string
    except IndexError:
        message = f"[red]Failed to get stock report for {stock}. 'Over the counter' stocks do not list after hours prices so that may be why. Otherwise, try again after hours.[/red]"
        rprint(message)
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
        earnings_date_tag = [span for span in table_tags if "EARNING" in str(span)][0]
        if "N/A" in str(earnings_date_tag):
            earnings_date = "N/A"
        else:
            span = '<td class="Ta(end) Fw(600) Lh(14px)" data-test="EARNINGS_DATE-value"><span>'
            earnings_date = (
                str(earnings_date_tag)
                .replace(span, "")
                .replace("</span> - <span>", " - ")
                .replace("</span></td>", "")
            )
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
    if float(daily_price_change) + float(ah_price_change) < 0:
        rprint(f"[red]{summary}[/red]", sep="\n")
    else:
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
    spans = [span for span in soup.find_all("span") if "href" in str(span)]
    urls = list()
    for span in spans:
        rprint(f"[dark_cyan]{span}[/dark_cyan]")
        try:
            divs = span.find("div")
            for div in divs:
                rprint(f"[dark_cyan]{div}[/dark_cyan]")
                url = div.find("a").get("href")
                # Normalize trailing backslash in urls.
                if url.endswith("/"):
                    url = url[0:-1]
                urls.append(url)
            rprint(f"[deep_sky_blue2]{url}[/deep_sky_blue2]")
        except TypeError:
            continue
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
    for obj_url in tqdm(set(objects)):
        try:
            obj = obj_url.split("/")[-1]
            urllib.request.urlretrieve(url, filename=obj)
            rprint(f"[deep_sky_blue2]New network object saved: {obj}[/deep_sky_blue2]")
        except urllib.error.HTTPError:
            traceback.print_exc()
            rprint(
                f"[deep_sky_blue2]Forbidden to download file: {obj}[/deep_sky_blue2]"
            )
        except urllib.error.URLError:
            rprint(f"[deep_sky_blue2]Failed due to invalid url: {obj}[/deep_sky_blue2]")
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
        rprint(f"\n[deep_sky_blue2]Loaded stocks from {args.stocks}.[/deep_sky_blue2]\n")
    else:
        stocks = args.stocks.split(",")
except TypeError:
    stocks = []
prices = list()
stocks = [stock.upper().strip() for stock in stocks]
for stock in tqdm(stocks):
    # Dynamically size the box around ticker name based on its length.
    line = (len(stock) * "-") + "--"
    rprint(f"\n\n[steel_blue]{line}\n|{stock}|\n{line}[/steel_blue]")
    url = f"https://finance.yahoo.com/quote/{stock}/"
    try:
        summary, ah_pct_change = yahoo_finance_prices(url, stock)
        prices.append([stock, summary, url, ah_pct_change])
        rprint(f"[steel_blue]{url}[/steel_blue]\n")
        # Added time delay between each request to avoid too many hits too fast.
        if len(stocks) > 1:
            time.sleep(1)
    except IndexError:
        rprint(
            f"[red]Failed to get stock report for {stock}. 'Over the counter' stocks do not list after hours prices so that may be why. Otherwise, try again after hours.[/red]"
        )
        prices.append([stock, "N/A", url, "N/A"])
        continue
if args.csv:
    import pandas as pd
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
