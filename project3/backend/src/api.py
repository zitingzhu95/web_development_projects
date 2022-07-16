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

def get_all_drinks(recipe_format):
    '''Queries a formatted list of drinks with long or short recipe description
    *Input:
        <string> recipe_format "long" or "short", depending on how detailled the informations are needed
    *Output:
        <list> Formatted instances of Drinks
    If no drinks could be found, abort with 404 error.
    '''
    # Get all drinks in database
    all_drinks = Drink.query.order_by(Drink.id).all()
    # Format with different recipe detail level
    if recipe_format.lower() == 'short':
        all_drinks_formatted = [drink.short() for drink in all_drinks]
    elif recipe_format.lower() == 'long':
        all_drinks_formatted = [drink.long() for drink in all_drinks]
    else:
        return abort(500, {'message': 'bad formatted function call. recipe_format needs to be "short" or "long".'})

    if len(all_drinks_formatted) == 0:
        abort(404, {'message': 'no drinks found in database.'})
    
    # Return formatted list of drinks
    return all_drinks_formatted

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks' , methods=['GET'])
def drinks():
    """Returns all drinks"""
    return jsonify({
    'success': True,
    'drinks': get_all_drinks('short')
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail',  methods=['GET'])
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    """Returns all drinks with detailed recipe information"""
    return jsonify({
    'success': True,
    'drinks': get_all_drinks('long')
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks',  methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """Creates new drink and returns it to client"""
    
    body = request.get_json()
    print("######################")
    print(body)
    print("######################")
    print("{}".format(body['recipe']))
    new_drink = Drink(
        title = "{}".format(body['title']),
        recipe = """{}""".format(json.dumps(body['recipe'])))
 
    new_drink.insert()
    # new_drink.recipe = body['recipe']
    return jsonify({
    'success': True,
    'drinks': Drink.long(new_drink)
    })

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
@app.route('/drinks/<int:drink_id>',  methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    """Updates existing drink and returns it to client"""
    
    # Get body from request
    body = request.get_json()

    if not body:
      abort(400, {'message': 'request does not contain a valid JSON body.'})
    
    # Find drink which should be updated by id
    drink_to_update = Drink.query.filter(Drink.id == drink_id).one_or_none()

    # Check if and which fields should be updated
    updated_title = body.get('title', None)
    updated_recipe = body.get('recipe', None)
    
    # Depending on which fields are available, make apropiate updates
    if updated_title:
        drink_to_update.title = body['title']
    
    if updated_recipe:
        drink_to_update.recipe = """{}""".format(body['recipe'])
    
    drink_to_update.update()

    return jsonify({
    'success': True,
    'drinks': [Drink.long(drink_to_update)]
    })



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
@app.route('/drinks/<int:drink_id>',  methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    """Deletes 1 drink with given id"""
    if not drink_id:
        abort(422, {'message': 'Please provide valid drink id'})

    # Get drink with id
    drink_to_delete = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if not drink_to_delete:
        abort(404, {'message': 'Drink with id {} not found in database.'.format(drink_id)})
     
    drink_to_delete.delete()
    
    return jsonify({
    'success': True,
    'delete': drink_id
    })


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
