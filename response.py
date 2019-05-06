#!/system/bin/env python3
# These functions are meant to be used to create response
# for AJAX requests such as while saving category or item.

from flask import jsonify


def success(redirect_url='/', item_data={}):
    response = {}
    response['error'] = False
    response['redirect_url'] = redirect_url

    # Include the item that was just updated
    response['item_data'] = item_data
    return jsonify(response), 200


def error(message):
    response = {}
    response['error'] = True
    response['message'] = message
    return jsonify(response), 400
