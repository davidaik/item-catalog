#!/system/bin/env python3

from flask import session as login_session
import random
import string



def get_signin_request_token():
    signin_request_token = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['signin_request_token'] = signin_request_token
    return login_session['signin_request_token']


def is_signed_in():
    return login_session.get('user_id') is not None