#!/system/bin/env python3
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

DATABASE_NAME = 'database'

def get_time():
    return datetime.datetime.now()


class Role(Base):
    __tablename__ = 'role'

    id = Column(
        Integer, primary_key=True
    )

    email = Column(
        String(250), nullable=False
    )

    role = Column(
        String(20), nullable=False
    )


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    desc = Column(String(250), nullable=False)

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    desc = Column(String(250), nullable=False)
    short_desc = Column(String(250), nullable=False)
    created_at = Column(DateTime, default=get_time)
    updated_at = Column(DateTime, onupdate=get_time)
    category = relationship('Category', backref='item')
    category_id = Column(Integer, ForeignKey('category.id'), nullable=True)
    nice_date = ""



engine = create_engine(
    'postgresql+psycopg2://catuser:catalog@localhost/catalog'
)
Base.metadata.create_all(engine)
