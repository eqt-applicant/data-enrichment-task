from main import scrape_company


def test_one_company_scrape():
    d = scrape_company(
        "https://www.eqtgroup.com/Investments/Current-Portfolio/adamo/")
    print(d)
    assert ['Martin Czermin', 'CEO'] in d.get("management")


def test_one_company_scrape_description_not_empty():
    d = scrape_company(
        "https://www.eqtgroup.com/Investments/Current-Portfolio/adamo/")
    print(d)
    assert len(d.get("description")) != 0
