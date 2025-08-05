from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

class BaseScraper:
    def __init__(self, source_name):
        self.source_name = source_name
        self.driver = None
        
    def setup_selenium(self):
        """Setup headless Chrome browser"""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument('--enable-unsafe-webgl')
        options.add_argument('--use-gl=swiftshader')
        options.add_argument('--enable-unsafe-swiftshader')
        options.add_argument('--ignore-gpu-blocklist')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        

        driver_path = ChromeDriverManager().install()
        if not driver_path.endswith("chromedriver.exe"):
            candidate = Path(driver_path).parent / "chromedriver.exe"
            if candidate.exists():
                driver_path = str(candidate)
            else:
                raise FileNotFoundError(f"Could not find chromedriver.exe in {Path(driver_path).parent}")
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
            
    def close_selenium(self):
        """Close browser if open"""
        if self.driver:
            self.driver.quit()
            
    def get_page(self, url, use_selenium=False):
        time.sleep(random.uniform(1, 3))

        if use_selenium:
            if not self.driver:
                self.setup_selenium()

            self.driver.get(url)

            # Flipkart-specific logic
            if "flipkart.com" in url:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "cPHDOP"))
                    )
                except Exception as e:
                    print(f"Flipkart wait error: {e}")

            # Maple-specific logic
            elif "maple" in url:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.card"))
                    )
                except Exception as e:
                    print(f"Maple wait error: {e}")

            # Scroll down slightly in all selenium requests
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            return self.driver.page_source

        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text


        
    def cleanup(self):
        """Ensure browser is closed after scraping"""
        self.close_selenium()
    