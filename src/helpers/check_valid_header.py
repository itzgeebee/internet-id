from flask import abort

from src.helpers.auth_tokens import decode_auth_token
from src.helpers.errors import invalid_token_response


def check_valid_header(header):
    if not header:
        return False
    if not header.startswith("Bearer "):
        return False
    auth_token = header.split(" ")[1]

    return auth_token


def check_public_key(public_key):
    return decode_auth_token(public_key)


def verify_token(auth_header):
    resp = check_valid_header(auth_header)
    if not resp:
        abort(401, 'Invalid token. Please log in again.')

    decoded_token = decode_auth_token(resp)
    return decoded_token
