import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import os

base_url = 'https://imovina.net/statistika_cena_nekretnina/'

chromedriver_path = '' # download chromedriver and add path to the chromedriver.exe

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def get_dropdown_options_selenium(driver, select_id):
    select_element = driver.find_element(By.ID, select_id)
    options = select_element.find_elements(By.TAG_NAME, 'option')
    return {option.get_attribute('value'): option.text.strip() for option in options if option.get_attribute('value')}


def get_dropdown_options(soup, select_id):
    options = soup.find('select', id=select_id).find_all('option')
    return {option.get('value'): option.get_text(strip=True) for option in options if option.get('value')}

response = requests.get(base_url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'html.parser')

# Uncoment if you want to get data for each category, town and year available
#statistics = get_dropdown_options(soup, 'categoryId')
statistics = ['1']

cities = get_dropdown_options(soup, 'cityId')
#cities = {'1': 'Beograd'} # 1 is Beograd's id, each city has its own id

#years = get_dropdown_options(soup, 'yearId')
years = {'2024': '2024', '2023': '2023', '2022': '2022'}

# 2024 is default year and has dates on the page whereas no dates are availabe for other years until you click on the PRIPREMI button
def get_dates(driver, year_value):
    if year_value != '2024': 
        driver.get(base_url)
        godina_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'year'))
        )
        select = Select(godina_dropdown)
        select.select_by_value(year_value)
        time.sleep(5)
        pripremi_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div/div/form/div[2]/div[3]'))
        )
        pripremi_button.click()
        dates = get_dropdown_options_selenium(driver, 'statsId')

    else:
        dates = get_dropdown_options(soup, 'statsId')

    return dates

# process each date within the given year
def process_year(stat, city_value, city_name, year_value, year_name):
    folder_name = f"rezultati\\{city_name}_{year_name}_real_estate_prices"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)

    date = get_dates(driver, year_value)

    for date_value, date_name in date.items():
        data = []
        params = {
            'statistika': stat,
            'grad': city_value,
            'godina': year_value,
            'datum': date_value
        }
        response = requests.get(f'https://imovina.net/statistika_cena_nekretnina/?viewType=map&category={stat}&city={city_value}&year={year_name}&stats={date_value}&load=PRIPREMI', headers=headers, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        
        if table is None:
            print(f"Table not found for Statistika: {stat}, Grad: {city_name}, Godina: {year_name}, Datum: {date_name}")
            continue

        for row in table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0:
                reon = columns[0].get_text(strip=True)
                jednosoban = columns[1].get_text(strip=True)
                jednosoban_em2 = columns[2].get_text(strip=True)
                dvosoban = columns[3].get_text(strip=True)
                dvosoban_em2 = columns[4].get_text(strip=True)
                trosoban = columns[5].get_text(strip=True)
                trosoban_em2 = columns[6].get_text(strip=True)
                ukupno_em2 = columns[7].get_text(strip=True)
                data.append([stat, city_name, year_name, date_name, reon, jednosoban, jednosoban_em2, dvosoban, dvosoban_em2, trosoban, trosoban_em2, ukupno_em2])
        
        sleep(1)
        df = pd.DataFrame(data, columns=['Statistika', 'Grad', 'Godina', 'Datum', 'Reon', 'Jednosoban', 'Jednosoban e/m2', 'Dvosoban', 'Dvosoban e/m2', 'Trosoban', 'Trosoban e/m2', 'Ukupno e/m2'])
        filename = os.path.join(folder_name, f'real_estate_prices_{stat}_{city_name}_{date_name}.csv')
        df.to_csv(filename, index=False)
        print(f'Data has been written to real_estate_prices_{date_name}_{city_name}.csv')

    driver.quit()

for stat in statistics:
    for city_value, city_name in cities.items():
        for year_value, year_name in years.items():
            process_year(stat, city_value, city_name, year_value, year_name)