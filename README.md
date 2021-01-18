# TODO-list

* [ ] extras: logo
* [ ] extras: include news at the bottom?
* [ ] extras: sdgs -> replace with text
* [ ] extras: flatten advisor into advisor_name and advisor_link
* [ ] extras: clean management / key_figures
* [ ] extras: clean key_events
* [ ] extras: transform columns into more appropriate data types
* [x] write more on testing
* [x] write docs
* [x] enrich all companies with fund reference data
* [x] enrich all companies with org reference data
* [x] scrape all companies own pages
* [x] scrape a company
* [x] join current portfolio + divested into companies
* [x] scrape divested page
* [x] scrape current_portfolio page
* [x] scrape funds page
  
# Introduction

This repo contains code to scrape 

 - https://www.eqtgroup.com/About-EQT/Funds/Active-Funds/
 - https://www.eqtgroup.com/Investments/Current-Portfolio/
 - https://www.eqtgroup.com/Investments/Divestments/

for fund and company data into the non-enriched data model (described below).
After scraping, the data is enriched with additional fund-and-organization
reference data and stored as newline-delimited JSON (ndjson).

The two files belonging to the final resulting dataset can be found in _result.tar.gz_.


# Assumptions / Ideas for taking this further

This pipeline will run in a daily / weekly batch fashion, scheduled by something
like Apache Airflow. I will write this as a single script that runs on my
laptop, but it shouldn't be too hard to convert this into a DAG. Upon doing
that, I would add a task to load this into BigQuery to facilitate running
queries against the data.


# Dependencies & discussion of tech decisions 

I have used python 3.8.6 with pipenv for dependency management.
Libraries used are requests, beautifulsoup4, html5lib and pandas.

I aim for a simple architecture (no need to read in chunks / stream, use gcs as
storage etc).

The setup requires Google Cloud SDK to be installed and authenticated ('gcloud
auth').

The given reference dataset of organizations did not fit in memory (old laptop)
using pandas.read_json() so I parsed the file line by line instead.

# Usage

Run

    ./setup-and-get-reference-data.sh
    
to create temporary directories, download and decompress the reference data to
`./data`.

Run

    pipenv install

to install required python dependencies.


    pipenv run python main.py

Runs the pipeline.

# Testing

    pipenv run pytest
    
Runs the tests.

If this was converted to an Airflow DAG, I would make sure to include the tests
as their own tasks where they would be appropriate. There are not that many
things that can be unit tested here. My focus has been to make sure that the
script can fail if things are not where they are supposed to be. If this was a
real pipeline, I'd use something like Great Expectations in the DAG and (if
necessary) monitor the output of the tasks.


    
# Data model

The data model I have chosen is very flat.
It is expressed below as pseudo code in tables with JSON examples that follow.

The tables follow this structure:

| Entity name                                        |
|----------------------------------------------------|
| field: type explanation (description with comment) |

## Entities

| Fund                    |
|-------------------------|
| name: str (primary key) |
| launch_year: int        |
| size: str               |
| status: str             |

Example:

``` json
{
  "fund": "EQT Exp Capital II",
  "launch": 2007,
  "size": "EUR 474 million",
  "status": "Fully Invested",
  "hrefs": "https://www.eqtgroup.com/About-EQT/Funds/Active-Funds/EQT-Exp-Cap-II/"
}
```

| Company                                                                                                 |
|---------------------------------------------------------------------------------------------------------|
| company: str                                                                                            |
| sector: str (enum-like)                                                                                 |
| country: str (enum-like)                                                                                |
| fund: str (foreign key to Fund.name)                                                                    |
| entry: str (Month Year)                                                                                 |
| href: str                                                                                               |
| exit: str  (Month Year, nullable)                                                                       |
| sdgs: str[] (strings uniquely identifing an sdg; enum-like)                                             |
| advisor: {"advisorname": str, "advisor_href": str}                                                      |
| scraped_description: str                                                                                |
| description_links: str[]  (where you usually find the company url)                                      |
| key_events: str (could be empty str instead of None)                                                    |
| board_of_directors: str[][] - [] of [name:str, title:str] pairs (nullable)                              |
| management_or_key_events: str[][] - [] of [name:str, title:str] pairs (or [key:str figure:str] pairs)   |
| enriched_homepage_url: str, nullable                                                                    |
| country_code: str, nullable                                                                             |
| city: str, nullable                                                                                     |
| founded_on: date, nullable                                                                              |
| short_description: str                                                                                  |
| description: str                                                                                        |
| funding_rounds: int                                                                                     |
| last_funding_on: str (date, YYYY-MM-DD)                                                                 |
| funding_total_usd: int                                                                                  |
| employee_count: str                                                                                     |
| funding_round_uuid: str[] (ordered aggregate list from earliest to latest funding round)                |
| investment_type: str[] (ordered aggregate list from earliest to latest funding round)                   |
| announced_on: str[] (dates YYYY-MM-DD)  (ordered aggregate list from earliest to latest funding round)  |
| raised_amount_usd: number[] (can be NaN) (ordered aggregate list from earliest to latest funding round) |
| investor_names: str[] (ordered aggregate list from earliest to latest funding round)                    |
| investor_count: number[] (ordered aggregate list from earliest to latest funding round)                 |

