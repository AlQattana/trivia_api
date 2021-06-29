import os
from re import search
from flask import Flask, request, abort, jsonify
from flask.globals import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random

from sqlalchemy.sql.expression import true

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @[Done] TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @[Done] TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response
  '''
  @[Done] TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  @cross_origin()
  def retrieve_categories():
    categories = Category.query.all()
    
    formatted_categories = [category.format() for category in categories]

    if len(categories) == 0:
      abort(404)

    return jsonify({
        'success': True,
        'categories': formatted_categories,
        })
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  @cross_origin()
  def retrieve_questions():
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)

    categories = Category.query.all()

    if len(current_questions) == 0:
      abort(404)

    formatted_categories = [category.format() for category in categories]    

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'current_category': None,
        'categories': formatted_categories
        })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  @cross_origin()
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id,
      })

    except: 
      abort(422)
    

  '''
  @[Done] TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  @cross_origin()
  def create_question():
      body = request.get_json()
      
      answer = body.get('answer', None)
      category = body.get('category', None)
      difficulty = body.get('difficulty', None)
      question = body.get('question', None)
      
      if None in (answer, category, difficulty, question):
        abort(422)

      try:
        question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
        question.insert()

        return jsonify({
        'success': True,
        'created': question.id,
        })
      
      except:
        abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  @cross_origin()
  def search_questions():
    body = request.get_json()

    search_term = body.get('search_term', None)
    
    if search_term:
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term)))
      current_questions = paginate_questions(request, selection)

      return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(current_questions),
      'current_category': None
      })
    
    else:
      abort(422)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  @cross_origin()
  def retrieve_questions_by_category(category_id):
    try:  
      selection = Question.query.filter(Question.category == str(category_id)).all()
      questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'questions': questions,
        'total_questions': len(questions),
        'current_category': category_id        
      })
    except:
      abort(404)
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
      try:
          body = request.get_json()

          quiz_category = body.get('quiz_category', None)
          previous_questions = body.get('previous_questions', None)

          if (quiz_category is None or previous_questions is None):
              abort(422)

          if quiz_category['type'] == 'click':
              available_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
          else:
              available_questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()

          new_question = available_questions[random.randrange(0, len(available_questions))].format() if len(available_questions) > 0 else None

          return jsonify({
              'success': True,
              'question': new_question
          })
      except:
          abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
      }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "internal server error"
      }), 500

  return app

    