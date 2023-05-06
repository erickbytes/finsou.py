# finsou.py

finsou.py uses Python's html.parser + Beautiful Soup + regex to parse Yahoo price info.

- parse Yahoo Finance HTML market close and after hours stock prices
- download earnings reports w/ pdf_miner.py
- default: prints summary
- has optional csv command line argument

**Examples**
```
# Summarize a list of stocks.
python finsou.py -s "SPOT,GOOG,NET"

# Write price summaries to csv.
python finsou.py --stocks "TSLA,MSFT,AAPL" --csv "Prices Summary.csv"

# Read a list of stocks from a text file with one ticker on each line.
python finsou.py -s portfolio.txt -c "Portfolio Prices.csv"
```
Example portfolio.txt contents:
```
TSLA
MSFT
AAPL
```

**CLI Options**

| Arg  | Alt. Arg  | Info     											  |
|-----:|-----------|------------------------------------------------------|
|   -s | --stocks  | comma delited string of stocks   					  |
|   -c | --csv     | write csv summary to given file, ex: "csv_name.csv"  |
|   -h | --help    | show help message and exit  						  |