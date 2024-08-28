import time
import pandas as pd
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Parser:
    def __init__(self, url: str, driver_path: str):
        self.url = url

        self.service = Service(executable_path=driver_path)
        self.options = webdriver.ChromeOptions()

    def _parse_html(self, zip_code: int):
        self.driver = Chrome(service=self.service, options=self.options)
        self.driver.get(url)

        search_box = self.driver.find_element(By.ID, "historySearch")
        time.sleep(1)
        search_box.send_keys(str(zip_code))
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        search_box.submit()
        view_button = self.driver.find_element(By.ID, "dateSubmit")
        view_button.click()

        time.sleep(10)
        return self.driver.page_source

    def _get_table_from_html(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'mat-table'})
        return table

    def _save_html(self, html, zip_code: int):
        with open(f'html_tables/table_{zip_code}.html', 'w') as file:
            file.write(html)

    def _get_html_from_file(self, zip_code: int):
        with open(f'html_tables/table_{zip_code}.html', 'r') as file:
            html = file.read()
            return html

    def _get_weather_data_from_html(self, html: str, zip_code: int):
        df = pd.DataFrame(columns=['zip_code', 'time', 'temperature', 'humidity', 'wind_speed'])
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find('table', {'class': 'mat-table'}).find_all('tr')
        for row in rows:
            row_list = row.find_all('td')
            row_data = {}
            if not len(row_list) == 10:
                continue
            row_data['zip_code'] = zip_code
            row_data['time'] = row_list[0].text.strip()
            row_data['temperature'] = row_list[1].text.strip().split()[0]
            row_data['humidity'] = row_list[3].text.strip().split()[0]
            row_data['wind_speed'] = row_list[5].text.strip().split()[0]

            new_row = pd.DataFrame([row_data])
            df = pd.concat([df, new_row], ignore_index=True)

        with open(f'weather_data_csv/weather_data_{zip_code}.csv', 'w') as file:
            df.to_csv(file, index=False)

    def save_weather_data(self, zip_codes: List[int], parse=False):
        try:
            if parse:
                for zip_code in zip_codes:
                    html = self._parse_html(zip_code)
                    self._save_html(html, zip_code)
            for zip_code in zip_codes:
                html = self._get_html_from_file(zip_code)
                self._get_weather_data_from_html(html, zip_code)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    zip_codes = [125480]
    url = 'https://www.wunderground.com/history'
    driver_path = './driver/chromedriver'
    vpn_extension_path = ''

    parser = Parser(
        url=url,
        driver_path=driver_path
    )
    parser.save_weather_data(zip_codes, parse=False)
