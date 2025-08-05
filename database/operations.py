from .models import DeviceData, DBManager
from config import DATABASE_URL
from datetime import datetime, timedelta
import pandas as pd

db_manager = DBManager(DATABASE_URL)

def add_device_prices(devices):
    session = db_manager.get_session()
    try:
        added_count = 0
        for device in devices:
            try:
                # Check if device already exists in the last 24 hours
                existing = session.query(DeviceData).filter(
                    DeviceData.source == device['source'],
                    DeviceData.brand == device['brand'],
                    DeviceData.model == device['model'],
                    DeviceData.condition == device['condition'],
                    DeviceData.price == device['price'],
                    DeviceData.date_scraped >= datetime.utcnow() - timedelta(hours=24)
                ).first()
                
                if not existing:
                    new_device = DeviceData(
                        source=device['source'],
                        brand=device['brand'],
                        model=device['model'],
                        condition=device['condition'],
                        price=device['price']
                    )
                    session.add(new_device)
                    added_count += 1
            except Exception as e:
                print(f"Error adding device: {device.get('model', 'Unknown')}")
                print(f"Error details: {str(e)}")

        session.commit()
        print(f"Successfully added {added_count} devices to database")
        return added_count

    except Exception as e:
        session.rollback()
        print(f"Database commit failed: {str(e)}")
        return 0

    finally:
        session.close()


def get_latest_prices(days=1):
    session = db_manager.get_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        results = session.query(DeviceData).filter(
            DeviceData.date_scraped >= cutoff_date
        ).all()
        return results
    finally:
        session.close()

def get_all_data():
    session = db_manager.get_session()
    try:
        results = session.query(DeviceData).all()
        return results
    finally:
        session.close()


def to_dataframe(query_result):
    if not query_result:
        return pd.DataFrame(columns=[
            'id', 'source', 'brand', 'model', 'condition', 'price', 'date_scraped'
        ])
    
    data = [{
        'id': item.id,
        'source': item.source,
        'brand': item.brand,
        'model': item.model,
        'condition': item.condition,
        'price': item.price,
        'date_scraped': item.date_scraped
    } for item in query_result]
    
    return pd.DataFrame(data)

def get_db_manager():
    return db_manager
