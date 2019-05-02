#!/system/bin/env python3
from flask import jsonify

def success(redirect_url='/', item_data={}):
    response = {}
    response['error'] = False
    response['redirect_url'] = redirect_url
    response['item_data'] = item_data  # Contains data of item updated/added to the db
    return jsonify(response), 200

def error(message):
    response = {}
    response['error'] = True
    response['message'] = message
    return jsonify(response), 400
