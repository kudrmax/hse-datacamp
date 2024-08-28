from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time


class Parser:
    def __init__(self, url: str, driver_path: str):
        self.url = url

        self.service = Service(executable_path=driver_path)
        self.options = webdriver.ChromeOptions()

    def _accept_cookies(self):
        # self.driver.find_element(By.XPATH, '//*[@id="cookie"]').click()
        # self.driver.find_element(By.CLASS_NAME, 'message-button').click()
        # self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Accept all"]').click()
        # self.driver.find_element(By.XPATH, "//button[text()='Accept all']").click()
        # self.driver.find_element(By.XPATH, "//button[text()='Accept all']").click()
        pass

    def _get_html_by_zip_code(self, zip_code: int):
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

    def _get_table(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'mat-table'})
        return table

    def _get_weather_data_from_html(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'mat-table'})
        # table = soup.find('tbody')
        print(table)
        # table = soup.find('table', class_='mat-table cdk-table mat-sort ng-star-inserted').find('tbody')
        # rows = table.find_all('tr')
        # print(rows)
        # table = soup.find('table', class_='mat-table')
        # rows = []
        # for tr in table.find_all('tr'):
        #     cells = [td.text.strip() for td in tr.find_all(['td', 'th'])]
        #     rows.append(cells)

    def _save_html_to_file(self, html: str, save_to: str = 'weather_data.html'):
        with open(save_to, 'w') as file:
            file.write(html)

    def _get_html_from_file(self, file: str):
        with open(file, 'r') as f:
            html = f.read()
            return html

    def _create_html_table(self, zip_code: int):
        self.driver = Chrome(service=self.service, options=self.options)
        html = self._get_html_by_zip_code(zip_code)
        table = self._get_table(html)
        with open(f'html_tables/table_{zip_code}.html', 'w') as file:
            file.write(str(table))

    def parse(self, zip_codes: List[int]):
        try:
            for zip_code in zip_codes:
                self._create_html_table(zip_code)
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
    parser.parse(zip_codes)
