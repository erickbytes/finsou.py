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

**CLI Options**

| Arg  | Alt. Arg  | Info     											`|
|-----:|-----------|------------------------------------------------------|
|   -s | --stocks  | comma delited string of stocks   					  |
|   -c | --csv     | write csv summary to given file, ex: "csv_name.csv"  |
|   -h | --help    | show help message and exit  						  |