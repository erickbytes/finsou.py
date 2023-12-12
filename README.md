# finsou.py

The finsou.py CLI uses Python's [html.parser](https://docs.python.org/3/library/html.parser.html), [Beautiful Soup](https://pypi.org/project/beautifulsoup4/), [regex](https://docs.python.org/3/library/re.html) and [yfinance](https://pypi.org/project/yfinance/) to parse Yahoo stock price info. Available to use daily after 3 PM Central Standard Time, or anytime when the regular US stock market is closed.

**Example Stock Summary**

`python finsou.py -s PINS`

![stock summary example](stock-summary-example.png "Fetch a Stock Summary")

See stock price reports in your terminal:
- market open, daily price action, market close and after hours summary for each stock in your terminal
- color coded report, green or red, based on the sum of regular market + after hours price moves
- upcoming earnings date and ex-dividend date
- PEG ratio and its implications for stock's current valuation
- export price summaries queried to csv
- download earnings reports and media with urllib

**Caveats**
- After hours prices for "over the counter" (OTC) traded stocks are not listed on Yahoo.
- Fetching a stock report takes about 1-3 seconds on a fast, stable Wi-Fi connection.
- Media is only downloaded if the investor website returns an HTML page. Sometimes, websites return Javascript. When this is the case, a browser or Selenium is required to render the HTML.

**Install Python Library Dependencies**
```
pip install beautifulsoup4
pip install pandas
pip install requests
pip install rich
pip install tqdm
pip install yfinance
```

**CLI Options**

| Arg  | Alt. Arg  | Description										                         |
|-----:|-----------|-----------------------------------------------------------------------------|
|   -s | --stocks  | accepts stock ticker, comma delimited string of stocks or portfolio.txt     |
|   -c | --csv     | write csv summary to given file, ex: "csv_name.csv"                         |
|   -f | --fast| pass 1 to this flag to disable yfinance PEG lookup       |
|   -r | --research| accepts investor resources url, downloads PDF, docx, csv, xlsx + mp3        |
|   -h | --help    | show help message and exit  						                         |

**Examples**
```
# Summarize a list of stocks.
python finsou.py -s SPOT,DDOG,NET

# Write price summaries to csv.
python finsou.py --stocks TSLA,MSFT,AAPL --csv "Prices Summary.csv"

# Read a list of stocks from a text file with one ticker on each line.
python finsou.py -s portfolio.txt -c "Portfolio Prices.csv" --fast 1

# Scan investor relations site and download all media from urls.
python finsou.py -s KO -r https://investors.coca-colacompany.com/financial-information/financial-results
```

**Example portfolio.txt contents:**
```
META
PINS
SNAP
```

![media download example](media-download-example.png "Download Financial Reports and Media")

**Interpreting PEG Ratio**
- greater than 1 = Overvalued
- 0 to near 1 = Undervalued
- negative = Caution

Understanding PEG Ratio, [Bing](https://bing.com):
> "The PEG ratio is a financial metric that helps investors determine the value of a stock while factoring in the company’s expected earnings growth. A PEG ratio of 1 is considered to be a good indicator of a stock’s true value and may indicate that a company is relatively undervalued.
In general, a PEG ratio of less than 1 is considered to be an indicator of a stock’s true value and may indicate that a company is relatively undervalued. Conversely, a PEG ratio of greater than 1 is generally considered unfavorable, suggesting a stock is overvalued.
A negative PEG ratio can mean one of two things:
either the P/E ratio of the stock is negative, meaning that the company is losing money,
or
the estimated growth rate for future earnings is negative, indicating that
the earnings of the company are expected to decrease in the future.
If the PEG ratio is negative because of a negative P/E ratio, it is generally
considered to be a bad sign. Negative earnings are an extremely risky place for
a business to be in, and the possible gains that could be made by gambling
on a comeback story usually aren’t enough to justify the enormous risk you
take by investing in this kind of situation.However, if a company’s growth is negative, it could be something you want to avoid, but it is not necessarily a bad sign.
The implications for a negative PEG ratio depend on the reason behind the negative PEG ratio."

To learn more details about this project, read my blog post [here](https://lofipython.com/making-a-yahoo-stock-price-summary-cli-with-python).
