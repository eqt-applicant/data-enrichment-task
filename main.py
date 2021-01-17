import requests
import pandas as pd
import logging as log
import sys
from bs4 import BeautifulSoup
import re


def setup_logging():
    root = log.getLogger()
    root.setLevel(log.INFO)

    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(log.DEBUG)
    formatter = log.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def scrape(url):
    http_headers = {
        "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like " +
        "Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With":
        "XMLHttpRequest"
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
    soup = BeautifulSoup(text, features="lxml")
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
    """Extracts hrefs from the first found <a> tag per row (usually the first
    column).
    """
    hrefs = []
    rows = soup.table.tbody.find_all('tr')
    for row in rows:
        href_suffix = row.find('a').get('href')
        href = f"https://www.eqtgroup.com{href_suffix}"
        hrefs.append(href)
    return hrefs


def scrape_current_portfolio():
    text = scrape('https://www.eqtgroup.com/Investments/Current-Portfolio/')
    soup = BeautifulSoup(text, features="lxml")
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
    soup = BeautifulSoup(text, features="lxml")
    hrefs = extract_company_hrefs(soup)
    dfs = pd.read_html(text)
    assert_one_dataframe(dfs)

    df = dfs[0]
    df.rename(columns=str.lower, inplace=True)
    df.rename(columns={"sdg *": "sdg"}, inplace=True)

    df['hrefs'] = hrefs

    return df


def extract_sdgs(soup):
    sdgs = []
    for img in soup.find("div", class_="main-contentarea").find_all("img"):
        img_src = img.attrs.get("src")
        try:
            m = re.search("e_print_([0-9]+).jpg", img_src)
        except AttributeError:
            continue  # img_src did not match an SDG src
        sdgs.append(m.group(1))
    return sdgs


def extract_advisor(soup):
    advisor_span = soup.find("span", class_="advisorname-section")
    advisor_link = advisor_span.find("a")
    if advisor_link:
        href = advisor_link.attrs.get("href")
        return {
            "advisor_href": f"http://www.eqtgroup.com{href}",
            "advisorname": advisor_link.string
        }


def scrape_company(url):
    log.info(f"scraping company url: {url}")
    text = scrape(url)
    soup = BeautifulSoup(text, features="lxml")

    advisor = extract_advisor(soup)
    sdgs = extract_sdgs(soup)

    description = soup.find("div", class_="main-body").get_text()
    description_links = [
        link.attrs.get("href")
        for link in soup.find("div", class_="main-body").find_all("a")
    ]
    board_of_directors = [
        div.get_text().strip().split("\n")
        for div in soup.find("div", class_="board-of-directors-module").
        find_all("div", class_="fact-row")
    ]

    management = [
        div.get_text().strip().split("\n")
        for div in soup.find("div", class_="management-module").find_all(
            "div", class_="fact-row")
    ]
    return {
        "sdgs": sdgs,
        "advisor": advisor,
        "description": description,
        "description_links": description_links,
        "board_of_directors": board_of_directors,
        "management": management
    }


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
    ndivested = scrape_divested()

    companies = current_portfolio.merge(divested, how='outer')
    companies.rename({'hrefs': 'href'})

    from pprint import pprint
    pprint(dict)

    if save:
        save_ndjson('data/raw/funds.ndjson', funds)
        save_ndjson('data/raw/companies.ndjson', companies)


if __name__ == "__main__":
    main()
