import os
import random
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """Set up CORS. Allow '*' for origins."""
    CORS(app, resources={r"/*": {"origins": "*"}})

    """Use the after_request decorator to set Access-Control-Allow"""
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    #  ----------------------------------------------------------------  #
    #  0. Define costomized function
    #  ----------------------------------------------------------------  #
    def paginate_questions(request, questions):
        '''
        Paginates and formats questions
        Parameters:
        - <HTTP object> request, that may contain a "page" value
        - <database selection> selection of questions, queried from database
        Returns:
        - <list> list of dictionaries of questions,
            max. 10 questions(QUESTIONS_PER_PAGE)
        '''
        # Get page from request. If not given, default to 1
        page = request.args.get('page', 1, type=int)
        # Calculate start and end slicing
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        # Format selection into list of dicts and slice
        questions = [question.format() for question in questions]
        current_questions = questions[start:end]

        return current_questions

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

    #  ----------------------------------------------------------------  #
    #  1. Create an endpoint to handle GET requests
    #     for all available categories.
    #  ----------------------------------------------------------------  #
    """
    This endpoint should return a list of categories
    """
    @app.route('/categories', methods=["GET"])
    def get_categories():
        # Get all categories
        categories = db.session.query(Category).all()
        formated_categories = [category.type for category in categories]
        return jsonify({
                'success': True,
                'categories': formated_categories
            })
    #  ----------------------------------------------------------------  #
    #  2. Create an endpoint to handle GET requests for questions,
    #     including pagination (every 10 questions).
    #  ----------------------------------------------------------------  #
    """
    This endpoint should return
    a list of questions, number of total questions,
    current category, categories.
    """
    @app.route('/questions', methods=["GET"])
    def get_questions():
        
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = db.session.query(Question).order_by(Question.id).all()
        formated_questions = [question.format() for question in questions]
        if len(formated_questions) == 0 or start > len(formated_questions):
            abort(404, {'message': 'No questions in selected page.'})
        categories = db.session.query(Category).all()
        formated_categories = [category.type for category in categories]
        curent_categories = [category.type for category in categories]
        return jsonify({
                'success': True,
                'questions': formated_questions[start:end],
                'totalQuestions': len(formated_questions),
                'currentCategory': curent_categories,
                'categories': formated_categories
            })

    #  ----------------------------------------------------------------  #
    #  3. Create an endpoint to DELETE question using a question ID.
    #  ----------------------------------------------------------------  #
    """
    This endpoint should remove a questions
    when you click the trash icon next to a question.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):

        question = db.session.query(Question)\
            .filter(Question.id == question_id)\
            .one_or_none()
        if not question:
            abort(
                400,
                {'message':
                    'Question with id {} does not exist.'
                    .format(question_id)})
        try:
            question.delete()
            return jsonify({
                    'deleted': question_id,
                    'success_delete': True
                    })
        except BaseException:
            abort(422)

    """
    4. Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    TEST:When you submit a question on the "Add" tab,
    the form will clear and the question will appear
    at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():

        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        if not new_question:
            abort(400, {'message': 'Question can not be blank'})

        if not new_answer:
            abort(400, {'message': 'Answer can not be blank'})

        if not new_category:
            abort(400, {'message': 'Category can not be blank'})

        if not new_difficulty:
            abort(400, {'message': 'Difficulty can not be blank'})

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            questions = Question.query.order_by(Question.id).all()
            questions_paginated = paginate_questions(request, questions)

            # Return succesfull response
            return jsonify({
                "question_id": question.id,
                'success_insert': True,
                'questions': questions_paginated,
                'total_questions': len(questions)
            })

        except BaseException:
            abort(422)
    """
    5. Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    TEST:Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search_questions', methods=['POST'])
    def search_question():

        body = request.get_json()
        search_term = body.get('searchTerm', None)
        questions = db.session.query(Question).filter(
            Question.question.ilike(f'%{search_term}%')).all()
        if not questions:
            abort(404, {'message': 'no questions that contains \
                "there is no question with such a string in it" found.'})
        formated_questions = [question.format() for question in questions]

        return jsonify({
            'success': True,
            'questions': formated_questions,
            'total_questions': len(formated_questions),
            'current_category': None
        })

    """
    6. Create a GET endpoint to get questions based on category.
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        questions = db.session.query(Question)\
            .filter(Question.category == (category_id))\
            .all()
        if not questions:
            abort(
                400,
                {'message':
                    'No questions with category {} found.'
                    .format(category_id)})
        formated_questions = [question.format() for question in questions]
        return jsonify({
                'success': True,
                'questions': formated_questions,
                'total_questions': len(formated_questions),
                'current_category': category_id
            })

    """
    7. Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():

        body = request.get_json()
        if not body:
            # If no JSON Body was given, raise error.
            abort(
                400, {'message': 'Please provide a JSON body \
                    with previous question Ids and optional category.'})
        # Get paramters from JSON Body.
        previous_questions = body.get('previous_questions', None)
        category = body.get('quiz_category', None)
        previous_questions = body.get('previous_questions')

        if not previous_questions:
            if category:
                # if no list with previous questions is given, but a category,
                # just gut any question from this category.
                questions_to_select = db.session.query(Question)\
                    .filter(Question.category == str(category['id']))\
                    .order_by(Question.id)\
                    .all()
                questions = questions_to_select

            else:
                # if no list with previous questions is given
                # and also no category,
                # just gut any question.
                questions_to_select = db.session.query(Question)\
                    .order_by(Question.id)\
                    .all()
                questions = questions_to_select

        else:
            if category:
                # if a list with previous questions is given
                # and also a category,
                # query for questions
                # which are not contained in previous question
                # and are in given category
                questions_to_select = db.session.query(Question)\
                    .filter(Question.category == str(category['id']))\
                    .filter(Question.id.notin_(previous_questions))\
                    .all()
                questions = db.session.query(Question)\
                    .filter(Question.category == str(category['id']))\
                    .order_by(Question.id)\
                    .all()
            else:
                # if a list with previous questions is given but no category,
                # query for questions
                # which are not contained in previous question.
                questions_to_select = db.session.query(Question)\
                    .filter(Question.id.notin_(previous_questions))\
                    .all()
                questions = db.session.query(Question)\
                    .order_by(Question.id).all()
        questions_formatted = [
            question.format() for question in questions_to_select]
        number_of_questions = len(questions)
        number_of_questions_to_select = len(questions_to_select)
        if len(previous_questions) == number_of_questions:
            return jsonify({
                'message': 'All the questions have been tested!',
                'forceEnd': True
            })

        random_question = questions_formatted[
            random.randint(0, number_of_questions_to_select-1)]

        return jsonify({
                'success': True,
                'question': random_question,
            })
    """
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def handle_400_error(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': getErrorMessage(
                error,
                'Null or invalid syntax in request.')
        }), 400

    @app.errorhandler(404)
    def handle_404_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': getErrorMessage(error, "Requested page not found.")
        }), 404

    @app.errorhandler(405)
    def handle_405_error(error):

        return jsonify({
            'success': False,
            'error': 405,
            'message': getErrorMessage(error, "Method not allowed.")
        }), 405

    @app.errorhandler(422)
    def handle_422_error(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': getErrorMessage(error, "Cannot process request.")
        }), 422

    @app.errorhandler(500)
    def handle_500_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': getErrorMessage(error, "Internal server error.")
        }), 500

    return app
