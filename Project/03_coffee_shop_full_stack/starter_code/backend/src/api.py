import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
def drinks():
    all_drinks = Drink.query.all()
    short_drinks = [drink.short() for drink in all_drinks]
    
    return jsonify({
        "success" : True,
        "drinks" : short_drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def drinks_detail(payload):
    get_drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in get_drinks]
    return jsonify({
        "success": True, 
        "drinks": long_drinks
    }), 200
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_a_drink(payload):
    request_drinks_json = request.get_json()
    try:
        get_recipe = request_drinks_json.get("recipe", None)
        get_title = request_drinks_json.get("title", None)
        if get_recipe and get_title is None:
            abort(401)
        add_drink = Drink()
        add_drink.title = get_title
        add_drink.recipe = json.dumps(get_recipe)
        add_drink.insert()
    except:
        abort(401)
    return jsonify({
        "success": True, 
        "drinks": [add_drink.long()]
    }), 200

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:patch_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drinks(payload, patch_id):
    get_edit_id = request.get_json()
    edit_drink = Drink.query.filter(Drink.id == patch_id).one_or_none()
    new_title = get_edit_id.get("title", None)
    new_recipe = get_edit_id.get("recipe", None)
    if new_title:
        edit_drink.title = new_title
    if new_recipe:
        edit_drink.recipe = json.dumps(new_recipe)
        edit_drink.update()
    return jsonify({
        "success": True, 
        "drinks": [edit_drink.long()]
    }), 200
    

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:del_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(payload, del_id):
    del_drink = Drink.query.filter(Drink.id == del_id).one_or_none()
    if not del_drink:
        abort(404)
    del_drink.delete()
    return jsonify({
        "success" : True,
        "deleted_drink" : del_drink.id
    }), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource Not Found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405