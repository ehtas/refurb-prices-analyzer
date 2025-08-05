import streamlit as st
from database import operations as db_ops
from scraper.cashify import CashifyScraper
from scraper.maple import MapleScraper
from scraper.refitglobal import RefitScraper
from scraper.mobilegoo import MobileGooScraper
from scraper.amazon import AmazonRenewedScraper
from scraper.flipkart import FlipkartScraper
from scraper.quikr import QuikrScraper
import pandas as pd
import plotly.express as px
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os
from config import USERS
from database.operations import get_db_manager, add_device_prices, get_all_data, to_dataframe
from database.models import Base

# Initialize database manager
db_manager = get_db_manager()
# Page configuration
st.set_page_config(
    page_title="Refurb Price Analyzer",
    page_icon="📱",
    layout="wide"
)

# Authentication
def authenticate(username, password):
    return username in USERS and USERS[username] == password

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login form
if not st.session_state.authenticated:
    st.title("Refurbished Device Price Analyzer")
    st.subheader("Please log in to access the dashboard")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password")
    st.stop()

# Main application
st.title("📱 Refurbished Device Price Analyzer")
st.markdown("Track and compare prices across refurbished device marketplaces")

# Scraper functions
def run_cashify_scraper():
    scraper = CashifyScraper()
    return scraper.scrape()

def run_maple_scraper():
    scraper = MapleScraper()
    return scraper.scrape()

def run_refit_scraper():
    scraper = RefitScraper()
    return scraper.scrape()
    
def run_mobilegoo_scraper():    
    scraper = MobileGooScraper()
    return scraper.scrape()
    
def run_amazon_scraper():    
    scraper = AmazonRenewedScraper()
    return scraper.scrape()
    
def run_flipkart_scraper():
    scraper = FlipkartScraper()
    return scraper.scrape()

def run_quikr_scraper():
    scraper = QuikrScraper()
    return scraper.scrape()
    
SCRAPERS = {
    "Cashify": run_cashify_scraper,
    "Maple": run_maple_scraper,
    "RefitGlobal": run_refit_scraper,
    "MobileGoo": run_mobilegoo_scraper,
    "Amazon": run_amazon_scraper,
    "Flipkart": run_flipkart_scraper,
    "Quikr": run_quikr_scraper,
}

def run_all_scrapers():
    with st.spinner("Running scrapers... This may take a few minutes"):
        cashify_devices = run_cashify_scraper()
        maple_devices = run_maple_scraper()
        refit_devices = run_refit_scraper()
        mobilegoo_devices = run_mobilegoo_scraper()
        amazon_devices = run_amazon_scraper()
        flipkart_devices = run_flipkart_scraper()
        quikr_devices = run_quikr_scraper()
        
        all_devices = cashify_devices + maple_devices + refit_devices + mobilegoo_devices + amazon_devices + flipkart_devices + quikr_devices
        added_count = db_ops.add_device_prices(all_devices)
        
        st.success(f"Added {added_count} new records!")
        time.sleep(2)
        st.rerun()

# Scheduler setup
if 'scheduler_started' not in st.session_state:
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_all_scrapers, 'interval', hours=24)
    scheduler.start()
    st.session_state.scheduler_started = True
    
all_data = db_ops.get_all_data()
df = db_ops.to_dataframe(all_data)


# Sidebar controls
with st.sidebar:
    st.header("Controls")
    
    if st.button("Run All Scrapers Now"):
        run_all_scrapers()
        
    st.markdown("---")
    st.markdown("### Run Individual Scraper")
    for name, fn in SCRAPERS.items():
        with st.container():
            col1, col2 = st.columns([0.7, 0.3])
            run_key = f"btn_{name}"
            run = col2.button(f"▶️ Run", key=run_key)

            col1.markdown(f"**📦 {name} Scraper**")

            if run:
                # Render spinner below
                with st.spinner(f"Running {name}…"):
                    devices = fn()
                    added_count = db_ops.add_device_prices(devices)
                    st.success(f"✅ Added {added_count} new records from {name}")
                    time.sleep(2)
                    st.rerun()



    st.markdown("---")
    st.header("Filters")
    
    # Source filter
    sources = st.multiselect(
        "Select Sources", 
        ["Cashify", "Maple","RefitGlobal","MobileGoo","AmazonRenewed","Flipkart","Quikr"], 
        default=["Cashify", "Maple"]
    )
    
    # Brand filter
    if not df.empty and 'brand' in df.columns:
        unique_brands = ["All"] + sorted(df['brand'].unique().tolist())
    else:
        unique_brands = ["All"]
        st.warning("No device data found in the database. Please run scrapers first.")
    selected_brand = st.selectbox("Filter by Brand", unique_brands)
    
    # Condition filter
    conditions = ["All", "Excellent", "Good", "Fair", "Poor"]
    selected_condition = st.selectbox("Filter by Condition", conditions)
    
    # Date filter
    min_date = df['date_scraped'].min() if not df.empty else datetime.now()
    max_date = df['date_scraped'].max() if not df.empty else datetime.now()
    date_range = st.date_input(
        "Date Range", 
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    
    # Apply filters early
    filtered_df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(filtered_df['date_scraped']):
        filtered_df['date_scraped'] = pd.to_datetime(filtered_df['date_scraped'], errors='coerce')
    if selected_brand != "All":
        filtered_df = filtered_df[filtered_df['brand'] == selected_brand]
    if selected_condition != "All":
        filtered_df = filtered_df[filtered_df['condition'] == selected_condition]
    if sources:
        filtered_df = filtered_df[filtered_df['source'].isin(sources)]
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['date_scraped'].dt.date >= start_date) &
            (filtered_df['date_scraped'].dt.date <= end_date)
        ]
    st.markdown("---")
    # Export and Download CSV 
    if st.button("Export to CSV"):
        with st.spinner("Preparing CSV..."):
            csv = filtered_df.to_csv(index=False)
            st.success("✅ Ready! Click below to download.")
            st.download_button("📥 Download Filtered CSV", csv, "refurb_prices_filtered.csv", "text/csv")


 
