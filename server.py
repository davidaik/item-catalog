#!/system/bin/env python3

from flask import Flask, request, redirect, url_for, render_template
import html
import calendar
import db_utils
import response

from flask import session as login_session
from flask import jsonify
import random
import string

from google.oauth2 import id_token
from google.auth.transport import requests
import json

import auth

app = Flask(__name__)

# The Google API client ID below is broken
# into multiple lines for pep8 compliance
CLIENT_ID = '{}{}'.format(
                        '692318378170-ufp0veeknbkbbu24er6h2g3n11c4govm',
                        '.apps.googleusercontent.com'
                    )


@app.route('/')
@app.route('/category/<int:category_id>', endpoint='category_page')
def get_index(category_id=0):
    categories = db_utils.get_categories()
    items = db_utils.get_items(category_id)
    page_title = 'Latest Items'
    if category_id != 0:
        category = db_utils.get_category(category_id)
        page_title = category.name
    for item in items:
        item.nice_date = '{month} {day}, {year}'.format(
            month=calendar.month_name[item.created_at.month],
            day=item.created_at.day,
            year=item.created_at.year)
    signed_in = auth.is_signed_in()
    is_user_admin = False
    if signed_in:
        is_user_admin = auth.is_user_admin()
    return render_template(
        'index.html',
        categories=categories,
        items=items,
        page_title=page_title,
        CLIENT_ID=CLIENT_ID,
        signed_in=signed_in,
        is_user_admin=is_user_admin,
        user_name=auth.get_user_name(),
        picture=auth.get_user_picture(),
        SIGNIN_REQUEST_TOKEN=auth.get_signin_request_token()
    )


@app.route('/category/new', methods=['GET', 'POST'])
@app.route('/category/<int:id>/edit', methods=['GET', 'POST'])
def get_edit_category_page(id=0):
    if request.method == 'GET':
        if not auth.is_user_admin():
            # Only admins can add and edit catories
            return render_template('unauthorized.html')
        if id and id != 0:
            # id is specified, render edit category page
            category = db_utils.get_category(id)
            return render_template(
                'edit-category.html',
                category=category,
                CLIENT_ID=CLIENT_ID,
                signed_in=auth.is_signed_in(),
                picture=login_session.get('picture')
            )
        else:
            return render_template(
                'edit-category.html',
                CLIENT_ID=CLIENT_ID,
                signed_in=auth.is_signed_in(),
                picture=login_session.get('picture')
            )
    elif request.method == 'POST':
        # This is meant to be reached from AJAX request.
        # We return a JSON response that will be used by
        # The JS code making the request.
        if not auth.is_user_admin():
            return response.error('Unauthorized')
        if request.form['name'] and request.form['desc']:
            if id and id != 0:
                # id is specified, update existing category
                category = db_utils.update_category(
                    id, request.form['name'], request.form['desc'])
                categoryData = {'id': category.id,
                                'name': category.name, 'desc': category.desc}
                return response.success(url_for('get_index'), categoryData)
            else:
                category = db_utils.add_category(
                    request.form['name'], request.form['desc'])
                categoryData = {'id': category.id,
                                'name': category.name, 'desc': category.desc}
                return response.success(url_for('get_index'), categoryData)


@app.route('/delete/category/<int:id>', methods=['POST'])
def post_delete_category(id):
    # This is meant to be reached from AJAX request.
    # We return a JSON response that will be used by
    # The JS code making the request.
    if not auth.is_user_admin():
        return response.error('Unauthorized')
    db_utils.delete_category(id)
    return response.success()


@app.route(
    '/item/new',
    methods=['GET', 'POST'],
    endpoint='new_item')
