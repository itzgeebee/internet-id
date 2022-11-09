import os
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, current_app
from flask_bcrypt import Bcrypt
import json

from flask_cors import CORS
from jsonschema import ValidationError
from werkzeug.exceptions import HTTPException
from flask_mail import Mail

# from flask_cors import CORS

load_dotenv()

bcrypt = Bcrypt()
sender = Mail()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DATABASE_USER=os.environ.get('DATABASE_USER'),
        DATABASE_PASSWORD=os.environ.get('DATABASE_PASSWORD'),
        DATABASE_HOST=os.environ.get('DATABASE_HOST'),
        DATABASE=os.environ.get('DATABASE_NAME'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object('config')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return jsonify({'message': 'Hello, World!'})

    from . import db
    db.init_app(app)
    bcrypt.init_app(app)
    sender.init_app(app)

    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "error": error.description,
            "message": "resource not found"
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        if isinstance(error.description, ValidationError):
            original_error = error.description
            return make_response(jsonify({'success': False,
                                          'error': original_error.message}), 400)
        # handle other "Bad Request"-errors
        return jsonify({"success": False, "error": error.description,
                        "message": "bad request"}), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({"success": False, "error": error.description,
                        "message": "unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({"success": False, "error": error.description,
                        "message": "forbidden"}), 403

    @app.errorhandler(405)
    def invalid_method_error(error):
        return jsonify({"success": False, "error": error.description,
                        "message": "invalid method"}), 405

    @app.errorhandler(422)
    def not_processable_error(error):
        return jsonify({"success": False, "error": error.description,
                        "message": "not processable"}), 422

    @app.errorhandler(409)
    def duplicate_resource_error(error):
        return jsonify({"success": False, "error": error.description,
                        "message": "duplicate resource"}), 409

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"success": False, "error": 500,
                        "message": "internal server error"}), 500

    from . import auth, users, product, verify
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(product.bp)
    app.register_blueprint(verify.bp)

    cors = CORS()
    cors.init_app(app, resources={r"/api/*": {"origins": "*",
                                              "supports_credentials": True, }})

    return app
