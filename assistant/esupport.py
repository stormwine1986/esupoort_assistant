from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.keys import Keys

from typing import List
import time
from urllib.parse import quote

class ESupport:
    """A class to represent a web driver."""
    def __init__(self, driver_path):
        self.driver_path = driver_path
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--log-level=3')
        # Suppress logging of automation and USB errors
        options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self, email, password):
        """Login to the website."""
        self.driver.get('https://www.ptc.com/en/support/search/#f-ts_product_category=Codebeamer&f-ts_category=Support')
        ## 登录
        username_input = self.driver.find_element(By.ID, "username_eSupportLoginForm")
        username_input.send_keys(email)
        password_input = self.driver.find_element(By.ID, "password_eSupportLoginForm")
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 10).until(EC.title_contains('PTC Knowledgebase Search'))
        
    def search_articles(self, search:str) -> List[dict]:
        """
        List articles.
        @param search: Search keyword
        @return: A list of dictionaries containing article information such as title and link.
        """
        self.driver.get(f"https://www.ptc.com/en/support/search/#q={quote(search)}&f-ts_product_category=Codebeamer&f-ts_category=Support")
        atomic_folded_result_list = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, "atomic-folded-result-list")
            )
        )
        ## 等待 shadow root 下的元素加载完成
        time.sleep(15)
        atomic_result = self.driver.execute_script(
            'return arguments[0].shadowRoot.querySelectorAll("atomic-result")', 
            atomic_folded_result_list
        )
        results = []
        for result in atomic_result:
            atomic_result_text = self.driver.execute_script(
                'return arguments[0].shadowRoot.querySelector("atomic-result-text")', 
                result
            )
            parent_element = atomic_result_text.find_element(By.XPATH, '..')
            results.append({
                "title": atomic_result_text.text, "link": parent_element.get_attribute("href")
            })
        return results
    
    def get_article_details(self, articles: List[dict]) -> List[dict]:
        """
        Get article details such as description and resolution.
        @param articles: List[dict] Top 5 Articles
        @return: List[dict] Article Details
        """
        for article in articles:
            self.driver.get(article["link"])
            h2 = self.driver.find_elements(By.TAG_NAME, "h2")
            for el in h2:
                if el.text == "Description":
                    next_sibling = el.find_element(By.XPATH, "following-sibling::*[1]")
                    article["description"] = next_sibling.text
                elif el.text == "Resolution":
                    next_sibling = el.find_element(By.XPATH, "following-sibling::*[1]")
                    article["resolution"] = next_sibling.text
                
        return articles
    
    def exit(self):
        """
        Quit the driver.
        """
        self.driver.quit()
        
    