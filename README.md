# finsou.py

The finsou.py CLI uses Python's html.parser + Beautiful Soup + regex to parse Yahoo stock price info. With it, you can:

- see market open, daily price action, market close and after hours summary for each stock in your terminal
- see upcoming earnings date and ex-dividend date
- export price summaries queried to csv
- see a color coded report, green or red, report based on the sum of regular market and after hours price moves
- download earnings reports and media with urllib

After hours only. This tool only currently works after the market has closed normal market hours.

**Example Stock Summary**

`python finsou.py -s MSFT`

![stock summary example](stock-summary-example.png "Fetch a Stock Summary")

**Install Python Library Dependencies**
```
pip install beautifulsoup4
pip install pandas
pip install requests
pip install rich
pip install tqdm
```

**CLI Options**

| Arg  | Alt. Arg  | Description										                         |
|-----:|-----------|-----------------------------------------------------------------------------|
|   -s | --stocks  | accepts stock ticker, comma delimited string of stocks or portfolio.txt     |
|   -c | --csv     | write csv summary to given file, ex: "csv_name.csv"                         |
|   -r | --research| accepts investor resources url, downloads PDF, docx, csv, xlsx + mp3        |
|   -h | --help    | show help message and exit  						                         |

**Examples**
```
# Summarize a list of stocks.
python finsou.py -s SPOT,DDOG,NET

# Write price summaries to csv.
python finsou.py --stocks TSLA,MSFT,AAPL --csv "Prices Summary.csv"

# Read a list of stocks from a text file with one ticker on each line.
python finsou.py -s portfolio.txt -c "Portfolio Prices.csv"

# Note: this is experimental and results will vary.
python finsou.py -s GRAB -r https://investors.grab.com/events-and-presentations
# Currently needs to be modified depending on the HTML structure of the page. URLs are typically buried in nested span and div tags.
```

**Example portfolio.txt contents:**
```
META
PINS
SNAP
```
