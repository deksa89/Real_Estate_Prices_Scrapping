# Real Estate Prices Web Scraper
This Python script scrapes real estate price statistics from the imovina.net website. It collects data on various property types across different cities and years, saving the information into CSV files.

## Features
Web Scraping: Utilizes BeautifulSoup to parse HTML and extract data.
Browser Automation: Employs selenium for handling dynamic content and dropdown selections.
Data Storage: Saves scraped data into structured CSV files.

## Requirements
- Python 3.11
- requests
- selenium
- BeautifulSoup4
- pandas
- ChromeDriver (compatible with your Chrome browser version)

## Output
The script will create a directory named rezultati and save the scraped data into CSV files within subdirectories named after the city and year.

```rezultati/
├── Beograd_2024_real_estate_prices/
│   ├── real_estate_prices_2024-01-01.csv
│   ├── real_estate_prices_2024-02-01.csv
│   └── ...
└── ...```
