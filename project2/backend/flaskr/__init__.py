import os
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

    """Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs"""
    CORS(app,resources={r"/*": {"origins": "*"}})

    """Use the after_request decorator to set Access-Control-Allow"""
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response


    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods = ["GET"])
    def get_categories():
        categories = db.session.query(Category).all()
        formated_categories = [category.type for category in categories]
        return jsonify({
                'success': True,
                'categories': formated_categories
            })



    """
    Create an endpoint to handle GET requests for questions, including pagination (every 10 questions).
    This endpoint should return a list of questions, number of total questions, current category, categories.
    @TODO:
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods = ["GET"])
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = db.session.query(Question).order_by(Question.id).all()
        formated_questions = [question.format() for question in questions]
        if len(formated_questions) == 0:
            abort(404)
        categories = db.session.query(Category).all()
        formated_categories = [category.type for category in categories]
        curent_categories = [category.type for category in categories]
        return jsonify({
                'success': True,
                'questions': formated_questions[start:end],
                'totalQuestions':len(formated_questions),
                'currentCategory':curent_categories,
                'categories':formated_categories
            })

    @app.route('/questions/<int:question_id>', methods = ["GET"])
    def get_question(question_id):
        question = db.session.query(Question).filter(Question.id ==question_id).one_or_none()
        formated_question = question.format()
        return jsonify({
                'success_get_question': True,
                'questions': formated_question
            })


    """
    Create an endpoint to DELETE question using a question ID.
    @TODO:
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods = ["DELETE"])
    def delete_question(question_id):
        question = db.session.query(Question).filter(Question.id ==question_id).one_or_none()
        question.delete()
        return jsonify({
                'success_delete': True
            })


    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    @TODO:
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods = ['POST'])
    def add_question():
        body = request.get_json()
        print(body)
        question = Question(
                question = body.get("question"),
                answer = body.get("answer"),
                category = body.get("category"),
                difficulty = body.get("difficulty")
        )
        question.insert()
        return jsonify({
                'success_insert': True
            })


    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    @TODO:
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search_questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        questions = db.session.query(Question).filter(
            Question.question.ilike(f'%{search_term}%')).all()
        formated_questions = [question.format()
                                for question in questions]

        return jsonify({
            'success': True,
            'questions': formated_questions,
            'total_questions': len(formated_questions),
            'current_category': None
        })

    """
    Create a GET endpoint to get questions based on category.
    @TODO:
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods = ['GET'])
    def get_questions_by_category(category_id):
        questions = db.session.query(Question).filter(Question.category == (category_id+1)).all()
        formated_questions = [question.format() 
                                    for question in questions]
        print(formated_questions)
        return jsonify({
                'success': True,
                'questions': formated_questions,
                'total_questions': len(formated_questions),
                'current_category': category_id
            })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods =['POST'])
    def get_quiz():
        print(request.get_json())
        body = request.get_json()
        category_id = int(body.get('quiz_category').get('id')) + 1
        previous_questions = body.get('previous_questions')
        questions = db.session.query(Question).filter(Question.category == category_id).order_by(Question.id).all()
        number_of_questions = len(questions)
        selectied_question_id = random.randint(0,number_of_questions -1)
        if len(previous_questions )== number_of_questions:
             return jsonify({
                'success': True,
                'forceEnd': True
            })
        while questions[selectied_question_id].id in previous_questions:
            selectied_question_id = random.randint(0,number_of_questions -1)  
        selectied_question = questions[selectied_question_id].format()
        print({
                'success': True,
                'question': selectied_question,
                'previous_questions': previous_questions,
            })
        return jsonify({
                'success': True,
                'question': selectied_question,
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
            'message': 'Null or invalid syntax in request.'
        }), 400

    @app.errorhandler(404)
    def handle_404_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Requested page not found"
        }), 404

    @app.errorhandler(405)
    def handle_405_error(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "Method not allowed"
        }), 405

    @app.errorhandler(422)
    def handle_422_error(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "Cannot process request."
        }), 422

    @app.errorhandler(500)
    def handle_500_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "Internal server error"
        }), 500

    return app