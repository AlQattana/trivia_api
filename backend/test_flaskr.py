import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format('postgres:1342','localhost:5432', self.database_name)
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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    ######################################################

    def test_get_paginated_questionss(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    ######################################################

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))        

    ######################################################

    def test_delete_question(self):
        # First creating a dummy question
        question = Question(question='dummy question', answer='dummy answer', difficulty=1, category=1)
        question.insert()

        # Test begin
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'])
        self.assertEqual(data['deleted'], question.id)    
    
    ######################################################

    def test_delete_invalid_question(self):
        res = self.client().delete(f'/questions/145489498')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
  
    ######################################################

    def test_create_question(self):
        # First creating a dummy question
        test_question = {
            'question': 'Who am I ?',
            'answer': 'Maha',
            'category': '1',
            'difficulty': '2'
        }

        res = self.client().post(f'/questions', json=test_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        question = Question.query.filter(Question.answer == "Maha").one_or_none() 

        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(data['created'], question.id)

        question.delete()   

    ######################################################

    def test_422_create_question(self):
        # First creating a dummy question
        test_question = {
            'question': 'Who am I ?',
            'answer': 'Maha',
            'difficulty': '2'
        }

        res = self.client().post(f'/questions', json=test_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
 

    ######################################################

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    ######################################################

    def test_get_question_search_with_results(self):
        res = self.client().post('/questions/search', json={'search_term': 'soccer'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 2)

    ######################################################

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions/search', json={'search_term': 'SomeRanDomSearcHTerM'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)    

    ######################################################

    def retrieve_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    ######################################################
    
    def test_play_quiz(self):
        new_quiz_round = {'previous_questions': [],
                          'quiz_category': {'type': 'Entertainment', 'id': 5}}

        res = self.client().post('/quizzes', json=new_quiz_round)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()