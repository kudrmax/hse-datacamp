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

        service = Service(executable_path=driver_path)
        options = webdriver.ChromeOptions()
        self.driver = Chrome(service=service, options=options)

    def _accept_cookies(self):
        # self.driver.find_element(By.XPATH, '//*[@id="cookie"]').click()
        # self.driver.find_element(By.CLASS_NAME, 'message-button').click()
        # self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Accept all"]').click()
        # self.driver.find_element(By.XPATH, "//button[text()='Accept all']").click()
        # self.driver.find_element(By.XPATH, "//button[text()='Accept all']").click()
        pass

    def _get_html_by_zip_code(self, zip_code: str):
        self.driver.get(url)

        search_box = self.driver.find_element(By.ID, "historySearch")
        time.sleep(1)
        search_box.send_keys(zip_code)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        search_box.submit()
        view_button = self.driver.find_element(By.ID, "dateSubmit")
        view_button.click()

        time.sleep(3)
        return self.driver.page_source

    def _get_weather_data_from_html(self, html: str):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'mat-table'})
        table = soup.find('tbody')
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

    def _get_parse_by_zip_code(self, zip_code: str):
        html = self._get_html_by_zip_code(zip_code)
        self._save_html_to_file(html, save_to='weather_data.html')
        # html = self._get_html_from_file('weather_data.html')
        result = self._get_weather_data_from_html(html)
        time.sleep(3)

    def parse(self, zip_code):
        try:
            self._get_parse_by_zip_code(zip_code)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    zip_code = 10001
    url = 'https://www.wunderground.com/history'
    driver_path = './driver/chromedriver'
    vpn_extension_path = ''

    parser = Parser(
        url=url,
        driver_path=driver_path
    )
    parser.parse(zip_code)