@app.route(
    '/item/<int:id>/edit',
    methods=['GET', 'POST'],
    endpoint='edit_item'
)
def get_edit_item_page(id=0):

    if request.method == 'GET':
        if not auth.is_signed_in():
            # Redirect to login page.
            # The url to which we are redirected will contain a paramenter
            # which will be the url to redirect back to
            # after logging in
            redirect_parameter = None
            if id and id != 0:
                redirect_parameter = 'redirect={}'.format(
                    url_for('edit_item', id=id))
            else:
                redirect_parameter = 'redirect={}'.format(url_for('new_item'))
                url = '{path}?{parameter}'.format(
                    path=url_for('get_login_page'),
                    parameter=redirect_parameter
                )
                return redirect(url, 302)
        categories = db_utils.get_categories()
        item = None
        if id and id != 0:
            item = db_utils.get_item(id)
            if item is None:
                return render_template('404.html')
            else:
                if (not auth.is_user_admin() and
                        item.user_id != auth.get_user_id()):
                    # Cannot edit item that does not belong to user
                    # But admins are allowed
                    return render_template('unauthorized.html')
        return render_template(
            'edit-item.html',
            item=item,
            categories=categories,
            CLIENT_ID=CLIENT_ID,
            signed_in=auth.is_signed_in(),
            user_name=auth.get_user_name(),
            picture=login_session.get('picture')
        )
    elif request.method == 'POST':
        # This is meant to be reached from AJAX request.
        # We return a JSON response that will be used by
        # The JS code making the request.
        if not auth.is_signed_in():
            return response.error('Unauthorized')

        if id and id != 0:
            # Update item
            item = db_utils.get_item(id)
            if (not auth.is_user_admin() and
                    item.user_id != auth.get_user_id()):
                # Only item owners and admins allowed to update item
                return response.error('Unauthorized')

            if (request.form['name'] and
                    request.form['desc'] and
                    request.form['cat-id']):
                item = db_utils.update_item(
                                    request.form['item-id'],
                                    request.form['name'],
                                    request.form['desc'],
                                    request.form['cat-id']
                                )
                itemData = {
                            'id': item.id,
                            'name': item.name,
                            'desc': item.desc,
                            'short_desc': item.short_desc,
                            'category_id': item.category_id
                            }
                return response.success(
                                        url_for(
                                            'get_item_page',
                                            id=itemData['id']
                                        ),
                                        itemData
                                    )
            else:
                return response.error('Failed to save')
        else:
            # Create new item
            if (request.form['name'] and
                    request.form['desc'] and
                    request.form['cat-id']):
                item = db_utils.add_item(
                    request.form['name'],
                    request.form['desc'],
                    request.form['cat-id'],
                    auth.get_user_id()
                )
                itemData = {
                            'id': item.id,
                            'name': item.name,
                            'desc': item.desc,
                            'short_desc': item.short_desc,
                            'category_id': item.category_id
                            }
                return response.success(
                                        url_for(
                                                'get_item_page',
                                                id=itemData['id']
                                        ),
                                        itemData
                                    )
            else:
                return response.error('Failed to save')


@app.route('/item/<int:id>', methods=['GET'])
def get_item_page(id):
    categories = db_utils.get_categories()
    item = db_utils.get_item(id)
    recent_items = db_utils.get_recent_items(5)
    if item is None:
        return render_template('404.html')
    item.nice_date = '{month} {day}, {year}'.format(
                        month=calendar.month_name[
                            item.created_at.month
                        ],
                        day=item.created_at.day,
                        year=item.created_at.year
                    )
    signed_in = auth.is_signed_in()
    is_user_admin = False
    is_item_owner = False
    if signed_in:
        is_user_admin = auth.is_user_admin()
        is_item_owner = item.user_id == auth.get_user_id()
    return render_template(
        'item.html',
        id=id,
        categories=categories,
        item=item,
        recent_items=recent_items,
        CLIENT_ID=CLIENT_ID,
        signed_in=signed_in,
        is_user_admin=is_user_admin,
        is_item_owner=is_item_owner,
        user_name=auth.get_user_name(),
        picture=login_session.get('picture'),
        SIGNIN_REQUEST_TOKEN=auth.get_signin_request_token()
    )


