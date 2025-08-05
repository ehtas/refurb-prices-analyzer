from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class DeviceData(Base):
    __tablename__ = 'device_data'  

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    date_scraped = Column(DateTime, default=datetime.utcnow)

    
    def __repr__(self):
        return f"<DevicePrice({self.source}, {self.brand} {self.model}, ₹{self.price})>"

class DBManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def get_session(self):
        return self.Session()