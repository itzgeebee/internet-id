import re

from flask import (
    Blueprint, abort, jsonify, request, g
)
from flask_cors import CORS
from flask_expects_json import expects_json

from src.helpers.auth_tokens import encode_auth_token
from src.helpers.check_valid_header import verify_token, check_public_key
from src.db import get_db
from src import current_app
from src.helpers.isValidMail import validate_mail
from src.schema.schema import add_product_schema, update_product_schema

bp = Blueprint('products', __name__, url_prefix='/api/v1/products')
CORS(bp, resources={r"/api/*": {"origins": "*"}})


def build_sql_query(data, id, table_name):
    base_query = f"UPDATE {table_name} SET "
    query = ""
    query_params = []
    for key, values in data.items():
        query += f"{key} = %s, "
        query_params.append(values)
    query = query[:-2]
    query += f" WHERE id = %s"
    query_params.append(id)
    query = base_query + query
    return query, tuple(query_params)


def is_url(url):
    url_pattern = re.compile(
        r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\(["
        r"^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

    return bool(url_pattern.match(url))


@bp.route('/', methods=['POST'])
@expects_json(add_product_schema)
def add_product():
    auth_header = request.headers.get('Authorization')
    resp = verify_token(auth_header)

    data = g.data

    company_name = data.get('company_name', None)
    company_mail = data.get('company_mail', None)
    if not validate_mail(company_mail):
        abort(400, 'Invalid company mail')
    project_description = data.get('project_description', None)
    website_url = data.get('website_url', None)
    if not is_url(website_url):
        abort(400, 'Invalid url')
    business_type = data.get('business_type', None)
    private_key = data.get('private_key', None)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM user WHERE user_id = %s", (resp,))
        user = cursor.fetchone()
        if not user:
            return jsonify(
                {
                    "success": False,
                    "message": "User not found"
                }
            ), 404

        if user['private_key'] != private_key:
            return jsonify(
                {
                    "success": False,
                    "message": "Invalid private key"
                }
            ), 404

        cursor.execute(
            "INSERT INTO business (company_name, company_mail, project_description, website_url, business_type, user_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (company_name, company_mail, project_description, website_url, business_type, resp))
        db.commit()
    except Exception as e:
        current_app.logger.error(e.args[0])
        abort(422, e.args[1])
    finally:
        cursor.close()

    public_key = encode_auth_token(company_mail, 30)
    return jsonify({
        'status': 'success',
        'message': 'Product added successfully',
        'data': {
            'public_key': public_key
        }
    }), 201


@bp.route('/', methods=['GET'])
def get_products():
    auth_header = request.headers.get('Authorization')
    resp = verify_token(auth_header)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM business WHERE user_id = %s", (resp,))
        products = cursor.fetchall()

    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    else:
        return jsonify({
            'status': 'success',
            'data': products
        })
    finally:
        cursor.close()


@bp.route('/<int:product_id>/', methods=['PATCH'])
@expects_json(update_product_schema)
def update_product(product_id):
    auth_header = request.headers.get('Authorization')
    resp = verify_token(auth_header)

    data = g.data
    if data['company_mail']:
        if not validate_mail(data['company_mail']):
            abort(400, 'Invalid company mail format')

    if data == {}:
        abort(400, 'No data provided')

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        business_cursor = db.cursor(dictionary=True)
        business_cursor.execute("SELECT * FROM business WHERE user_id = %s", (resp,))
        business = business_cursor.fetchall()
        if not business:
            return jsonify(
                {
                    "success": False,
                    "message": "Product not found"
                }
            ), 404

        for product in business:
            if product['id'] == product_id:
                break
            else:
                return jsonify(
                    {
                        "success": False,
                        "message": "Product not found"
                    }
                ), 404

        query = build_sql_query(data, product_id, 'business')
        print(query)
        cursor.execute(query[0], query[1])

    except Exception as e:
        current_app.logger.error(e)
        abort(422, e.args[0])
    else:
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })

