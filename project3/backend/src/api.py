import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from database.models import db_drop_and_create_all, setup_db, Drink
from auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
#db_drop_and_create_all()

#  ----------------------------------------------------------------  #
#  0. Define costomized function
#  ----------------------------------------------------------------  #
def getErrorMessage(error, default_text):
    '''
    Returns default error text or custom error message
    Parameters:
    - <error> system generated error message
    which contains a description message
    - <string> default text to be used as error message
    if Error has no specific message
    Returns:
    - <string> specific error message or default text
    (if no specific message is given)
    '''
    try:
        # Return message contained in error
        return error.description["message"]
    except TypeError:
        # otherwise, return given default text
        return default_text

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


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


#----------------------------------------------------------------------------#
# API error handler & formatter.
#----------------------------------------------------------------------------#
 
# reate error handlers for all expected errors 

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": getErrorMessage(error, "bad request")
        }), 400

@app.errorhandler(404)
def ressource_not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": getErrorMessage(error, "resource not found")
        }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "method not allowed"
        }), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": getErrorMessage(error, "unprocessable")
        }), 422

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "internal server error"
        }), 500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
