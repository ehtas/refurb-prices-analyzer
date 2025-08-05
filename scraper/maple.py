from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from utils.normalization import normalize_brand, normalize_condition, extract_model
import time

class MapleScraper(BaseScraper):
    def __init__(self):
        super().__init__("Maple")
        from config import SCRAPER_CONFIG
        self.config = SCRAPER_CONFIG["maple"]

    def scrape(self):
        try:
            all_devices = []
            base_url = f"{self.config['base_url']}/collection/iphone"
            per_page = 8

            # Step 1: Fetch the first page to determine total number of pages
            first_url = f"{base_url}?offset=1&perpage={per_page}"
            first_html = self.get_page(first_url, use_selenium=True)

            # Step 2: Extract total number of pages dynamically
            soup = BeautifulSoup(first_html, 'html.parser')
            pagination_links = soup.select('ul.Pagination_pagination__WK02Q li.Pagination_pageItem__8Jvhv a')

            total_pages = 1  # Fallback
            for a in pagination_links:
                text = a.text.strip()
                if text.isdigit():
                    total_pages = max(total_pages, int(text))

            print(f"Total pages detected: {total_pages}")

            # Step 3: Loop through all pages using offset
            for page_num in range(1, total_pages + 1):  # offset = page_num
                paged_url = f"{base_url}?offset={page_num}&perpage={per_page}"
                print(f"Fetching page {page_num}: {paged_url}")

                html_content = self.get_page(paged_url, use_selenium=True)
                devices = self.parse_page(html_content)

                if not devices:
                    print(f"No devices found at page {page_num}. Stopping early.")
                    break

                all_devices.extend(devices)
                time.sleep(1)

            return all_devices

        except Exception as e:
            print(f"Maple scraper error: {str(e)}")
            return []
        finally:
            self.cleanup()

    def parse_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        devices = []

        device_containers = soup.select('li.card')

        if not device_containers:
            print("No device containers found on Maple page")
            return devices

        print(f"Found {len(device_containers)} device containers")

        for container in device_containers:
            try:
                link_tag = container.find('a')
                if not link_tag:
                    continue

                name_tag = container.select_one('div.info > h5')
                if not name_tag:
                    continue

                device_name = name_tag.text.strip()

                price_tag = container.select_one('span.sell-price')
                if not price_tag:
                    continue

                price_text = price_tag.text.strip()
                price_match = re.search(r'₹([\d,]+)', price_text)
                if not price_match:
                    continue

                price = float(price_match.group(1).replace(',', ''))

                detail_text = container.select_one('div.info > p')
                condition = "Good"
                if detail_text:
                    parts = detail_text.text.strip().split("|")
                    if len(parts) > 1:
                        condition = parts[1].strip()

                brand = "Apple"
                model = extract_model(device_name)
                condition = normalize_condition(condition)
                brand = normalize_brand(brand)

                devices.append({
                    'source': self.source_name,
                    'brand': brand,
                    'model': model,
                    'condition': condition,
                    'price': price
                 
                })

            except Exception as e:
                print(f"Error processing device: {str(e)}")
                continue

        print(f"Returning {len(devices)} devices from current page")
        return devices

