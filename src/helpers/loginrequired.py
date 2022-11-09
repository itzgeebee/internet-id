from functools import wraps

from flask import request, jsonify

from src.helpers.auth_tokens import decode_auth_token


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return jsonify({
                'status': 'fail',
                'message': 'Authorization header is missing'
            }), 401
        access_token = request.headers['Authorization']
        try:
            user_id = decode_auth_token(access_token)
        except Exception as e:
            return jsonify({
                'status': 'fail',
                'message': e.args
            }), 401
        return f(user_id, *args, **kwargs)

    return decorated_function
