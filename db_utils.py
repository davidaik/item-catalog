#!/system/bin/env python3

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from db_init import DATABASE_NAME, Base, Role, User, Category, Item

import datetime

engine = create_engine(
    'postgresql+psycopg2://catuser:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def add_admin(email):
    admin = Role(email=email, role='admin')
    session.add(admin)
    session.commit()

def remove_admin(email):
    admin = session.query(Role).filter_by(email=email).one()
    session.delete(admin)
    session.commit()

def get_admins():
    return session.query(Role).all()

def get_admin(email):
    return session.query(Role).filter_by(email=email, role='admin').first()

def get_user(user_id):
    return session.query(User).filter_by(user_id=user_id).first()

def add_user(user_id, email, name):
    user = getUser(user_id)
    if user is not None:
        raise Exception('User already exists')
    user = User(user_id=user_id, email=email, name=name)
    session.add(user)
    session.commit()

# Categories

def add_category(name, desc):
    category = Category(name=name, desc=desc)
    session.add(category)
    session.flush()
    session.commit()
    return category

def update_category(id, name, desc):
    category = session.query(Category).filter_by(id=id).one()
    category.name = name
    category.desc = desc
    session.add(category)
    session.flush()
    session.commit()
    return category

def get_categories():
    return session.query(Category).all()

def get_category(id):
    return session.query(Category).filter_by(id=id).one()

def delete_category(id):
    category = getCategory(id)
    session.delete(category)
    session.commit()

# Items
def get_items(categoryId):
    if categoryId == 0:
        return session.query(Item).order_by(desc(Item.created_at)).all()
    return session.query(Item).filter_by(category_id=categoryId).order_by(desc(Item.created_at)).all()

def get_item(id):
    return session.query(Item).filter_by(id=id).one()

def add_item(name, desc, cat_id):
    category = session.query(Category).filter_by(id=cat_id).one()
    if not category:
        raise Exception('CATEGORY_NOT_EXIST')
    item = Item(name=name, desc=desc, short_desc=desc, category=category)
    session.add(item)
    session.flush()
    session.commit()
    return item

def update_item(id, name, desc, cat_id):
    item = session.query(Item).filter_by(id=id).one()
    category = session.query(Category).filter_by(id=cat_id).one()
    if not item:
        raise Exception('ITEM_NOT_EXIST')
    if not category:
        raise Exception('CATEGORY_NOT_EXIST')
    if item:
        item.name = name
        item.desc = desc
        item.short_desc = desc
        item.category = category
    session.add(item)
    session.flush()
    session.commit()
    return item

def delete_item(item):
    session.delete(item)
    session.commit()
