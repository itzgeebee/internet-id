import datetime

import jwt
from flask import abort

from src import current_app
from src.db import get_db


def check_blacklist(auth_token):
    # check whether auth token has been blacklisted
    db = get_db()
    cursor = db.cursor()
    query = "SELECT * FROM blacklisted_token WHERE token = %s"
    cursor.execute(query, (auth_token,))
    result = cursor.fetchone()
    if result:
        return True
    return False


def encode_auth_token(user_id, exp=7):
    """
    Generates the Auth Token
    :param user_id: integer | string  - user_id
    :return: string
    """

    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=exp),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )
    except Exception as e:
        current_app.logger.error(e)
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """

    try:

        is_blacklisted_token = check_blacklist(auth_token)
        if is_blacklisted_token:
            abort(401, 'Token blacklisted. Please log in again.')

        payload = jwt.decode(auth_token,
                             algorithms="HS256",
                             key=current_app.config.get('SECRET_KEY'))
        return payload['sub']
    except jwt.ExpiredSignatureError:
        abort(401, 'Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        abort(401, 'Invalid token. Please log in again.')


def check_valid_header(header):
    if not header:
        return False
    if not header.startswith("Bearer "):
        return False
    auth_token = header.split(" ")[1]

    return auth_token
