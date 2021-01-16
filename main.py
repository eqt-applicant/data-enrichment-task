import requests
import pandas as pd
import logging as log
import sys

def scrape_funds():
    url = 'https://www.eqtgroup.com/About-EQT/Funds/Active-Funds/'
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    log.info(f'scraping {url}')
    r = requests.get(url, headers=header)
    dfs = pd.read_html(r.text)
    log.info(f'got {len(dfs)} data frames')
    if len(dfs) != 1:
        log.error('got wrong number of data frames')
        log.error(dfs)
        sys.exit(-1)
    return dfs[0]


def main():
    df = scrape_funds()
    print(df.head())

if __name__ == "__main__":
    main()
