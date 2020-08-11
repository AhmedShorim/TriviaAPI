import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"*": {"origins": '*'}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def categories():
    # get all categories
    categories = Category.query.all()

    try:
      # formatting the list of categories into a dictionary for the frontend
      formatted_categories = dict((category.id, category.type) for category in categories)

      return jsonify({
        "categories": formatted_categories,
        "success": True
      })
    except:
      abort(500)
  
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
  def questions():
    try:
      # get page number from request arguments, if null then set it to 1
      page = request.args.get('page', 1, type=int)

      # set the start and the end indexes for the pages
      start = (page-1) * 10
      end = start + 10

      # get all categories and format them
      categories = Category.query.all()
      formatted_categories = dict((category.id, category.type) for category in categories)

      # set the current category to the first category
      current_category = Category.query.first()

      # get all questions belonging to the first category and format them into an array
      questions = Question.query.filter_by(category=str(current_category.id)).all()
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        "questions": formatted_questions[start:end],
        "total_questions": len(formatted_questions),
        "categories": formatted_categories,
        "current_category": current_category.id,
        "success": True
      })
    except:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    # try & except clause to catch if the question_id is not an integer
    try:
      # check if the question_id is a valid ID
      if int(question_id) < 1:
        abort(400)
    except:
      abort(400)

    # get the required question object
    question = Question.query.get(question_id)

    # check if the question object is null
    if question is None:
      abort(400)

    try:
      # delete the question
      question.delete()

      return jsonify({
        "success": True
      })
    except:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def add_question():
    # get the question data
    data = request.get_json()

    try:
      # create a question 
      question = Question(data['question'], data['answer'], data['category'], data['difficulty'])
    except:
      abort(422)

    try:
      # insert the question to the database
      question.insert()

      return jsonify({
        "success": True
      })
    except:
      abort(500)

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
  def search_questions():
    # get the search term from the request body
    searchterm = request.get_json()['searchTerm']

    # check if search term is empty
    if searchterm == "":
      abort(400)

    try:
      # get the questions matching the search term and format them into a list
      questions = Question.query.filter(func.lower(Question.question).contains(func.lower(searchterm))).all()
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        "questions": formatted_questions,
        "total_questions": len(formatted_questions),
        "current_category": questions[0].category,
        "success": True
      })
    except:
      abort(500)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<category_id>/questions')
  def questions_by_category(category_id):
    # try & except clause to catch if the category_id is not an integer
    try:
      # check if the category_id is a valid ID
      if int(category_id) < 1:
        abort(400)
    except:
      abort(400)
    
    try:
      # get all questions matching the category and formatting them into a list
      questions = Question.query.filter_by(category=category_id).all()
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        "questions": formatted_questions,
        "total_questions": len(formatted_questions),
        "current_category": category_id,
        "success": True
      })
    except:
      abort(500)

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
  def quizzes():
    # get data from request body
    data = request.get_json()
    previous_questions = data['previous_questions']
    quiz_category = data['quiz_category']

    # check if category is empty or null
    if quiz_category is None or quiz_category == "":
      abort(400)

    # check if quiz category id is an integer
    try:
      int(quiz_category['id'])
    except:
      abort(400)

    # get questions related to the category
    questions = Question.query.filter_by(category=quiz_category['id']).all()

    # try & except clause to catch if a question id was sent in the previous questions list that does not exist
    try:
      # remove all the previous questions from the questions list
      for previous_question_id in previous_questions:
        questions.remove(Question.query.get(previous_question_id))
    except:
      abort(422)

    try:
      # check if no more questions exists
      if len(questions) == 0:
        return jsonify({
          "success": True
        })
    
      # generate a random index from the questions list
      randomIndex = random.randint(0, len(questions)-1)

      # format the questions into a list and extract the next question
      formatted_questions = [question.format() for question in questions]
      next_question = formatted_questions[randomIndex]

      return jsonify({
        "question": next_question,
        "success": True
      })
    except:
      abort(500)

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
      "message": "Bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Resource not found"
    }), 404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Data unprocessable"
    }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Internal server error"
    }), 500

  return app