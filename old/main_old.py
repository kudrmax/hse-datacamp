import datetime
import time

import pandas as pd

from weather_parser import Parser

if __name__ == '__main__':
    # data = pd.read_csv('data/weather_stations.csv')
    # zip_codes = list(data['zip_code'])
    # airport_indexes = list(data['index'])

    data = pd.read_csv('../data/zip_codes.csv')
    zip_codes = list(data['zip_code'])

    start_date = datetime.date(2024, 6, 1)
    end_date = datetime.date(2024, 6, 1)

    url = 'https://www.wunderground.com/history'
    driver_path = '../driver/chromedriver'
    html_dir_path = '../html_tables'

    parser = Parser(
        url=url,
        driver_path=driver_path,
        html_dir_path=html_dir_path
    )
    parser.save_weather_data(
        zip_codes,
        ['NONE' for _ in range(len(zip_codes))],
        start_date,
        end_date,
        parse=True,
        save_csv=True,
    )
