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


def addAdmin(email):
    admin = Role(email=email, role='admin')
    session.add(admin)
    session.commit()

def removeAdmin(email):
    admin = session.query(Role).filter_by(email=email).one()
    session.delete(admin)
    session.commit()

def getAdmins():
    return session.query(Role).all()

def getUser(user_id):
    return session.query(User).filter_by(user_id=user_id).first()

def addUser(user_id, email, name):
    user = getUser(user_id)
    if user is not None:
        raise Exception('User already exists')
    user = User(user_id=user_id, email=email, name=name)
    session.add(user)
    session.commit()

# Categories

def addCategory(name, desc):
    category = Category(name=name, desc=desc)
    session.add(category)
    session.flush()
    session.commit()
    return category

def updateCategory(id, name, desc):
    category = session.query(Category).filter_by(id=id).one()
    category.name = name
    category.desc = desc
    session.add(category)
    session.flush()
    session.commit()
    return category

def getCategories():
    return session.query(Category).all()

def getCategory(id):
    return session.query(Category).filter_by(id=id).one()

def deleteCategory(id):
    category = getCategory(id)
    session.delete(category)
    session.commit()

# Items
def getItems(categoryId):
    if categoryId == 0:
        return session.query(Item).order_by(desc(Item.created_at)).all()
    return session.query(Item).filter_by(category_id=categoryId).order_by(desc(Item.created_at)).all()

def getItem(id):
    return session.query(Item).filter_by(id=id).one()

def addItem(name, desc, cat_id):
    category = session.query(Category).filter_by(id=cat_id).one()
    if not category:
        raise Exception('CATEGORY_NOT_EXIST')
    item = Item(name=name, desc=desc, short_desc=desc, category=category)
    session.add(item)
    session.flush()
    session.commit()
    return item

def updateItem(id, name, desc, cat_id):
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

def deleteItem(item):
    session.delete(item)
    session.commit()
