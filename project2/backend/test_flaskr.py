import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}"\
            .format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test
    for successful operation and for expected errors.
    """

    #  -----------------------------------------------------------------  #
    #  0. General test for invalid url
    #  -----------------------------------------------------------------  #
    def test_endpoint_not_available(self):
        """Test getting an endpoint which does not exist """
        res = self.client().get('/question')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],  "Requested page not found.")

    #  -----------------------------------------------------------------  #
    #  1. Tests for /categories Get
    #  -----------------------------------------------------------------  #
    def test_get_category(self):
        """Test GET all categories"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_error_405_get_all_categories(self):
        """Test wrong method to GET all categories """
        res = self.client().patch('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "Method not allowed.")
        self.assertEqual(data['success'], False)

    #  -----------------------------------------------------------------  #
    #  2. Tests for /questions GET
    #  -----------------------------------------------------------------  #

    def test_get_all_questions_paginated(self):
        """Test GET all questions from all categories."""
        res = self.client().get(
            '/questions?page=1', json={'category:': 'Science'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['totalQuestions'] > 0)

    def test_error_405_get_all_questions_paginated(self):
        """Test wrong method to get all questions from all categories """
        res = self.client().patch('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['message'], "Method not allowed.")
        self.assertEqual(data['success'], False)

    def test_error_404_get_all_questions_paginated(self):
        """Test get all questions with not existing page """
        res = self.client().get('/questions?page=12345')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], "Requested page not found.")
        self.assertEqual(data['success'], False)

    #  -----------------------------------------------------------------  #
    #  3. Tests for /questions DELETE
    #  -----------------------------------------------------------------  #
    def test_delete_question(self):
        """Test DELETE /question """
        # Create a new question so it can later be deleted
        # Used as header to POST /question
        json_create_question = {
            'question': 'Will this question be deleted?',
            'answer': 'Yes, it will be deleted soon!',
            'category': '1',
            'difficulty': 1
        }

        res = self.client().post('/questions', json=json_create_question)
        data = json.loads(res.data)
        question_id = data['question_id']

        # Make a DELETE request with newly created question
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success_delete'])
        self.assertEqual(data['deleted'], question_id)

    def test_404_delete_question(self):
        """Test error DELETE /question with an id which does not exist """
        res = self.client().delete('/questions/{}'.format(123456789))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(
            data['message'],
            'Question with id {} does not exist.'.format(123456789)
            )

    #  -----------------------------------------------------------------  #
    #  4. Tests for /questions POST
    #  -----------------------------------------------------------------  #
    def test_create_question(self):
        """Test POST a new question """

        # Used as header to POST /question
        json_create_question = {
            'question': 'Is this a test question?',
            'answer': 'Yes',
            'category': '1',
            'difficulty': 1
        }

        res = self.client().post(
            '/questions', json=json_create_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success_insert'])
        self.assertTrue(data['total_questions'] > 0)

    def test_error_create_question(self):
        """Test POST a new question with missing category """

        # Used as header to POST /question
        json_create_question_error = {
            'question': 'Is this a test question?',
            'answer': 'Yes it is!',
            'difficulty': 1
        }

        res = self.client().post(
            '/questions', json=json_create_question_error)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Category can not be blank')

    #  -----------------------------------------------------------------  #
    #  5. Tests for /search_questions POST
    #  -----------------------------------------------------------------  #
    def test_search_question(self):
        """Test POST to search a question with an existing search term. """

        # Used as header to POST /search_questions
        json_search_question = {
            'searchTerm': 'what',
        }

        res = self.client().post(
            '/search_questions', json=json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)

    def test_error_404_search_question(self):
        """Test POST to search a question with non existing search term. """

        # Used as header to POST /search_questions
        json_search_question = {
            'searchTerm': 'there is no question with such a string in it',
        }

        res = self.client().post(
            '/search_questions', json=json_search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(
            data['message'],
            'no questions that contains \
                "there is no question with such a string in it" found.')

    #  -----------------------------------------------------------------  #
    #  6. Tests for /categories/<string:category_id>/questions GET
    #  -----------------------------------------------------------------  #
    def test_get_questions_from_category(self):
        """Test GET all questions from selected category."""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'] > 0)
        self.assertEqual(data['current_category'], 1)

    def test_400_get_questions_from_category(self):
        """Test 400 if no questions with queried category is available."""
        res = self.client().get('/categories/14125412/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(
            data['message'], 'No questions with category 14125412 found.')

    #  -----------------------------------------------------------------  #
    #  7. Tests for /quizzes POST
    #  -----------------------------------------------------------------  #
    def test_play_quiz_with_category(self):
        """Test /quizzes succesfully with given category """
        json_play_quizz = {
            'previous_questions': [20, 21],
            'quiz_category': {
                'type': 'Science',
                'id': 1
                }
        }
        res = self.client().post('/quizzes', json=json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        # Also check if returned question is NOT in previous question
        self.assertTrue(
            data['question']['id'] not in json_play_quizz['previous_questions']
            )

    def test_play_quiz_with_category_but_all_been_played(self):
        """Test /quizzes succesfully with given category """
        json_play_quizz = {
            'previous_questions': [13, 14, 15],
            'quiz_category': {
                'type': 'Geography',
                'id': 3
                }
        }
        res = self.client().post('/quizzes', json=json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            data['message'], 'All the questions have been tested!')
        self.assertTrue(data['forceEnd'])

    def test_play_quiz_without_category(self):
        """Test /quizzes succesfully without category"""
        json_play_quizz = {
            'previous_questions': [20, 21]}
        res = self.client().post('/quizzes', json=json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['question'])
        # Also check if returned question is NOT in previous question
        self.assertTrue(
            data['question']['id'] not in json_play_quizz['previous_questions']
            )

    def test_error_400_play_quiz(self):
        """Test /quizzes error without any JSON Body"""
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Please provide a JSON body \
                    with previous question Ids and optional category.')

    def test_error_405_play_quiz(self):
        """Test /quizzes error with wrong method"""
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['error'], 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed.')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
