from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from utils.normalization import normalize_brand, normalize_condition, extract_model

class RefitScraper(BaseScraper):
    def __init__(self):
        super().__init__("RefitGlobal")
        from config import SCRAPER_CONFIG
        self.config = SCRAPER_CONFIG["refitGlobal"]

    def scrape(self):
        try:
            url = f"{self.config['base_url']}/collections/all-refurbished-mobile-phones"
            html_content = self.get_page(url, use_selenium=False)
            return self.parse_page(html_content)
        except Exception as e:
            print(f"Refit scraper error: {str(e)}")
            return []
        finally:
            self.cleanup()

    def parse_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        devices = []

        containers = soup.select('div.card-wrapper.product-card-wrapper')

        if not containers:
            print("No product containers found.")
            return devices

        print(f"Found {len(containers)} products")

        for item in containers:
            try:
                # Device name
                name_tag = item.select_one('h3.card__heading a')
                device_name = name_tag.text.strip() if name_tag else ""

                # Price
                price_tag = item.select_one('span.price-item--sale') or item.select_one('span.price-item--regular')
                price_text = price_tag.text.strip() if price_tag else ""
                price_match = re.search(r'₹([\d,]+)', price_text)
                price = float(price_match.group(1).replace(',', '')) if price_match else None

                if not device_name or not price:
                    continue

                brand = device_name.split()[0]
                model = extract_model(device_name)

                devices.append({
                    'source': self.source_name,
                    'brand': normalize_brand(brand),
                    'model': model,
                    'condition': normalize_condition("Refurbished"),
                    'price': price
                })

            except Exception as e:
                print(f"Error processing product: {str(e)}")
                continue
        print(f"Returning {len(devices)}")
        return devices
