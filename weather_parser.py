import os
import time
import datetime

import pandas as pd
from typing import List, Set

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


def date_range_generator(start_date: datetime.date, end_date: datetime.date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)


def get_set_of_existing_station_date_pair():
    dir_path = 'data/weather_of_stations_at_date'
    filenames = os.listdir(dir_path)
    filenames = [f for f in filenames if f.endswith('.html') and os.path.isfile(os.path.join(dir_path, f))]
    filenames = [os.path.splitext(f)[0] for f in filenames]
    station_set = set()
    for filename in filenames:
        filename_list = filename.strip().split('_')
        station_set.add((filename_list[3], datetime.datetime.strptime(filename_list[5], '%Y-%m-%d').date()))
    return station_set

def get_set_of_existing_zip_code_date_pair():
    dir_path = 'data/weather_of_zip_codes_at_date'
    filenames = os.listdir(dir_path)
    filenames = [f for f in filenames if f.endswith('.csv') and os.path.isfile(os.path.join(dir_path, f))]
    filenames = [os.path.splitext(f)[0] for f in filenames]
    zip_codes_set = set()
    for filename in filenames:
        filename_list = filename.strip().split('_')
        zip_codes_set.add((int(filename_list[4]), datetime.datetime.strptime(filename_list[6], '%Y-%m-%d').date()))
    return zip_codes_set


class Parser:
    def __init__(
            self,
            url: str,
            driver_path: str,
            html_dir_path: str | None = None,
    ):
        self.url = url
        # self.html_checker = Checker(html_dir_path)
        # self.html_saver = HTMLDataSaver()

        self.service = Service(executable_path=driver_path)
        self.options = webdriver.ChromeOptions()
        self.options.page_load_strategy = 'none'

    def _run_driver(self):
        self.driver = Chrome(service=self.service, options=self.options)

    @staticmethod
    def _date_range_generator(start_date: datetime.date, end_date: datetime.date):
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)

    def _get_station_by_zip_code(self, zip_code: int, date: datetime.date) -> str | None:
        try:
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
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'mat-table'))
            )
            url = self.driver.current_url
            return url.strip().split('/')[-3]
        except TimeoutException:
            return None

    def save_station_of_zip_code_to_csv(self, zip_code: int):
        station = self.get_station_of_zip_code_from_csv(zip_code)
        if station:
            # print(f'Станция для {zip_code=} уже была получена')
            return
        station = self._get_station_by_zip_code(zip_code, datetime.date(2024, 6, 1))
        if station:
            print(f'Получена станция для {zip_code=}')
            with open('data/station_of_zip_code.csv', 'a') as f:
                f.write(f'{zip_code},{station}\n')
            return
        print(f'Не получилось получить станцию для {zip_code=}')
        # with open('data/bad_zip_codes.txt', 'a') as f:
        #     f.write(f'{zip_code}\n')

    def get_station_of_zip_code_from_csv(self, zip_code: int) -> str | None:
        df = pd.read_csv('data/station_of_zip_code.csv')
        rows = df.loc[df['zip_code'] == zip_code, 'station']
        if len(rows) == 0:
            return None
        return rows.values[0]

    def _get_set_of_station(self) -> Set[str]:
        df = pd.read_csv('data/station_of_zip_code.csv')
        set_of_station = set(df['station'])
        return set_of_station

    def get_weather_html_by_station(self, station: str, date: datetime.date, try_parse=True) -> str | None:
        done_station = get_set_of_existing_station_date_pair()
        if (station, date) in done_station:
            print(f'html для станции {station} за дату {date} уже был получен')
            with open(f'data/weather_of_stations_at_date/weather_of_station_{station}_at_{date}.html', 'r') as f:
                return f.read()
        if try_parse:
            url = f'{self.url}/daily/{station}/date/{date.year}-{date.month}-{date.day}'
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, 6).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'mat-table'))
                )
                print(f'Получен html для станции {station} за дату {date}')
                return self.driver.page_source
            except Exception as e:
                print(f'Ошибка при получении html для станции {station} за дату {date}')
                print(e)

    def get_weather_df_from_html(self, html: str, zip_code: str, date: datetime.date) -> pd.DataFrame:
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
            row_data['time'] = datetime.datetime.strptime(row_list[0].text.strip(), "%I:%M %p").strftime("%H:%M")
            row_data['temperature'] = row_list[1].text.strip().split()[0]
            row_data['humidity'] = row_list[3].text.strip().split()[0]
            row_data['wind_speed'] = row_list[5].text.strip().split()[0]

            new_row = pd.DataFrame([row_data])
            df = pd.concat([df, new_row], ignore_index=True)
        return df


if __name__ == '__main__':
    url = 'https://www.wunderground.com/history'
    driver_path = './driver/chromedriver'
    parser = Parser(url=url, driver_path=driver_path)

    start_date = datetime.date(2024, 6, 1)
    end_date = datetime.date(2024, 6, 20)

    # получение всех зип кодов
    data = pd.read_csv('data/zip_codes_new.csv')
    zip_codes = list(data['zip_code'])

    parser._run_driver()

    # получение пар (зип код, станция)
    for zip_code in zip_codes:
        parser.save_station_of_zip_code_to_csv(zip_code)

    # получение погоды для конкретной станции
    # сохранение погоды для станции для даты
    # station_set = parser._get_set_of_station()
    # print(f'Все станции: {station_set}')
    # for station in station_set:
    #     for date in date_range_generator(start_date, end_date):
    #         html = parser.get_weather_html_by_station(station, date)
    #         if html:
    #             with open(f'data/weather_of_stations_at_date/weather_of_station_{station}_at_{date}.html', 'w') as f:
    #                 f.write(html)

    # парсинг собранных html
    # для кода находим станцию и находим нужный html и парсим его
    done_zip_codes_and_dates = get_set_of_existing_zip_code_date_pair()
    for zip_code in zip_codes:
        for date in date_range_generator(start_date, end_date):
            if (zip_code, date) not in done_zip_codes_and_dates:
                station = parser.get_station_of_zip_code_from_csv(zip_code)
                if not station:
                    print(f'Не известна станция для {zip_code=}')
                    continue
                html = parser.get_weather_html_by_station(station, date, try_parse=False)
                if not html:
                    print(f'Нет html для станции {station} за дату {date}')
                    continue
                weather_df = parser.get_weather_df_from_html(html, zip_code, date)
                weather_df.to_csv(f'data/weather_of_zip_codes_at_date/weather_of_zip_code_{zip_code}_at_{date}.csv')
                print(f'Погода для {zip_code=} за дату {date} была записана в файл')