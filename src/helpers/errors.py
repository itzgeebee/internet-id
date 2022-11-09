from flask import jsonify


def invalid_token_response():
    return jsonify({
        "success": False,
        "message": "invalid token",
        "error": 401
    }), 401


def db_error_response(error):

    if error.args[0] == 1062:
        return jsonify({
            "success": False,
            "message": "duplicate resource",
            "error": 409
        }), 409
    elif error.args[0] == 1452:
        return jsonify({
            "success": False,
            "message": "invalid foreign key",
            "error": 422
        }), 422
    elif error.args[0] == 1364:
        return jsonify({
            "success": False,
            "message": "invalid column",
            "error": 422
        }), 422
    elif error.args[0] == 1054:
        return jsonify({
            "success": False,
            "message": "invalid column",
            "error": 422
        }), 422
    return jsonify({
        "success": False,
        "message": "database error",
        "error": error
    }), 500