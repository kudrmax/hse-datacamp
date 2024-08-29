import time
import datetime

import pandas as pd
from typing import List, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select


class Checker:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.set = None

    def mark_data_as_done(self, data):
        with open(self.file_name, 'a') as f:
            f.write(data)

    def check_data_is_done(self, data, update_set=False):
        with open(self.file_name, 'r') as f:
            lines = f.readlines()
        if update_set or not self.set:
            self.set = set(lines)
        return data in self.set


class Parser:
    def __init__(
            self,
            url: str,
            driver_path: str,
            html_check_file_path
    ):
        self.url = url
        self.html_checker = Checker(html_check_file_path)
        self.service = Service(executable_path=driver_path)
        self.options = webdriver.ChromeOptions()

    @staticmethod
    def date_range_generator(start_date, end_date):
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)

    @staticmethod
    def _get_data_for_checker(zip_code: int, date: datetime.date):
        return f'{zip_code}_{date}'

    def _parse_html(self, zip_code: int, date: datetime.date):
        self.driver.get(self.url)

        # ввод индекса
        search_box = self.driver.find_element(By.ID, "historySearch")
        time.sleep(1)
        search_box.send_keys(str(zip_code))
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        # заполнение даты
        def get_select(id):
            dropdown = self.driver.find_element(By.ID, id)
            select = Select(dropdown)
            return select

        select = get_select('monthSelection')
        select.select_by_value(f'{date.month}')
        time.sleep(1)

        select = get_select('daySelection')
        select.select_by_value(f'{date.day}')
        time.sleep(1)

        select = get_select('yearSelection')
        select.select_by_value(f'{date.year}')
        time.sleep(1)

        # нажатие на кнопку
        search_box.submit()
        view_button = self.driver.find_element(By.ID, "dateSubmit")
        view_button.click()

        # ожидание загрузки
        time.sleep(10)
        return self.driver.page_source

    def _get_table_from_html(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'mat-table'})
        return table

    def _save_html(self, html, zip_code: int, date: datetime.date):
        with open(f'html_tables/table_{zip_code}_{date}.html', 'w') as file:
            file.write(html)

    def _get_html_from_file(self, zip_code: int, date: datetime.date):
        with open(f'html_tables/table_{zip_code}_{date}.html', 'r') as file:
            html = file.read()
            return html

    def _get_weather_data_from_html(self, html: str, zip_code: int, date: datetime.date):
        df = pd.DataFrame(columns=['zip_code', 'date', 'time', 'temperature', 'humidity', 'wind_speed'])
        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find('table', {'class': 'mat-table'}).find_all('tr')
        for row in rows:
            row_list = row.find_all('td')
            row_data = {}
            if not len(row_list) == 10:
                continue
            row_data['zip_code'] = zip_code
            row_data['date'] = date
            row_data['time'] = row_list[0].text.strip()
            row_data['temperature'] = row_list[1].text.strip().split()[0]
            row_data['humidity'] = row_list[3].text.strip().split()[0]
            row_data['wind_speed'] = row_list[5].text.strip().split()[0]

            new_row = pd.DataFrame([row_data])
            df = pd.concat([df, new_row], ignore_index=True)

        with open(f'weather_data_csv/weather_data_{zip_code}_{date}.csv', 'w') as file:
            df.to_csv(file, index=False)

    def save_weather_data(
            self,
            zip_codes: List[int],
            start_date: datetime.date,
            end_date: datetime.date,
            parse=False
    ):
        try:
            if parse:
                self.driver = Chrome(service=self.service, options=self.options)
                for zip_code in zip_codes:
                    for date in self.date_range_generator(start_date, end_date):
                        html = self._parse_html(zip_code, date)
                        self._save_html(html, zip_code, date)
                        self.html_checker.mark_data_as_done(self._get_data_for_checker(zip_code, date))
            for zip_code in zip_codes:
                for date in self.date_range_generator(start_date, end_date):
                    html = self._get_html_from_file(zip_code, date)
                    self._get_weather_data_from_html(html, zip_code, date)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    zip_codes = [125480]
    start_date = datetime.date(2024, 6, 1)
    end_date = datetime.date(2024, 6, 2)

    url = 'https://www.wunderground.com/history'
    driver_path = './driver/chromedriver'
    html_check_file_path = './done_html.txt'

    parser = Parser(
        url=url,
        driver_path=driver_path,
        html_check_file_path=html_check_file_path
    )
    parser.save_weather_data(zip_codes, start_date, end_date, parse=True)
