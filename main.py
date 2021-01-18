import requests
import pandas as pd
import logging as log
import sys
from bs4 import BeautifulSoup
import re
from pathlib import Path
import json


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
    []

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
    main_contentarea_div = soup.find("div", class_="main-contentarea")
    if not main_contentarea_div:
        return []

    sdgs = []
    for img in main_contentarea_div.find_all("img"):
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

    description_div = soup.find("div", class_="main-body")
    description_links = None
    description = ""
    if description_div:
        description_links = [
            link.attrs.get("href") for link in description_div.find_all("a")
        ]
        description = description_div.get_text()

    key_events_div = soup.find("div", class_="key-events")
    key_events = ""
    if key_events_div:
        key_events = key_events_div.get_text()

    board_of_directors_div = soup.find("div",
                                       class_="board-of-directors-module")
    board_of_directors = None
    if board_of_directors_div:
        board_of_directors = [
            div.get_text().strip().split("\n")
            for div in board_of_directors_div.find_all("div",
                                                       class_="fact-row")
        ]

    management_div = soup.find("div", class_="management-module")
    management = None
    if management_div:
        management = [
            div.get_text().strip().split("\n")
            for div in management_div.find_all("div", class_="fact-row")
        ]
    return {
        "sdgs": sdgs,
        "advisor": advisor,
        "description": description,
        "description_links": description_links,
        "key_events": key_events,
        "board_of_directors": board_of_directors,
        "management": management
    }


def save_ndjson(filename, df):
    log.info(f'saving df with shape {df.shape} to {filename}.')
    df.to_json(filename, orient='records', lines=True)


def read_org_fields(company_names):
    orgs = {}
    with open('data/reference/interview-test-org.ndjson', 'r') as f:
        for line in f:
            org_data = json.loads(line)
            company_name = org_data["company_name"]
            if company_name in company_names:
                orgs[company_name] = org_data

    log.info(f"added org data for {len(orgs)} organizations")
    return orgs


def scrape_and_save_funds_current_and_divested():
    log.info("scrape and save funds, current portfolio and divested")

    funds = scrape_funds()
    current_portfolio = scrape_current_portfolio()
    divested = scrape_divested()

    companies = current_portfolio.merge(divested, how='outer')
    companies.rename(columns={'hrefs': 'href'}, inplace=True)

    companies["own_page"] = companies.apply(
        lambda row: scrape_company(row["href"]), axis=1)
    companies = pd.concat([
        companies.drop(['own_page'], axis=1), companies['own_page'].apply(
            pd.Series)
    ],
                          axis=1)

    save_ndjson('data/raw/funds.ndjson', funds)
    save_ndjson('data/raw/companies.ndjson', companies)


def enrich_with_reference(companies):
    log.info(
        "enriching with fund round aggregate and organizational reference data"
    )
    reference_funding = pd.read_json(
        'data/reference/interview-test-funding.ndjson', lines=True)

    company_names = set(companies["company"].to_list())
    company_names |= set(map(str.lower, companies["company"].to_list()))

    reference_org_fields = read_org_fields(company_names)
    reference_org = pd.DataFrame.from_dict(reference_org_fields,
                                           orient='index')
    enriched_org = companies.merge(reference_org,
                                   left_on='company',
                                   right_on='company_name',
                                   how='left')

    enriched_org_uuids = set(enriched_org["uuid"].to_list())
    reference_funding = reference_funding[reference_funding[
        'company_uuid'].map(lambda uuid: uuid in enriched_org_uuids)]

    funding_rounds_agg = reference_funding.groupby('company_uuid')[[
        'funding_round_uuid', 'company_name', 'investment_type',
        'announced_on', 'raised_amount_usd', 'investor_names', 'investor_count'
    ]].agg(list)

    enriched = enriched_org.merge(funding_rounds_agg,
                                  left_on="uuid",
                                  right_on="company_uuid",
                                  how="left")
    return enriched


def main():
    setup_logging()

    if not Path('data/raw/companies.ndjson').exists():
        scrape_and_save_funds_current_and_divested()

    funds = pd.read_json('data/raw/funds.ndjson', lines=True)
    companies = pd.read_json('data/raw/companies.ndjson', lines=True)
    companies.rename(columns={'description': 'scraped_description'},
                     inplace=True)

    enriched = enrich_with_reference(companies)

    # clean up
    log.info('cleaning up the enriched dataset')
    enriched.drop(columns=["company_name_x", "company_name_y", "sdg", "uuid"],
                  inplace=True)
    enriched.rename(
        columns={
            "management": "management_or_key_figures",
            "homepage_url": "enriched_homepage_url"
        })

    save_ndjson('data/out/enriched_companies.ndjson', enriched)
    save_ndjson('data/out/fund.ndjson', funds)


if __name__ == "__main__":
    main()
