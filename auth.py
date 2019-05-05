#!/system/bin/env python3

from flask import session as login_session

def is_signed_in():
    return login_session.get('user_id') is not None