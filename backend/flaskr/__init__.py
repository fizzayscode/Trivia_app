
from multiprocessing.connection import answer_challenge
import os
from queue import Empty
from unicodedata import category
from flask import Flask, request, abort, jsonify,flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    def paginate_questions(request, selection):
     page = request.args.get("page", 1, type=int)
     start = (page - 1) * QUESTIONS_PER_PAGE
     end = start + QUESTIONS_PER_PAGE

     questions = [question.format() for question in selection]
     current_questions = questions[start:end]

     return current_questions

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories" , methods=["GET"])
    def get_categories():
        # query to get all the categories from the database table 'category' and order it by the id that is in ascending order
        categories = Category.query.order_by(Category.id).all()

        #if the length of the category is 0 that means it is empty and there's no data or the query refused to fetch or soemthung went wrong then
        # i abort
        if len(categories)==0:
            abort(404)

        #an empty dict that will hold all my categories 
        categories_dict={}


        #creating a for loop to iterate over each element in all my categories and show how it should be displayed 
        # as a dict, that is the id is key and the type is the value pair example {1:science}
        categories_dict={category.id:category.type for category in categories}
        return jsonify({
            'success':True,
            # then i passed my category dictionary list to catergories json
            'categories':categories_dict,
            'current_category':None,
            'total_categories':len(categories)

        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        # query to fetch all my questions from the question table and order it and an ascending way by the id
        questions=Question.query.order_by(Question.id).all()

        #if the lenght of my quetions is 0 that means it is empty theres no data to fetch or something went wrong
        if len(questions)==0:
            abort(404)
        
        # then else do this
        # this is a method call to paginate questions and i passed all my questions to it for it to paginate 
        # all my questions and display 10 per page
        paginated_questions=paginate_questions(request,questions)

        all_categories=Category.query.all()


        # an empty list that will hold all my category types
        categories=[]

        #for loop to iterate over all my categories and add only the category type to my categories list
        categories=[category.type for category in all_categories]

        return jsonify({
            "success":True,
            "questions":paginated_questions,
            "total_questions":len(questions), 
            "categories":categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>" , methods=["DELETE"])
    def delete_question(question_id):

        try:
            # query to fetch a question based on some predefined question_id i put in the method parameter
            particular_question=Question.query.get(question_id)
            
            #then i check if the question was actually gotten or its available
            # if it is not i abort with the 404 not found error
            if(particular_question is None): 
                abort(404)
            
            # if it passes and does not abort that means that particular question was gotten from the database 
            # then i call the delete method which deletes the particular question from the database totally
            particular_question.delete()

            # query to get all my questions after deleting a particular question
            questions = Question.query.order_by(Question.id).all()

            # then called the paginate method again to get 10 questions perpage 
            paginated_questions = paginate_questions(request, questions)
            
               
            return jsonify({
                "success":True,
                "deleted": question_id,
                "questions":paginated_questions,
                "total_questions_now":len(questions)
            })

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def new_question():
        body=request.get_json()
        
        # trying to get the user question, answer category and difficulty from the forms request if theres no question it falls back to none
        # thats why its the second argument
        question_body=body.get("question",None)
        answer_body=body.get("answer",None)
        category_body=body.get("category",None)
        difficulty_body=body.get("difficulty",None)

        # theres is also another inpit which is the searchTerm also in '/questions' path to get questions based on the search
        search_word=body.get("searchTerm",None)


        try:
            # if my search_word that is the searchTerm is not None that is it is not empty 
            # that means im not posting a question but trying to retrieve a question, search for a question
            if search_word is not None:


            # query to search for or filter items in the questions database table that there is part of the 'search_word' in it 
            # does not matter the place the search_word could be in the middle, beggining or end, as long as the 'search_word' part of the question
                 search_result=Question.query.filter(Question.question.ilike('%'+search_word+'%')).all()
            
            
            # empty list to put my search questions
                 searched_questions=[]


            # iterating over all the items i got from the filtered questions and formatting them in a certian way , making them a list 
            #then getting the legnth of the whole list
                 searched_questions=[question.format() for question in search_result]

                 return jsonify({
                     "success":True,
                     "questions":searched_questions,
                     "total_questions":len(searched_questions),
                })
        

            # if the searchTerm is empty then im trying to create a new question to post in my database, it runs the below code
            question=Question(question=question_body,answer=answer_body,category=category_body,difficulty=difficulty_body)

            # querry to insert and commit to the database
            question.insert()

            # query to fetch all questions
            updated_questions=Question.query.order_by(Question.id).all()

            # paginate them 10 per page
            paginated_questions=paginate_questions(request, updated_questions)
            return jsonify({
                    "success": True,
                    "created_id": question.id,
                    "questions": paginated_questions,
                    "total_questions": len(updated_questions)
                }
            )
        
        except:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.


    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def questions_by_category(category_id):

        # i have to increment the category id to 1, and 1 to 2 because its starts
        #  from 0 and theres no category with the id of 0 after checking each of the id through the console
         category_id=category_id+1

        # query to filter or get category by a certain category_id that was passed from the method param 
         particular_category=Category.query.get(category_id)
        

        # if thaat particular_category does not exist then we have to abort and tell the user this caetgory was not found
         if particular_category is None: 
                 abort(404)
        

        # or else it actually exists and we are trying to fetch all the questions based off of that particular category_id  
         questions_in_category=Question.query.filter(Question.category==category_id).all()
        

        #and checking if there are questions in particular category to display
         if(questions_in_category is None):
            flash("there are currently no questions in this particular category")

        #or else retrieve and paginate the questions in that category 10 per page
         paginated_category_questions= paginate_questions(request, questions_in_category)

         return jsonify({
                "success":True,
                "questions":paginated_category_questions,
                "total_questions":len(questions_in_category),
                "particular_category":particular_category.type
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

    @app.route("/quizzes",methods=["POST"])
    def get_quiz_questions():
        body=request.get_json()

        #  if both previous questions and quiz_category are not in body then abort because we need both for the quiz to start
        if ("previous_questions" and "quiz_category" not in body ):
            abort(422)
        
        # getting both the previous questions and quiz_category from the body and storing them in my own field
        previous_questions=body.get("previous_questions")
        category=body.get("quiz_category")

        # got the particular category id from the catergory and stored it in the category_id
        category_id=category['id']

        #setting the list to an empty list before populating
        random_question=[]

        # checking to see if the category_id is 0 if it is 0 then i am trying to get the questions in the ALL category
        # because after console.log i found out the ALL id is actually 0 
        if (category_id ==0):



            # then i am running the query to to filter all my questions regardless of the category and checking to see if it is in the
            # previous questions id list before bringing it up for the user
            # the 'not_in' checks if it is not in the presvious questions id list and displays if its not because i am filtering by it 
            questions_in_category=Question.query.filter(Question.id.not_in(previous_questions)).all()


            # or else the category is not 0 that means the id is not  the "ALL" category i actaully have a
            #  predefined category i am trying to get the questions from
        elif(category_id != 0 ):


          
            # tthis query fetches and filters the questions based on the particular category is because questions have a category field also
            # then after fetching based pn caetgory_id then i filter the output i got again to the question id that is not in the previous questions id list
            # because i dont want duplicate questions
            #  then i get all the questions 
            questions_in_category=Question.query.filter(Question.category==category_id).filter(Question.id.not_in(previous_questions)).all()
            

            # checking to see if i actaully have questions in that catgeory to display or work on
        if (len(questions_in_category)>0):

            # then i run the random formula to get every question to display randomly 
            # the random collects 2 parameters 1 is the starting point and the end is the length of the whole list -1  
            # then every index it gets after radnomizing it prints the question in that index to the user
                 random_question=questions_in_category[random.randint(0,len(questions_in_category)-1)].format()
                
        return({
            "success":True,
            "question":random_question

        })




    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        "success": False, 
        "error": 404,
        "message": "Resource Not found"
        }), 404

    @app.errorhandler(422)
    def not_processed(error):
     return jsonify({
        "success": False, 
        "error": 422,
        "message": "could not process your request"
        }), 422


    @app.errorhandler(500)
    def server_error(error):
     return jsonify({
        "success": False, 
        "error": 500,
        "message": "Server Eroor"
        }), 500


    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400

   

    return app

