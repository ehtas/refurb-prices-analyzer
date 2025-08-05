from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import time
import re
from utils.normalization import normalize_brand, normalize_condition, extract_model

class QuikrScraper(BaseScraper):
    def __init__(self):
        super().__init__("Quikr")
        from config import SCRAPER_CONFIG
        self.config = SCRAPER_CONFIG["quikr"]

    def scrape(self):
        try:
            url = self.config['base_url']
            html = self.get_page_with_scroll(url, max_scrolls=15)
            devices = self.parse_page(html)
            return devices
        except Exception as e:
            print(f"Quikr scraper error: {e}")
            return []
        finally:
            self.cleanup()

    def get_page_with_scroll(self, url, max_scrolls=10):
        self.get_page(url, use_selenium=True)
        for i in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"⬇️ Scrolled {i+1}/{max_scrolls}")
        return self.driver.page_source

    def parse_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        cards = soup.select('div.relatedSnbProducts.srpProducts')
        print(f"🔍 Found {len(cards)} listings")

        devices = []

        for card in cards:
            try:
                title_tag = card.select_one("span.descText")
                if not title_tag:
                    continue
                device_name = title_tag.get_text(strip=True)
                model = re.split(r'[\(|\||,]', extract_model(device_name), maxsplit=1)[0].strip()

                # Hidden price
                price_tag = card.select_one('span[itemprop="price"]')
                if not price_tag or not price_tag.text.strip().isdigit():
                    continue
                price = float(price_tag.text.strip())

                # Brand and condition
                brand = normalize_brand(device_name.split()[0])
                condition_tag = card.select_one('span[itemprop="itemcondition"]')
                condition = normalize_condition(condition_tag.text.strip() if condition_tag else "Used")

                devices.append({
                    "source": self.source_name,
                    "brand": brand,
                    "model": model,
                    "condition": condition,
                    "price": price
                })

            except Exception as e:
                print(f"❌ Error parsing a card: {e}")
        print(f"Returning {len(devices)}")
        return devices
