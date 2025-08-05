import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = "sqlite:///create_a_db_file_in_root"

# Scraper configurations
SCRAPER_CONFIG = {
    "cashify": {
        "base_url": "https://www.cashify.in"
    },
    "refitGlobal":{
        "base_url": "https://refitglobal.com/"
    },
    "mobilegoo": {
        "base_url": "https://mobilegoo.shop"
    },
    "flipkart": {
        "base_url": "https://www.flipkart.com/search?q=refurbished+mobiles"
    },
    "quikr": {
        "base_url": "https://www.quikr.com/mobiles-tablets/Mobile-Phones+India+y149f"
    },
    "maple": {
        "base_url": "https://www.maplestore.in"
    }
}



# User authentication (simple demo)
USERS = {
    "admin": "admin123",
    "user": "user123"
}
AMAZON_API_KEY = ""
