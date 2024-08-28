from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class Parser:
    def __init__(self, url: str, driver_path: str):
        self.url = url
        self.driver_path = driver_path

        service = Service(executable_path=self.driver_path)
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=service, options=options)

    def _get_html_by_zip_code(self, zip_code: str):
        self.driver.get(url)
        time.sleep(1)

        search_box = self.driver.find_element(By.ID, "historySearch")
        time.sleep(1)
        search_box.send_keys(zip_code)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        view_button = self.driver.find_element(By.ID, "dateSubmit")
        view_button.send_keys(Keys.RETURN)
        time.sleep(1)

        return self.driver.page_source

    def _get_weather_data_from_html(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class':'mat-table'})
        print(table)
        # table = soup.find('table', class_='mat-table cdk-table mat-sort ng-star-inserted').find('tbody')
        # rows = table.find_all('tr')
        # print(rows)
        # table = soup.find('table', class_='mat-table')
        # rows = []
        # for tr in table.find_all('tr'):
        #     cells = [td.text.strip() for td in tr.find_all(['td', 'th'])]
        #     rows.append(cells)

    def _get_parse_by_zip_code(self, zip_code: str):
        html = self._get_html_by_zip_code(zip_code)
        result = self._get_weather_data_from_html(html)

    def parse(self, zip_code):
        try:
            self._get_parse_by_zip_code(zip_code)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    zip_code = 10001
    url = 'https://www.wunderground.com/history'
    driver_path = './driver/chromedriver'

    parser = Parser(url=url, driver_path=driver_path)
    parser.parse(zip_code)
