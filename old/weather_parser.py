import os
import time
import datetime

import pandas as pd
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Chrome, DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tqdm import tqdm


class Checker:
    def __init__(self, html_dir_path: str):
        filenames = os.listdir(html_dir_path)
        # filenames = [f for f in filenames if os.path.isfile(os.path.join(html_dir_path, f))]
        filenames = [f for f in filenames if f.endswith('.html') and os.path.isfile(os.path.join(html_dir_path, f))]
        filenames = [os.path.splitext(f)[0] for f in filenames]

        self.set = set()
        for filename in filenames:
            filename_list = filename.split('_')
            self.set.add(filename_list[1] + '_' + filename_list[2] + '_' + filename_list[3].split('.')[0])
        print(self.set)

    def mark_data_as_done(self, data):
        self.set.add(data)

    def is_data_already_parsed(self, data, update_set=False):
        return data in self.set


class HTMLDataSaver:
    @staticmethod
    def _get_table_from_html(html: str):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'mat-table'})
        return table

    @staticmethod
    def _save_html(html, zip_code: int, airport, date: datetime.date):
        with open(f'html_tables/table_{airport}_{zip_code}_{date}.html', 'w') as file:
            file.write(html)

    @staticmethod
    def _get_html_from_file(zip_code: int, airport, date: datetime.date):
        with open(f'html_tables/table_{airport}_{zip_code}_{date}.html', 'r') as file:
            html = file.read()
            return html


class Parser:
    def __init__(
            self,
            url: str,
            driver_path: str,
            html_dir_path
    ):
        self.url = url
        self.html_checker = Checker(html_dir_path)
        self.html_saver = HTMLDataSaver()

        self.service = Service(executable_path=driver_path)
        self.options = webdriver.ChromeOptions()
        self.options.page_load_strategy = 'none'

    @staticmethod
    def date_range_generator(start_date: datetime.date, end_date: datetime.date):
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)

    @staticmethod
    def _get_data_for_checker(zip_code: int, airport, date: datetime.date) -> str:
        return f'{airport}_{zip_code}_{date}'

    def _parse_html(self, zip_code: int, date: datetime.date) -> str | None:
        self.driver.get(self.url)
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'historySearch')))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'yearSelection')))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'daySelection')))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'monthSelection')))
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'dateSubmit')))

        # ввод индекса
        search_box = self.driver.find_element(By.ID, "historySearch")
        search_box.send_keys(str(zip_code))
        search_box.send_keys(Keys.RETURN)

        # заполнение даты
        def get_select(id):
            dropdown = self.driver.find_element(By.ID, id)
            select = Select(dropdown)
            return select

        select = get_select('monthSelection')
        select.select_by_value(f'{date.month}')

        select = get_select('daySelection')
        select.select_by_visible_text(f'{date.day}')

        select = get_select('yearSelection')
        select.select_by_visible_text(f'{date.year}')

        # нажатие на кнопку
        time.sleep(1)
        search_box.submit()
        view_button = self.driver.find_element(By.ID, "dateSubmit")
        view_button.click()

        # ожидание загрузки
        try:
            # time.sleep(10)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'mat-table'))
            )
            return self.driver.page_source
        except TimeoutException:
            return None

    def _get_and_save_weather_data_from_html(self, html: str, zip_code: int, date: datetime.date,
                                             airport: str | None = None) -> None:
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

        filename = f'weather_data_csv/weather_data_{airport}_{zip_code}_{date}.csv'
        with open(filename, 'w') as file:
            df.to_csv(file, index=False)

    def parse(self, zip_codes: List[int], airport_indexes, start_date: datetime.date, end_date: datetime.date) -> None:
        self.driver = Chrome(service=self.service, options=self.options)
        start = time.time()
        for zip_code, airport in zip(zip_codes, airport_indexes):
            for date in self.date_range_generator(start_date, end_date):
                if self.html_checker.is_data_already_parsed(self._get_data_for_checker(zip_code, airport, date)):
                    print(f'The page was skipped: {zip_code} {date} {airport}')
                    continue
                html = self._parse_html(zip_code, date)
                if html:
                    self.html_saver._save_html(html, zip_code, airport, date)
                    self.html_checker.mark_data_as_done(self._get_data_for_checker(zip_code, airport, date))
                    print(f'The page was parsed: {zip_code} {date} {airport}')
                else:
                    print(f'The page was NOT parsed: {zip_code} {date} {airport}')
                end = time.time()
                # print(f'Time elapsed: {end - start}')

    def save_csv(self, zip_codes: List[int], airport_indexes, start_date: datetime.date, end_date: datetime.date,
                 airport: str | None = None) -> None:
        for zip_code in zip_codes:
            for date in self.date_range_generator(start_date, end_date):
                html = self.html_saver._get_html_from_file(zip_code, date, airport_indexes)
                self._get_and_save_weather_data_from_html(html, zip_code, date, airport)
                print(f'The page was saved as csv: {zip_code} {date}')

    def save_weather_data(
            self,
            zip_codes: List[int],
            airport_indexes,
            start_date: datetime.date,
            end_date: datetime.date,
            parse=False,
            save_csv=False,
            airport: str | None = None,
    ):
        try:
            if parse:
                print('Parsing was started')
                self.parse(zip_codes, airport_indexes, start_date, end_date)
            if save_csv:
                self.save_csv(zip_codes, airport_indexes, start_date, end_date)
        except Exception as e:
            if '{"method":"css selector","selector":"[id="historySearch"]"}' in str(e):
                print('You have to turn on VPN')
                return
            print(e)


if __name__ == '__main__':
    pass
    # zip_codes = [125480]
    # start_date = datetime.date(2024, 6, 1)
    # end_date = datetime.date(2024, 6, 3)
    #
    # url = 'https://www.wunderground.com/history'
    # driver_path = './driver/chromedriver'
    # html_dir_path = './html_tables'
    #
    # parser = Parser(
    #     url=url,
    #     driver_path=driver_path,
    #     html_dir_path=html_dir_path
    # )
    # parser.save_weather_data(
    #     zip_codes,
    #     airport_indexes
    #     start_date,
    #     end_date,
    #     parse=True,
    #     save_csv=True,
    # )