Example:

``` json
{
  "company": "Acumatica",
  "sector": "TMT",
  "country": "United States",
  "fund": "EQT VII",
  "entry": "Aug 2019",
  "href": "https://www.eqtgroup.com/Investments/Current-Portfolio/acumatica/",
  "exit": null,
  "sdgs": [
    "09",
    "12"
  ],
  "advisor": {
    "advisor_href": "http://www.eqtgroup.com/About-EQT/Organization/Investment-Advisory-professionals/Partners/robert-maclean/",
    "advisorname": "Robert Maclean"
  },
  "scraped_description": "Through its ERP platform, Acumatica helps customers to streamline and automate processes, manage and control inventory in real-time and increase productivity. The Company’s software is delivered via the cloud and is accessible from any location, on any device.\nAcumatica is uniquely positioned to capitalize on the opportunity created from the ERP market’s shift to cloud-based software, thanks to its customer-centric product proposition and a highly-scalable indirect distribution model.\nAcumatica will continue to operate as a fully independent company, while cooperating with sister EQT VII portfolio company IFS. \nTo Acumatica\nMarket trends and drivers\nAcumatica operates in an attractive and sizeable market, with significant growth potential supported by migration tailwinds of on-premise to cloud.",
  "description_links": [
    "https://www.acumatica.com/"
  ],
  "key_events": "",
  "board_of_directors": [
    [
      "Johannes Reichel",
      "Board member"
    ],
    [
      "Jonas Persson",
      "Chairperson"
    ],
    [
      "Franck Cohen",
      "Board member"
    ],
    [
      "Peter Daffern",
      "Board member"
    ],
    [
      "Kim Clarke",
      "Board member"
    ],
    [
      "Robert Maclean",
      "Board member"
    ]
  ],
  "management": [
    [
      "Jon Roskill",
      "CEO"
    ]
  ],
  "homepage_url": "http://www.acumatica.com",
  "country_code": "USA",
  "city": "Kirkland",
  "founded_on": "2006-01-01",
  "short_description": "Acumatica is a provider of cloud business management software that empowers small and mid-size businesses to unlock their potential.",
  "description": "Acumatica is a provider of cloud business management software that empowers small and mid-size businesses to unlock their potential and drive growth. Built on the world’s best cloud and mobile technology and a unique customer-centric licensing model, Acumatica delivers a suite of fully integrated business management applications such as Financials, Distribution, CRM and Project Accounting, powered by a robust and flexible platform. In an interconnected world, Acumatica enables customers to take full control of their business; to play to their strengths, since every business is unique; and to empower their people by going wherever their people go, on any device.",
  "funding_rounds": "5",
  "last_funding_on": "2018-06-15",
  "funding_total_usd": "48300000",
  "employee_count": "101-250",
  "funding_round_uuid": [
    "deffdad1-4532-4c3c-be31-ac6f77a6c96d",
    "154f35d6-abbe-7186-d957-fbba07089b28",
    "4123b7f2-3e6f-cdba-8ddf-3ec4db295e68",
    "bb5f218f-1009-fc24-854e-f22b8c72e3b9",
    "e045aaa8-1614-49aa-96ef-8c43b0310c1d"
  ],
  "investment_type": [
    "series_a",
    "series_b",
    "series_c",
    "series_d",
    "private_equity"
  ],
  "announced_on": [
    "2009-11-03",
    "2011-09-13",
    "2013-11-18",
    "2014-10-21",
    "2018-06-15"
  ],
  "raised_amount_usd": [
    null,
    null,
    10000000.0,
    13300000.0,
    25000000.0
  ],
  "investor_names": [
    "{\"Almaz Capital\"}",
    "{Visma}",
    "{\"Almaz Capital\",\"Runa Capital\"}",
    "{MYOB}",
    "{Accel-KKR}"
  ],
  "investor_count": [
    1.0,
    1.0,
    2.0,
    4.0,
    1.0
  ]
}
```

