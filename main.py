import os
import django
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "selenium_iphone_project.settings")
django.setup()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from parser_app.parser import scrape_product


def main():
    print("Launch Selenium…")

    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 10)

    driver.get("https://brain.com.ua")

    # Пошук
    search_input = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            "//div[contains(@class,'header-search-form')]//input[@class='quick-search-input']"
        ))
    )
    search_input.send_keys("Apple iPhone 15 128GB Black")

    search_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[contains(@class,'header-search-form')]//input[@type='submit']"
        ))
    )
    search_button.click()

    # Клік по першому результату
    first_product = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            "(//div[contains(@class,'product-wrapper')]//a)[1]"
        ))
    )
    first_product.click()


    wait.until(EC.presence_of_element_located((
        By.XPATH, "//h1[contains(@class,'desktop-only-title')]"
    )))

    # Передаємо driver у парсер
    scrape_product(driver)
    driver.quit()

if __name__ == "__main__":
    main()
