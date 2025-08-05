import re
import requests
from .base_scraper import BaseScraper
from utils.normalization import normalize_brand, normalize_condition, extract_model
from config import AMAZON_API_KEY

class AmazonRenewedScraper(BaseScraper):
    def __init__(self):
        super().__init__("AmazonRenewed")
        self.api_endpoint = "https://serpapi.com/search.json"
        self.params = {
            "engine": "amazon",
            "k": "renewed phone",          # keyword
            "amazon_domain": "amazon.in",  # India marketplace
            "api_key": AMAZON_API_KEY,
        }

    def scrape(self):
        try:
            print(f"🔍 Fetching from SerpApi: {self.api_endpoint}")
            response = requests.get(self.api_endpoint, params=self.params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "organic_results" not in data:
                print("⚠️ No 'organic_results' found in response")
                return []

            return self.parse_api_response(data["organic_results"])

        except Exception as e:
            print(f"❌ SerpApi error: {e}")
            return []

    def parse_api_response(self, items):
        print(f"📦 Found {len(items)} items from Amazon Renewed via SerpApi")

        devices = []
        for item in items:
            try:
                title = item.get("title", "").strip()
                price_str = item.get("price", "").replace("₹", "").replace(",", "").strip()
                price = float(re.search(r'\d+(\.\d+)?', price_str).group()) if price_str else None

                if not title or price is None:
                    continue

                brand = normalize_brand(title)
                model = re.split(r'[\(|\||,]', extract_model(title), maxsplit=1)[0].strip()

                condition = normalize_condition("Renewed")

                devices.append({
                    "source": self.source_name,
                    "brand": normalize_brand(brand),
                    "model": model,
                    "condition": condition,
                    "price": price,
                })
            except Exception as e:
                print(f"⚠️ Error parsing item: {e}")
        print(f"Returning {len(devices)}")
        return devices
