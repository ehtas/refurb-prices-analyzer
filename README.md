# Refurbished Device Price Analyzer

Track and compare prices of refurbished devices across multiple marketplaces.

## Features

- Scrape pricing data from competitor websites
- Store data in SQLite database
- Streamlit dashboard for data visualization
- Price comparison with Maple Store
- Best price suggestions
- Scheduled daily scraping

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ehtas/refurb-prices-analyzer.git
   cd refurb-prices-analyzer
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration Instructions:**

- No need to configure environment variables or Streamlit secrets.
- Rename `config_template.py` to `config.py` and add your Amazon API key to the `AMAZON_API_KEY` variable.
- Create an empty SQLite database file named `market.db` in the root folder (same directory as `app.py`).


6. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Usage

1. Access the Streamlit app at `http://localhost:8501`
2. Login with credentials (default: admin/admin123 or user/user123)
3. Click "Run All Scrapers Now" to collect initial data
4. Use filters to analyze specific devices
5. View price comparisons and selling suggestions

## Scraper Notes

- Currently implemented scrapers: Cashify, Maple, RefitGlobal, MobileGoo, Amazon, Flipkart, Quikr
- To add more scrapers:
  1. Create a new file in `scraper/` directory
  2. Extend the `BaseScraper` class
  3. Implement `scrape()` and `parse_page()` methods
  4. Add the scraper to `app.py`
