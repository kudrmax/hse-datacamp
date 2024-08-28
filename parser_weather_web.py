from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

def parse(url, zip_code):
    driver_path = './chromedriver-mac-arm64/chromedriver'

    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    print('start')
    try:
        driver.get(url)
        time.sleep(1)

        search_box = driver.find_element(By.ID, "historySearch")
        time.sleep(1)
        search_box.send_keys(zip_code)
        search_box.send_keys(Keys.RETURN)
        time.sleep(1)

        view_button = driver.find_element(By.ID, "dateSubmit")
        view_button.send_keys(Keys.RETURN)
        time.sleep(1)

        html = driver.page_source
        print(html)
    finally:
        driver.quit()
        print('quit')


if __name__ == '__main__':
    zip_code = 10001
    url = 'https://www.wunderground.com/history'
    parse(url, zip_code)
