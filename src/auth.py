from datetime import datetime
import re
from threading import Thread
import secrets

from flask import (
    Blueprint, g, abort, jsonify, request
)
from flask_cors import CORS

from src.helpers.auth_tokens import encode_auth_token, check_valid_header
from src.helpers.check_valid_header import verify_token
from src.helpers.isValidMail import validate_mail
from src.schema.schema import auth_schema, login_schema
from src.db import get_db
from src import bcrypt, sender, current_app, limiter
from flask_expects_json import expects_json
from src.helpers.transform_respnses import (
    transform_user_response
)
from verify_user.isVerified import verify_ids as is_verified

from flask_mail import Message

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

CORS(bp)


def send_mail(app, msg):
    with app:
        sender.send(msg)


@bp.route('/register/', methods=['POST'])
@limiter.limit("5 per minute")
@expects_json(auth_schema)
def register():
    data = g.data
    private_key = None
    first_name = data['first_name']
    last_name = data['last_name']
    password = bcrypt.generate_password_hash(data['password'], 12).decode('utf-8')
    email = data['email']
    phone_number = data['phone_number']
    date_of_birth = data['date_of_birth']
    gender = data['gender']
    country = data['country']
    internet_id = bcrypt.generate_password_hash(f"{first_name}{last_name}{date_of_birth}").decode('utf-8')
    international_id = data.get('international_id', None)
    bank_verification_num = data.get('bank_verification_num', None)
    image_id = data.get('image_id', None)
    is_dev = data.get('is_dev', False)

    if not validate_mail(email):
        abort(400, 'Invalid email address format')

    if bank_verification_num:
        print("bvn")
        verified = is_verified(id_type="bank_verification_num",
                               identities={"bank_verification_num": bank_verification_num},
                               first_name=first_name, last_name=last_name, email=email,
                               phone=phone_number,
                               dob=datetime.strptime(date_of_birth, '%Y-%m-%d').strftime('%d-%b-%Y'))

        if not verified[0]:
            abort(401, verified[1])
    elif international_id:
        verified = is_verified(id_type="international_id",
                               identities={"international_id": international_id},
                               last_name=last_name)
        if not verified[0]:
            abort(401, verified[1])

    if is_dev:
        private_key = secrets.token_urlsafe()

    db = get_db()
    cursor = db.cursor(dictionary=True)
    identity_cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            'INSERT INTO user'
            '(first_name, last_name, password, email, phone_number, date_of_birth, gender, country, internet_id, is_dev, private_key) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
            (first_name, last_name, password, email, phone_number, date_of_birth, gender, country, internet_id, is_dev,
             private_key))

        identity_cursor.execute(
            'INSERT INTO identity'
            '(international_id, bank_verification_num, image_id, user_id) '
            'VALUES (%s, %s, %s, %s)',
            (international_id, bank_verification_num, image_id, cursor.lastrowid))

        db.commit()
    except Exception as e:
        abort(422, e.args[1])
    last_row_id = cursor.lastrowid
    cursor.execute('SELECT * FROM user WHERE user_id = %s', (last_row_id,))
    user = cursor.fetchone()

    msg = Message()
    msg.subject = "confirm your email"
    msg.recipients = [user["email"]]
    msg.body = f"here is internet id: {user['internet_id']} \n" \
               f"This id is not valid yet till you log into your dashboard and verify your identity \n" \
               f"Kindly login to your dashboard to verify your identity"

    Thread(target=send_mail, args=(current_app.app_context(), msg)).start()
    cursor.close()

    return jsonify({
        'status': 'success',
        'message': 'User registered successfully',
        'data': {
            'user': transform_user_response(user),
            'token': encode_auth_token(user['user_id'])
        }
    }), 201


@bp.route('/login/', methods=['POST'])
@limiter.limit("5 per minute")
@expects_json(login_schema)
def login():
    data = g.data
    internet_id = data.get('internet_id', None)
    password = data.get('password', None)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM user WHERE internet_id = %s', (internet_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({
                "success": False,
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        if not bcrypt.check_password_hash(user['password'], password):
            return jsonify({
                "success": False,
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        if not user['verified']:
            update_cursor = db.cursor(dictionary=True)
            update_cursor.execute('UPDATE user SET verified = %s WHERE user_id = %s', (True, user['user_id']))
            update_cursor.execute('SELECT * FROM user WHERE user_id = %s', (user["user_id"],))
            user = update_cursor.fetchone()
        db.commit()
    except Exception as e:
        current_app.logger.error(e)
        abort(400, e.args[1])
    else:
        cursor.close()
        db.close()
        return jsonify({
            'status': 'success',
            'status': 'success',
            'message': 'User logged in successfully',
            'data': {
                'user': transform_user_response(user),
                'token': encode_auth_token(f"{user['user_id']}")
            }
        })
    finally:
        cursor.close()
        db.close()


@bp.route('/logout/', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization')
    verify_token(auth_header)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        #     blackist_token
        token = auth_header.split(" ")[1]
        cursor.execute('INSERT INTO blacklisted_token (token) VALUES (%s)', (token,))
        db.commit()
    except Exception as e:
        abort(400, e.args[1])
    return jsonify({
        'status': 'success',
        'message': 'User logged out successfully'
    }), 200
