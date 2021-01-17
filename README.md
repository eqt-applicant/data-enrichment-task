# TODO-list

* DONE scrape funds page
* DONE scrape current_portfolio page
* DONE scrape divested page
* DONE join current portfolio + divested into companies
* DONE scrape a company
* TODO scrape all companies own pages
* TODO enrich a company with org reference data
* TODO enrich a company with fund reference data
* TODO enrich all companies with fund and org reference data
* TODO write docs
* TODO write more on testing

# Introduction

This repo contains code to scrape 

 - https://www.eqtgroup.com/About-EQT/Funds/Active-Funds/
 - https://www.eqtgroup.com/Investments/Current-Portfolio/
 - https://www.eqtgroup.com/Investments/Divestments/

for fund and company data into the non-enriched data model (described below).
After scraping, the data is enriched with additional fund-and-organization
reference data and stored as newline-delimited JSON (ndjson).

# Assumptions / Ideas for taking this further

This pipeline will run in a daily / weekly batch fashion, scheduled by something like Apache Airflow. I will write this as a single script that runs on my laptop, but it shouldn't be too hard to convert this into a DAG.
Upon doing that, I would add a step to load this into BigQuery to facilitate running queries against the data.

# Dependencies & tech

I have used python 3.8.6 with pipenv for dependency management.
Libraries used are requests, beautifulsoup4, html5lib and pandas.

No datasets are larger than what fits into the memory of my laptop, therefore I aim for a simple architecture (no need to read in chunks / stream, use gcs as storage etc).

The setup requires Google Cloud SDK to be installed and authenticated ('gcloud auth').

# Usage

Run

    ./setup-and-get-reference-data.sh
    
to create temporary directories, download and decompress the reference data to `./data`.

Run

    pipenv install

to install required python dependencies.


    pipenv run python main.py

Runs the pipeline.

# Note on testing


    pipenv run pytest
    
Runs the tests.

I have decided to do my tests as assertions on what the data looks like on various steps in the pipeline, where a failing tests prints an error message and exits the script with a non-zero exit code. If this were converted to an Airflow DAG, I would make sure to include the tests as their own tasks where they would be appropriate.

# Data model (non-enriched)

The data model I have chosen is very flat.
It is expressed below as pseudo code in tables.

## Entities

| Fund             |
|------------------|
| name: str        |
| launch_year: int |
| size: str        |
| status: str      |


| Company                     |
|-----------------------------|
| name: str                   |
| sector: str                 |
| country: str                |
| responsible_advisor: str    |
| fund: Record{Fund}          |
| entry: str                  |
| exit: str                   |
| sdg: int[]                  |
| description: str            |
| hrefs: str[]                |
| board_of_directors: str[][] |
| management: str[][]         |

