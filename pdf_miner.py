import traceback
import pprint
import os
import requests
from bs4 import BeautifulSoup
import urllib.request
from tika import parser
from http import client


def extract_links(url):
    """Parse HTML with Python's html.parser and bs4.
    Select all nodes with an href value and
    filter the PDF urls with list comprehensions.
    """
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    urls = [node.get("href") for node in soup.find_all(href=True)]
    return list(set(urls))


def download(obj_url, path):
    """The urllib urlretrieve function copies a network object to local file.
    The second argument, if present, specifies the file location to copy to.
    If filename is absent, the location will be a tempfile with a generated name.
    https://docs.python.org/3/library/urllib.request.html#urllib.request.urlretrieve
    """
    try:
        obj = obj_url.split("/")[-1]
        urllib.request.urlretrieve(url, filename=f"{path}/{obj}")
        print(f"New network object saved: {obj}")
    except urllib.error.HTTPError:
        traceback.print_exc()
        print(f"Forbidden to download file: {obj}")
    except ValueError:
        traceback.print_exc()
        print(f"Failed due to invalid url: {obj}")
    return None


def parse_pdf(pdf):
    """Accepts PDF path, returns PDF text."""
    raw = parser.from_file(pdf)
    return raw["content"]


def prefix_domain(stock, urls):
    if stock == "TM":
        urls = [f"https://global.toyota{url}" for url in urls]
    if stock == "GOOG":
        urls = [f"https://abc.xyz{url}" for url in urls]
    if stock == "LCID":
        urls = [f"https://ir.lucidmotors.com{url}" for url in urls]
    return urls


investor_urls = {
    "SNOW": "https://investors.snowflake.com/financials/annual-reports-and-proxies/default.aspx",
    "TSLA": "https://ir.tesla.com/#quarterly-disclosure",
    "MSFT": "https://www.microsoft.com/en-us/investor",
    "NKE": "https://investors.nike.com/investors/news-events-and-reports/?toggle=earnings",
    "NET": "https://cloudflare.net/events-and-presentations/default.aspx",
    "NVDA": "https://investor.nvidia.com/financial-info/annual-reports-and-proxies/default.aspx",
    "RBLX": "https://ir.roblox.com/events-and-presentations/default.aspx",
    "ETSY": "https://investors.etsy.com/financial-info/annual-reports-and-proxies/default.aspx",
    "DIS": "https://thewaltdisneycompany.com/investor-relations/",
    "SPOT": "https://investors.spotify.com/financials/default.aspx",
    "DDOG": "https://investors.datadoghq.com/static-files",
    "PYPL": "https://investor.pypl.com/news-and-events/events/default.aspx",
    "Z": "https://investors.zillowgroup.com/investors/financials/quarterly-results/default.aspx",
    "F": "https://shareholder.ford.com/Investors/financials/default.aspx",
    "SQ": "https://investors.block.xyz/financials/annual-results/default.aspx",
    "PINS": "https://investor.pinterestinc.com/financial-results/quarterly-results/default.aspx",
    "TM": "https://global.toyota/en/ir/financial-results/?padid=ag478_from_right_side",
    "NRDS": "https://investors.nerdwallet.com/financial-information/quarterly-results",
    "GOOG": "https://abc.xyz/investor/",
    "MNMD": "https://mindmed.co/investor-resources/#downloads",
    "LCID": "https://ir.lucidmotors.com/events-and-presentations/presentations",
    "RUN": "https://investors.sunrun.com/",
    "OKTA": "https://investor.okta.com/financial-information/annual-reports",
    "YETI": "https://investors.yeti.com/financials/quarterly-results/default.aspx",
    "COUR": "https://investor.coursera.com/financials/quarterly-results/default.aspx",
    "DOCN": "https://www.q4inc.com/Powered-by-Q4/",
    "CGC": "https://www.canopygrowth.com/investors/earnings/",
    "PTLO": "https://investors.portillos.com/financial-information/annual-reports",
    "AEO": "https://investors.ae.com/events-and-presentations/default.aspx",
    "AAPL": "https://investor.apple.com/investor-relations/default.aspx",
    "ROKU": "https://www.roku.com/investor",
    "TRIP": "https://www.tripadvisor.com/SiteIndex",
    "NTDOY": "https://www.nintendo.co.jp/ir/en/finance/highlight/index.html",
    "SPCE": "https://investors.virgingalactic.com/financials/Annual-Reports-and-Proxy-Forms/default.aspx",
    "NFLX": "https://ir.netflix.net/financials/quarterly-earnings/default.aspx",
    "HD": "https://ir.homedepot.com/investor-resources/investor-documents",
    "SOFI": "https://investors.sofi.com/news/default.aspx",
    "KO": "https://investors.coca-colacompany.com/",
    "BROS": "https://investors.dutchbros.com/events-and-presentations/presentations/default.aspx",
    "GRAB": "https://investors.grab.com//events/event-details/crowdstrike-fiscal-second-quarter-2023-results-conference-call",
    "CRLB": "https://investors.crescolabs.com/investors/financial-info/financial-reports/default.aspx",
    "API": "https://investor.agora.io/news-events/event-calendar",
    "CRWD": "https://ir.crowdstrike.com/financial-information/sec-filings?field_nir_sec_form_group_target_id%5B%5D=471&field_nir_sec_date_filed_value=#views-exposed-form-widget-sec-filings-table",
    "FSLR": "https://investor.firstsolar.com/financials/annual-reports/default.aspx",
    "SHOP": "https://investors.shopify.com/resources/default.aspx",
    "EA": "https://ir.ea.com/financial-information/quarterly-results/default.aspx",
    "SCHW": "https://www.aboutschwab.com/annual-report",
    "ARKG": "https://ark-funds.com/download-fund-materials/",
    "FUBO": "https://ir.fubo.tv/financials/annual-reports/default.aspx",
    "NCLH": "https://www.nclhltd.com/investors/financial-information/financial-results",
    "WEN": "https://www.irwendys.com/financials/quarterly-results/default.aspx",
    "SCHB": "https://www.schwabassetmanagement.com/products/schb",
    "PATH": "",
    "KR": "",
}
input(list(investor_urls.keys()))
client.HTTPConnection.debuglevel = 1
pprint.pprint(investor_urls, sort_dicts=True)
stock = input("Enter stock symbol:\n")
path = f"/home/erick/Desktop/Projects/scripts/pdf_scripts/pdfs/{stock}"
os.makedirs(path, exist_ok=True)
url = investor_urls.get(stock, "N/A")
urls = extract_links(url)
for url in urls:
    print(url)
pdfs = [url for url in urls if url.endswith(".pdf")]
csvs = [url for url in urls if url.endswith(".csv")]
mp4s = [url for url in urls if url.endswith(".mp4")]
docs = [url for url in urls if url.endswith(".docx")]
xls = [url for url in urls if url.endswith(".xlsx")]
statics = [url for url in urls if "static-file" in url]
objects = pdfs + csvs + mp4s + docs + xls + statics
for obj_url in objects:
    # Some websites use relative href routes that need domain added.
    #if obj_url.startswith("//"):
    #    obj_url = obj_url.replace("//", "https://")
    download(obj_url, path)

"""Ways Websites obscure urls:
- Encrypt files so that the extension is obsured from the url.
  It appears to be some sort of hashing system you'd need to crack.
- nesting a tags within span and div tags
- hosting reports on other websites
- templating variables used instead of hard-coded urls
"""
