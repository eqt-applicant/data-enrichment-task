import requests
import pandas as pd
import logging as log
import sys
from bs4 import BeautifulSoup


def setup_logging():
    root = log.getLogger()
    root.setLevel(log.DEBUG)

    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(log.DEBUG)
    formatter = log.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def scrape(url):
    http_headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    log.info(f'scraping {url}')
    r = requests.get(url, headers=http_headers)
    return r.text


def assert_one_dataframe(dfs):
    if len(dfs) != 1:
        log.error('got wrong number of data frames')
        log.error(dfs)
        sys.exit(-1)


def scrape_funds():
    text = scrape('https://www.eqtgroup.com/About-EQT/Funds/Active-Funds/')
    soup = BeautifulSoup(text)
    hrefs = [
        f"https://www.eqtgroup.com{link.get('href')}"
        for link in soup.table.find_all('a')
    ]

    dfs = pd.read_html(text)
    assert_one_dataframe(dfs)

    df = dfs[0]
    df.rename(columns=str.lower, inplace=True)
    df['hrefs'] = hrefs

    return df


def extract_company_hrefs(soup):
    "Extracts hrefs from the first table column (first found <a> tag)"
    hrefs = []
    rows = soup.table.tbody.find_all('tr')
    for row in rows:
        href_suffix = row.find('a').get('href')
        href = f"https://www.eqtgroup.com{href_suffix}"
        hrefs.append(href)
    return hrefs


def scrape_current_portfolio():
    text = scrape('https://www.eqtgroup.com/Investments/Current-Portfolio/')
    soup = BeautifulSoup(text)
    hrefs = extract_company_hrefs(soup)

    dfs = pd.read_html(text)
    assert_one_dataframe(dfs)

    df = dfs[0]

    df.rename(columns=str.lower, inplace=True)
    df.rename(columns={"sdg *": "sdg"}, inplace=True)

    df['hrefs'] = hrefs

    return df


def scrape_divested():
    text = scrape('https://www.eqtgroup.com/Investments/Divestments/')
    soup = BeautifulSoup(text)
    hrefs = extract_company_hrefs(soup)
    dfs = pd.read_html(text)
    assert_one_dataframe(dfs)

    df = dfs[0]
    df.rename(columns=str.lower, inplace=True)
    df.rename(columns={"sdg *": "sdg"}, inplace=True)

    df['hrefs'] = hrefs

    return df


def scrape_company(url):
    text = scrape(url)


def save_ndjson(filename, df):
    log.info(f'saving df with shape {df.shape} to {filename}.')
    with open(filename, 'w') as f:
        for row in df.iterrows():
            row[1].to_json(f)
            f.write('\n')


def main():
    setup_logging()
    save = True

    funds = scrape_funds()
    current_portfolio = scrape_current_portfolio()
    divested = scrape_divested()

    companies = current_portfolio.merge(divested, how='outer')
    companies.rename({'hrefs': 'href'})

    acumatica = companies.head(1).iloc[0]['hrefs']

    import ipdb
    ipdb.set_trace()

    if save:
        save_ndjson('data/raw/funds.ndjson', funds)
        save_ndjson('data/raw/companies.ndjson', companies)


if __name__ == "__main__":
    main()
