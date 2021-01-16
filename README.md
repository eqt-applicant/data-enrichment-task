# TODO-list

* DONE scrape funds page
* DONE scrape current_portfolio page
* DONE scrape divested page
* TODO join current + funds + divested into companies
* TODO scrape a company
* TODO scrape all companies own pages
* TODO enrich a company with org reference data
* TODO enrich a company with fund reference data
* TODO enrich all companies with fund and org reference data
* TODO write docs

# Introduction

This repo contains code to scrape 

 - https://www.eqtgroup.com/About-EQT/Funds/Active-Funds/
 - https://www.eqtgroup.com/Investments/Current-Portfolio/
 - https://www.eqtgroup.com/Investments/Divestments/

for fund and company data into the non-enriched data model (described below).
After scraping, the data is enriched with additional fund-and-organization
reference data and stored as newline-delimited JSON (ndjson).

No datasets are larger than what fits into the memory of my laptop, therefore I aim for a simple architecture (no need to read in chunks / stream, use gcs as storage etc).

# Assumptions / Ideas for taking this further

This pipeline will run in daily / weekly in a batch fashion, scheduled by something like Apache Airflow. I will write this as a single script that runs on my laptop, but it shouldn't be too hard to convert this into a DAG.

I would add a step to load this into BigQuery to facilitate queries being ran against the data.

# Dependencies & tech

I have used python 3.8.6 with pipenv for dependency management.
Libraries used are requests, beautifulsoup4, html5lib and pandas.

The setup requires Google Cloud SDK to be installed and authenticated ('gcloud auth').

# Usage

Run

    ./get-reference-data.sh
    
to download and decompress the reference data to `./data`.

Run

    pipenv install

to install required python dependencies.


    pipenv run python main.py

Runs the pipeline.

# Data model (non-enriched)

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