if st.sidebar.checkbox("Show Database Info"):
    # Show table structure
    st.subheader("Database Schema")
    from database.models import DevicePrice
    from sqlalchemy.inspection import inspect
    inspector = inspect(db_manager.engine)
    columns = inspector.get_columns('device_prices')
    st.table([{"Column": col['name'], "Type": col['type']} for col in columns])
    # Show row count
    session = db_manager.get_session()
    try:
        count = session.query(DevicePrice).count()
        st.write(f"Total records: {count}")
        # Show first 5 records
        if count > 0:
            st.subheader("Sample Records")
            sample = session.query(DevicePrice).limit(5).all()
            sample_data = [{
                'id': r.id,
                'source': r.source,
                'brand': r.brand,
                'model': r.model,
                'price': r.price,
                'date': r.date_scraped
            } for r in sample]
            st.table(sample_data)
    finally:
        session.close()
if st.sidebar.button("Reset Database"):
    session = db_manager.get_session()
    try:
        Base.metadata.drop_all(db_manager.engine)
        Base.metadata.create_all(db_manager.engine)
        st.sidebar.success("Database reset complete")
    except Exception as e:
        st.sidebar.error(f"Reset failed: {str(e)}")
    finally:
        session.close()
    time.sleep(2)
    st.rerun()
    
# Main dashboard
if not df.empty:
    # Apply filters
    if selected_brand != "All":
        df = df[df['brand'] == selected_brand]
    if selected_condition != "All":
        df = df[df['condition'] == selected_condition]
    if sources:
        df = df[df['source'].isin(sources)]
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['date_scraped'].dt.date >= start_date) & 
                (df['date_scraped'].dt.date <= end_date)]
    
    # Display data
    st.header("Latest Prices")
    st.dataframe(df.sort_values('date_scraped', ascending=False))
    
    # Price analysis
    st.header("Price Analysis")
    
    # Comparison with Maple
    if 'Maple' in sources:
        st.subheader("Price Comparison vs Maple")
        
        # Get Maple prices as baseline
        maple_prices = df[df['source'] == 'Maple']
        
        # Merge with other prices
        comparison_df = pd.merge(
            df[df['source'] != 'Maple'],
            maple_prices[['brand', 'model', 'price']],
            on=['brand', 'model'],
            suffixes=('', '_maple'),
            how='inner'
        )

        
        if not comparison_df.empty:
            # Calculate percentage difference
            comparison_df['percent_diff'] = (
            (comparison_df['price'] - comparison_df['price_maple']) / 
            comparison_df['price_maple'] * 100
            ).round(2)
            
            # Format results
            comparison_df = comparison_df[[
                'id','source', 'brand', 'model', 'condition', 
                'price', 'price_maple', 'percent_diff'
            ]]
            
            # Display comparison table
            st.dataframe(comparison_df.sort_values('percent_diff', ascending=False).reset_index(drop=True))
            
            # Best price suggestions
            st.subheader("Best Price Suggestions")
            
            # Find the best offer for each device
            best_offers = comparison_df.loc[
                comparison_df.groupby(['brand', 'model', 'condition'])['percent_diff'].idxmax()
            ]
            
            for _, row in best_offers.iterrows():
                if row['percent_diff'] > 0:
                    st.success(
                        f"Sell **{row['brand']} {row['model']}** ({row['condition']}) to "
                        f"**{row['source']}** - **{row['percent_diff']:.1f}%** higher than Maple "
                        f"(₹{row['price']} vs ₹{row['price_maple']})"
                    )
                else:
                    st.warning(
                        f"Maple offers better price for **{row['brand']} {row['model']}** "
                        f"({row['condition']}) by **{abs(row['percent_diff']):.1f}%**"
                    )
            
            # Visualization
            st.subheader("Price Comparison Chart")
            fig = px.bar(
                comparison_df,
                x='model',
                y='percent_diff',
                color='source',
                barmode='group',
                title='Price Difference vs Maple (%)',
                labels={'percent_diff': 'Price Difference (%)', 'model': 'Device Model'},
                hover_data=['price', 'price_maple']
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No comparable data found. Try expanding your filters.")
    else:
        st.warning("Include Maple in your sources to enable price comparisons")
else:
    st.warning("No data available. Run scrapers to collect pricing data.")

