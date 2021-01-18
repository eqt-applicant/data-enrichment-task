# TODO-list

* [ ] extras: logo
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
