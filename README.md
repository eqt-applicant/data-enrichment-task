# TODO-list

* [ ] extras: logo
* [ ] extras: sdgs -> replace with text
* [ ] extras: flatten advisor into advisor_name and advisor_link
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

| Fund                    |
|-------------------------|
| name: str (primary key) |
| launch_year: int        |
| size: str               |
| status: str             |


| Company                              |
|--------------------------------------|
| company: str  (primary key)          |
| sector: str                          |
| country: str                         |
| fund: str (foreign key to Fund.name) |
| entry: str                           |
| sdgs: int[]                           |
| responsible_advisor: str             |
| exit: str                            |
| description: str                     |
| hrefs: str[]                         |
| board_of_directors: str[][]          |
| management: str[][]                  |

