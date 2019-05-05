#!/system/bin/env python3

from flask import Flask, request, redirect, url_for, render_template
import html
import calendar
import db_utils
import response

from flask import session as login_session
from flask import make_response
import random
import string

from google.oauth2 import id_token
from google.auth.transport import requests
import json

import auth

app = Flask(__name__)

CLIENT_ID = 'YOUR GOOGLE SIGNIN API CLIENT ID HERE'

@app.route('/')
@app.route('/category/<int:categoryId>')
def getIndex(categoryId=0):
    categories = db_utils.getCategories()
    items = db_utils.getItems(categoryId)
    for item in items:
        item.nice_date = '{month} {day}, {year}'.format(
            month=calendar.month_name[item.created_at.month], day=item.created_at.day, year=item.created_at.year)
    return render_template('index.html', categories=categories, items=items, CLIENT_ID=CLIENT_ID, signed_in=auth.is_signed_in())


@app.route('/category/new', methods=['GET', 'POST'])
@app.route('/category/<int:id>/edit', methods=['GET', 'POST'])
def getEditCategoryPage(id=0):
    if request.method == 'GET':
        if id and id != 0:
            # id is specified, render edit category page
            category = db_utils.getCategory(id)
            return render_template('edit-category.html', category=category)
        else:
            return render_template('edit-category.html')
    elif request.method == 'POST':
        if request.form['name'] and request.form['desc']:
            if id and id != 0:
                # id is specified, update existing category
                category = db_utils.updateCategory(
                    id, request.form['name'], request.form['desc'])
                categoryData = {'id': category.id,
                                'name': category.name, 'desc': category.desc}
                return response.success(url_for('getIndex'), categoryData)
            else:
                category = db_utils.addCategory(
                    request.form['name'], request.form['desc'])
                categoryData = {'id': category.id,
                                'name': category.name, 'desc': category.desc}
                return response.success(url_for('getIndex'), categoryData)


@app.route('/delete/category/<int:id>', methods=['POST'])
def postDeleteCategory(id):
    db_utils.deleteCategory(id)
    return response.success()


@app.route('/item/new', methods=['GET', 'POST'])
@app.route('/item/<int:id>/edit', methods=['GET', 'POST'])
def getEditItemPage(id=0):
    if not auth.is_signed_in():
        return redirect(url_for('showLogin'))
        
    if request.method == 'GET':
        if id and id != 0:
            # id is specified, render edit item page
            item = db_utils.getItem(id)
            categories = db_utils.getCategories()
            return render_template('edit-item.html', item=item, categories=categories)
        else:
            # id is not specified, render new item page
            categories = db_utils.getCategories()
            return render_template('edit-item.html', categories=categories)
    elif request.method == 'POST':
        if id and id != 0:
            if request.form['name'] and request.form['desc'] and request.form['cat-id']:
                item = db_utils.updateItem(
                    request.form['item-id'], request.form['name'], request.form['desc'], request.form['cat-id'])
                itemData = {'id': item.id, 'name': item.name, 'desc': item.desc,
                            'short_desc': item.short_desc, 'category_id': item.category_id}
                return response.success(url_for('getItemPage', id=itemData['id']), itemData)
            else:
                return "ERROR"
        else:
            if request.form['name'] and request.form['desc'] and request.form['cat-id']:
                item = db_utils.addItem(
                    request.form['name'], request.form['desc'], request.form['cat-id'])
                itemData = {'id': item.id, 'name': item.name, 'desc': item.desc,
                            'short_desc': item.short_desc, 'category_id': item.category_id}
                return response.success(url_for('getItemPage', id=itemData['id']), itemData)
            else:
                return "ERROR"


@app.route('/item/<int:id>', methods=['GET'])
def getItemPage(id):
    categories = db_utils.getCategories()
    item = db_utils.getItem(id)
    return render_template('item.html', id=id, categories=categories, item=item)


@app.route('/delete/item/<int:id>', methods=['POST'])
def postDeleteItem(id):
    item = db_utils.getItem(id)
    db_utils.deleteItem(item)
    return response.success()


@app.route('/login')
def showLogin():
    signin_request_token = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['signin_request_token'] = signin_request_token
    return render_template('login.html', CLIENT_ID=CLIENT_ID, SIGNIN_REQUEST_TOKEN=login_session['signin_request_token'])

def makeToken():
    signin_request_token = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['signin_request_token'] = signin_request_token
    return login_session['signin_request_token']

def isLoggedIn():
    return 'userid' in login_session


@app.route('/signin', methods=['POST'])
def signIn():
    signin_request_token = request.form['signin_request_token']

    if request.form['signin_request_token'] != login_session['signin_request_token']:
        response = make_response(json.dumps('Invalid token.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    g_id_token = request.form['id_token']
    try:
        idinfo = id_token.verify_oauth2_token(g_id_token, requests.Request(), CLIENT_ID)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        if idinfo['aud'] != CLIENT_ID:
            raise ValueError('Invalid client id.')
        
    except ValueError:
        pass

    user_id = idinfo['sub']

    print('user id: {}'.format(user_id))
    print('email: {}'.format(idinfo['email']))
    print('name: {}'.format(idinfo['name']))

    stored_id_token = login_session.get('id_token')
    stored_user_id = login_session.get('user_id')
    if stored_id_token is not None and stored_user_id == user_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    user = db_utils.getUser(user_id)
    if user is None:
        db_utils.addUser(user_id, idinfo['email'], idinfo['name'])
        print('added user to database!')

    # Store the access token in the session for later use.
    login_session['id_token'] = g_id_token
    login_session['user_id'] = user_id
    return ""

@app.route('/signout', methods=['POST'])
def signOut():
    login_session.clear()
    return ""

if __name__ == '__main__':
    app.secret_key = 'wQwroWyX"uq<hRC'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