@app.route('/myitems')
@app.route('/user/<string:user_id>')
def get_my_items_page(user_id=0):
    if user_id == 0 and not auth.is_signed_in():
        # This would be reached when /myitems is requested.

        # Redirect to login page.
        # The url to which we are redirected will contain a paramenter
        # which will be the url to redirect back to
        # after logging in
        redirect_parameter = 'redirect={}'.format(url_for('get_my_items_page'))
        url = '{path}?{parameter}'.format(
            path=url_for('get_login_page'),
            parameter=redirect_parameter
        )
        return redirect(url, 302)
    page_title = 'My Items'
    if user_id != 0:
        user = db_utils.get_user(user_id)
        page_title = 'Items by {}'.format(user.name)
    categories = db_utils.get_categories()
    items = db_utils.get_user_items(user_id if user_id else auth.get_user_id())
    for item in items:
        item.nice_date = '{month} {day}, {year}'.format(
            month=calendar.month_name[item.created_at.month],
            day=item.created_at.day,
            year=item.created_at.year
        )
    signed_in = auth.is_signed_in()
    is_user_admin = False
    if signed_in:
        is_user_admin = auth.is_user_admin()
    return render_template(
        'index.html',
        page_title=page_title,
        categories=categories,
        items=items,
        CLIENT_ID=CLIENT_ID,
        signed_in=signed_in,
        is_user_admin=is_user_admin,
        user_name=auth.get_user_name(),
        picture=auth.get_user_picture(),
        SIGNIN_REQUEST_TOKEN=auth.get_signin_request_token()
    )


@app.route('/delete/item/<int:id>', methods=['POST'])
def post_delete_item(id):
    # This is meant to be reached from AJAX request.
    # We return a JSON response that will be used by
    # The JS code making the request.
    item = db_utils.get_item(id)
    db_utils.delete_item(item)
    return response.success()


@app.route('/login')
def get_login_page():
    return render_template(
                'login.html',
                CLIENT_ID=CLIENT_ID,
                SIGNIN_REQUEST_TOKEN=auth.get_signin_request_token())


@app.route('/signin', methods=['POST'])
def do_sign_in():
    # This is meant to be reached from AJAX request.
    # We return a JSON response that will be used by
    # The JS code making the request.
    if (request.form['signin_request_token'] !=
            login_session['signin_request_token']):
        return response.error('Invalid token.')

    g_id_token = request.form['id_token']
    try:
        idinfo = id_token.verify_oauth2_token(
            g_id_token, requests.Request(), CLIENT_ID)
        if (idinfo['iss'] not in
                ['accounts.google.com', 'https://accounts.google.com']):
            raise ValueError('Wrong issuer.')

        if idinfo['aud'] != CLIENT_ID:
            raise ValueError('Invalid client id.')

    except ValueError:
        return response.error('Could not sign in')

    user_id = idinfo['sub']

    stored_id_token = login_session.get('id_token')
    stored_user_id = login_session.get('user_id')

    user = db_utils.get_user(user_id)
    if user is None:
        # Add user to database if id does not exist.
        db_utils.add_user(user_id, idinfo['email'], idinfo['name'])

    if stored_id_token is not None and stored_user_id == user_id:
        return response.success()

    # Store the access token in the session for later use.
    login_session['id_token'] = g_id_token
    login_session['user_id'] = user_id
    login_session['name'] = idinfo['name']
    login_session['email'] = idinfo['email']
    login_session['picture'] = idinfo['picture']
    return response.success()


@app.route('/signout', methods=['POST'])
def do_sign_out():
    login_session.clear()
    return response.success()


# JSON endpoints
@app.route('/items.json')
def get_all_items_json():
    items = db_utils.get_items(0)
    item_list = []
    for item in items:
        item_list.append({
            'id': item.id,
            'name': item.name,
            'created_at': item.created_at,
            'updated_at': item.updated_at,
            'category_id': item.category_id,
            'category_name': item.category.name,
            'user_id': item.user_id,
            'short_desc': item.short_desc,
            'desc': item.desc
        })
    return jsonify(item_list), 200


@app.route('/item.json')
def get_item_json():
    id = request.args.get('id')
    if not id:
        return response.error('Item id not specified.')

    item = db_utils.get_item(id)
    item_dict = {
        'id': item.id,
        'name': item.name,
        'created_at': item.created_at,
        'updated_at': item.updated_at,
        'category_id': item.category_id,
        'category_name': item.category.name,
        'user_id': item.user_id,
        'short_desc': item.short_desc,
        'desc': item.desc
    }
    return jsonify(item_dict), 200


if __name__ == '__main__':
    app.secret_key = 'wQwroWyX"uq<hRC'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=False)
