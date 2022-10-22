import os
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
import time

from constants import COLUMNS

load_dotenv()
logging.basicConfig(level=logging.INFO)


class WebScraper:

    def __init__(self):
        self.login_address = f"{os.environ.get('ROOT_DOMAIN')}/login"
        self.browser = webdriver.Safari()
        self.logger = logging.getLogger(__name__)

    def login(self):
        self.browser.get(self.login_address)
        name = self.browser.find_elements(By.NAME, "emailid")[0]
        password = self.browser.find_elements(By.NAME, "password")[0]
        time.sleep(2)
        name.send_keys(os.environ.get('USERNAME'))
        password.send_keys(os.environ.get('PASSWORD'))
        time.sleep(2)
        name.send_keys(Keys.ENTER)
        password.send_keys(Keys.ENTER)
        self.logger.info("Login successful...")
        time.sleep(2)

    def crawl_and_scrape(self, start_query: int = 0):
        """Scrape items from page 1 to page 136"""
        profile_rows = []
        for _ in range(136):
            # Initiating each page interval
            self.logger.info("Scraping items at page interval %s", start_query)
            self.browser.get(f"{os.environ.get('ROOT_DOMAIN')}/browseprofile/viewall.html?start={start_query}")
            time.sleep(2)
            # Crawling through the page table
            for num in range(1, 21):
                view_details_button = self.browser.find_element(
                    By.XPATH, f'//*[@id="example"]/tbody/tr[{num}]/td/div/div[2]/div/div[2]/div/a'
                )
                profile_href = view_details_button.get_attribute('href')
                self.logger.info(f"Moving to profile page %s on page interval %s...", num, start_query)
                self.browser.get(profile_href)
                time.sleep(2)
                # Gathering all relevant text
                profile_id = self.browser.find_element(
                    By.XPATH, '//*[@id="page"]/section/div/div/div/div/article/div/div/div/h2'
                ).text
                profile_main = self.browser.find_element(
                    By.XPATH, '//*[@id="page"]/section/div/div/div/div/article/div/div/div/div[1]/div[2]/table'
                ).text
                profile_forms = ""
                for form in range(2, 4):
                    profile_forms += self.browser.find_element(
                        By.XPATH, f'//*[@id="home"]/form[{form}]/div'
                    ).text
                all_text = profile_id + profile_main + profile_forms
                profile_text_list = all_text.split()
                # Creating rows after colon is discovered in free text
                curr_profile_row = []
                for i in range(1, len(profile_text_list)-1):
                    if profile_text_list[i-1].endswith(":"):
                        if profile_text_list[i-2] == 'Income' and type(profile_text_list[i]) != str:
                            curr_profile_row.append('Unknown')
                        else:
                            curr_profile_row.append(profile_text_list[i])
                    # Handle height
                    if profile_text_list[i].endswith("cm") and profile_text_list[i-1] != ":":
                        curr_profile_row.append(profile_text_list[i])
                self.logger.info("Current row added to all rows:\n%s", curr_profile_row)
                profile_rows.append(curr_profile_row)
                time.sleep(2)
                self.browser.get(f"{os.environ.get('ROOT_DOMAIN')}/browseprofile/viewall.html?start={start_query}")

            start_query += 20
            if start_query >= 2700:
                # Once we have reached the end, we create a dataframe from the rows and columns
                df = pd.DataFrame(profile_rows, columns=COLUMNS)
                self.logger.info("Preview of dataframe:\n%s", df.head())
                df.to_csv(index=False)
                self.logger.info("Exporting to CSV...")

    def logout(self):
        self.logger.info("Shutting down peacefully...")
        self.browser.quit()
