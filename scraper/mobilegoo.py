import json
from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
import time
from utils.normalization import normalize_brand, normalize_condition, extract_model

class MobileGooScraper(BaseScraper):
    def __init__(self):
        super().__init__("MobileGoo")
        from config import SCRAPER_CONFIG
        self.config = SCRAPER_CONFIG["mobilegoo"]

    def scrape(self):
        try:
            all_devices = []
            base_url = f"{self.config['base_url']}/collections/mobiles"
            current_url = base_url
            visited_cursors = set()

            while True:
                print(f"Fetching: {current_url}")
                html = self.get_page(current_url, use_selenium=True)
                devices, next_cursor = self.parse_page(html)

                if not devices:
                    print("No devices found, stopping.")
                    break

                all_devices.extend(devices)

                if not next_cursor or next_cursor in visited_cursors:
                    print("No next cursor or already visited. Done.")
                    break

                visited_cursors.add(next_cursor)
                current_url = f"{base_url}?phcursor={next_cursor}"
                time.sleep(1)

            return all_devices

        except Exception as e:
            print(f"MobileGoo scraper error: {str(e)}")
            return []
        finally:
            self.cleanup()

    def parse_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        devices = []

        # 1) Select each product block by its outer container
        product_blocks = soup.select('div.mt-3.lg\\:mt-5')
        print(f"Found {len(product_blocks)} product blocks")

        for block in product_blocks:
            try:
                # 2) Read the displayed device name
                name_tag = block.select_one('h3.block a')
                if not name_tag:
                    continue
                device_name = name_tag.text.strip()

                # 3) Grab the JSON of all variants inside this same block
                script = block.find('script', type='application/json')
                if not script:
                    continue

                variants = json.loads(script.text)

                for variant in variants:
                    # JSON price is in paise → divide by 100 for ₹
                    raw_price = variant.get('price', 0)
                    price = raw_price / 100.0

                    # condition comes from option3 (e.g. “Good” or “Superb…”)
                    raw_cond = variant.get('option3', '')
                    condition = normalize_condition(raw_cond)

                    # extract model from the human name
                    model = extract_model(device_name)

                    # brand—still hardcoded or derived as you prefer
                    brand = normalize_brand("Apple")

                    devices.append({
                        'source': self.source_name,
                        'brand':   brand,
                        'model':   model,
                        'condition': condition,
                        'price':   price
                    })
            except Exception as e:
                print(f"Error parsing product block: {e}")

        
        next_cursor = None
        next_link = soup.select_one('a.pagination__item--next')
        if next_link and 'href' in next_link.attrs:
            m = re.search(r'phcursor=([^&]+)', next_link['href'])
            if m:
                next_cursor = m.group(1)
        print(f"Returning {len(devices)}")
        return devices, next_cursor


