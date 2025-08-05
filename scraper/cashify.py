from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re
from utils.normalization import normalize_brand, normalize_condition, extract_model


class CashifyScraper(BaseScraper):
    def __init__(self):
        super().__init__("Cashify")
        from config import SCRAPER_CONFIG
        self.config = SCRAPER_CONFIG["cashify"]
        
    def scrape(self):
        try:
            categories = [
                (f"{self.config['base_url']}/buy-refurbished-mobile-phones", "Phone"),
                (f"{self.config['base_url']}/buy-refurbished-tablets", "Tablet"),
                (f"{self.config['base_url']}/buy-refurbished-laptops", "Laptop"),
                (f"{self.config['base_url']}/buy-refurbished-smart-watches", "Smartwatch"),
            ]

            all_devices = []

            for url, category in categories:
                print(f"Scraping category: {category} | URL: {url}")
                html_content = self.get_page(url, use_selenium=True)
                category_devices = self.parse_page(html_content)
                all_devices.extend(category_devices)

            return all_devices

        except Exception as e:
            print(f"Cashify scraper error: {str(e)}")
            return []
        finally:
            self.cleanup()

    def parse_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        devices = []

        device_containers = soup.select('a[href^="/buy-refurbished-"]')

        if not device_containers:
            print("No device containers found")
            return devices

        print(f"Found {len(device_containers)} device containers")

        for container in device_containers:
            try:
                name_element = container.select_one('h3.subtitle3')
                device_name = name_element.text.strip() if name_element else ""

                price_element = container.select_one('h3.h3')
                price_text = price_element.text.strip() if price_element else ""
                price_match = re.search(r'₹?([\d,]+)', price_text)
                price = float(price_match.group(1).replace(',', '')) if price_match else None

                if not device_name or not price:
                    continue

                condition = "Good" 
                brand = device_name.split()[0]
                model = extract_model(device_name)

                brand = normalize_brand(brand)
                condition = normalize_condition(condition)

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
        print(f"Returning {len(devices)}")
        return devices
