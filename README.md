# finsou.py

finsou.py uses Python's html.parser + Beautiful Soup + regex to parse Yahoo price info.

- Parse Yahoo Finance HTML market close and after hours price info for a stock.
- Download Earnings Reports w/ pdf_miner.py
- default: prints summary
- has optional csv command line argument

**Example**
```
python finsou.py --stocks "TSLA,MSFT,AAPL" --csv "Prices Summary.csv"
```
