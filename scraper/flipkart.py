import re
import time
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from utils.normalization import normalize_brand, normalize_condition, extract_model
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FlipkartScraper(BaseScraper):
    def __init__(self):
        super().__init__("Flipkart")
        from config import SCRAPER_CONFIG
        self.config = SCRAPER_CONFIG["flipkart"]

    def scrape(self):
        try:
            all_devices = []
            base_url = self.config['base_url']

            max_pages = 5
            for page_num in range(1, max_pages + 1):
                current_url = f"{base_url}&page={page_num}"
                print(f"📄 Fetching page {page_num}: {current_url}")

                html = self.get_page(current_url, use_selenium=True)
                devices = self.parse_page(html)

                if not devices:
                    print("🛑 No devices found on this page. Stopping pagination.")
                    break

                all_devices.extend(devices)
                time.sleep(1.5)

            return all_devices

        except Exception as e:
            print(f"Flipkart scraper error: {str(e)}")
            return []
        finally:
            self.cleanup()

    def parse_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        devices = []

        outer_blocks = soup.select('div.cPHDOP.col-12-12')
        for block in outer_blocks:
            try:
                anchor = block.select_one('a.CGtC98')
                if not anchor:
                    continue

                title_tag = anchor.select_one('div.KzDlHZ')
                price_tag = anchor.select_one('div.Nx9bqj._4b5DiR')

                if not (title_tag and price_tag):
                    print("Missing title or price, skipping this product")
                    continue

                device_name = title_tag.text.strip()
                raw_price = price_tag.text.strip().replace("₹", "").replace(",", "")

                try:
                    price = float(raw_price)
                except ValueError:
                    print(f"⚠️ Couldn't parse price: {raw_price}")
                    continue

                if not device_name:
                    print("⚠️ Empty device name, skipping.")
                    continue
                    
                device_parts = device_name.replace("(", "").replace(")", "").split()
                brand_guess = device_parts[1] if len(device_parts) > 1 else device_parts[0]
                brand = normalize_brand(brand_guess)
                model = re.split(r'[\(|\||,]', extract_model(device_name), maxsplit=1)[0].strip()
                condition = "Refurbished"
                for li in anchor.select('li.J+igdf'):
                    if "Refurbished" in li.text:
                        condition = normalize_condition(li.text)
                        break

                

                devices.append({
                    "source": self.source_name,
                    "brand": brand,
                    "model": model,
                    "condition": condition,
                    "price": price
                })
            except Exception as e:
                print(f"❌ Error parsing product block: {e}")
        print(f"Returning {len(devices)}")
        return devices



