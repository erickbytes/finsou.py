# finsou.py

Try it after hours. This tool only currently works after the market has closed normal market hours.

The finsou.py CLI uses Python's html.parser + Beautiful Soup + regex to parse Yahoo stock price info. With it, you can:

- print market open, daily price action, market close and after hours summary for each stock
- export price summaries queried to csv
- download earnings reports and media with urllib

**Example Stock Summary**
```
python finsou.py -s "PATH"

PATH

MONSTER BREAKOUT!
Market Price $ Open: 12.87
Regular Market $ Close: 13.41
Daily % Change: +4.20%
Daily $ Change: +0.54
Post Market $ Close: 13.42
After Hours % Change: +0.07%
After Hours $ Change: +0.01
https://finance.yahoo.com/quote/PATH/
```
**Install Python Library Dependencies**
```
pip install beautifulsoup4
pip install pandas
pip install requests
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
python finsou.py -s "SPOT,DDOG,NET"

# Write price summaries to csv.
python finsou.py --stocks "TSLA,MSFT,AAPL" --csv "Prices Summary.csv"

# Read a list of stocks from a text file with one ticker on each line.
python finsou.py -s portfolio.txt -c "Portfolio Prices.csv"

# Get Coca-Cola prices and crawl investor relations website for media.
python finsou.py -s KO --research https://investors.coca-colacompany.com/
```
**Example portfolio.txt contents:**
```
META
PINS
SNAP
```
