from flask import (
    Blueprint, abort, jsonify, request, g
)
from flask_cors import CORS
from flask_expects_json import expects_json

from src.helpers.check_valid_header import verify_token, check_public_key
from src.db import get_db
from src import current_app
from src.helpers.transform_respnses import (
    transform_user_response
)
from src.schema.schema import verify_schema

bp = Blueprint('verify', __name__, url_prefix='/api/v1/verify')
CORS(bp)


@bp.route('/', methods=['POST'])
@expects_json(verify_schema)
def verify():
    public_key = request.args.get('pub-key', None)
    if not public_key:
        abort(400, 'Missing public key parameter')
    company_mail = check_public_key(public_key)
    customer = None
    means_of_verification = None
    data = g.data

    private_key = data.get('private_key', None)
    internet_id = data.get('internet_id', None)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM user WHERE private_key = %s", (private_key,))
        user = cursor.fetchone()

        if not user:
            return jsonify(
                {
                    "success": False,
                    "message": "Invalid private key"
                }
            ), 401

        cursor.execute("SELECT * FROM business WHERE user_id = %s", (user["user_id"],))
        business = cursor.fetchall()

        if not business:
            return jsonify(
                {
                    "success": False,
                    "message": "Your company/product has not been registered with us"
                }
            ), 404

        for b in business:
            if b["company_mail"] == company_mail:
                break
            else:
                return jsonify(
                    {
                        "success": False,
                        "message": "Your company/product has not been registered with us"
                    }
                ), 404

        cursor.execute("SELECT * FROM user WHERE internet_id = %s", (internet_id,))

        customer = cursor.fetchone()
        if not customer:
            return jsonify(
                {
                    "success": True,
                    "message": "This user has not been verified with us",
                    "verified": False
                }
            )
        cursor.execute("SELECT * FROM identity WHERE user_id = %s", (customer["user_id"],))
        identity = cursor.fetchone()
        means_of_verification = identity.keys()


    except Exception as e:
        current_app.logger.error(e)
        abort(500, e.args)

    else:
        return jsonify(
            {
                "success": True,
                "message": "This user has been verified with us",
                "verified": True,
                "data": {
                    "verified_with": list(means_of_verification)[2:]
                }
            }
        )
    finally:
        cursor.close()
