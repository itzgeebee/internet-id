from flask import (
    Blueprint, abort, jsonify, request
)

from src.helpers.check_valid_header import verify_token
from src.db import get_db
from src import current_app
from src.helpers.transform_respnses import (
    transform_user_response
)

bp = Blueprint('users', __name__, url_prefix='/api/v1/users')


@bp.route('/me/', methods=['GET'])
def get_me():
    auth_header = request.headers.get('Authorization')
    resp = verify_token(auth_header)
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM user WHERE user_id = %s", (resp,))
        user = cursor.fetchone()

        ids_cursor = db.cursor(dictionary=True)
        ids_cursor.execute("SELECT * FROM identity WHERE user_id = %s", (resp,))
        ids = ids_cursor.fetchall()
        products_cursor = db.cursor(dictionary=True)
        products_cursor.execute("SELECT * FROM business WHERE user_id = %s", (resp,))
        products = products_cursor.fetchall()

        if not user:
            abort(404, 'User not found')

        user_response = transform_user_response(user)
        user_response['identities'] = ids
        user_response['products'] = products
        return jsonify({
            'status': 'success',
            'data': user_response
        })
    except Exception as e:
        current_app.logger.error(e)
        abort(500, e.args)
    finally:
        cursor.close()
