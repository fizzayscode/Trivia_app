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
        self.database_path = "trivia_test"
        "postgresql://postgres:password@localhost:5432/trivia_test".format(
         "postgres", "password", "localhost:5432", self.database_name
)

        self.new_question={
             'question':'what is your name?',
             'answer' : 'hafiz',
             'category' : 4,
             'difficulty' : 4
        }

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


#test for getting categories pass
    def test_get_categories(self):
        res=self.client().get("/categories")
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

   
#test for getting paginated questions for pass
    def test_get_paginated_questions(self):
        res=self.client().get("/questions?page=1")
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])


#test for getting paginated pages that exceed number of pages for fail
    def test_404_request_beyond_validated_page(self):
        res = self.client().get("/quesions?page=10000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not found')


#test to delete certain question for pass
    def test_delete_certain_question(self):
        #question to insert
        question = Question(question="hello", answer="hi", difficulty=3, category=5)
        question.insert()

        #making the deletion by calling the endpoint to delete the inserted question
        res = self.client().delete('/questions/{}'.format(question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)



#test to delete question that dont exist in the database for fail
    def test_422_to_delete_exceeded_question(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'could not process your request')

#test to fetch questions by category type for pass
    def test_get_question_by_category_type(self):
        res=self.client().get("/categories/1/questions")
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['particular_category'])


#test to get category that cant be found in the categories
    def test_404_get_questions_by_category_not_found(self):
        res=self.client().get("/categpories/1000/questions" ,json={'answer':1})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"Resource Not found")


#test for posting a new question to database for pass
    def test_post_questions(self):
        res=self.client().post("/questions", json={"question":"who am i","answer":"i am hafiz","category":4,"difficulty":5})
        self.assertEqual(res.status_code,200)
        data=json.loads(res.data)
        self.assertEqual(data['success'],True)


#test for posting data to databse that will fail
    def test_422_if_question_creations_fails(self):
        res = self.client().post("/questions", json={"question":"who am i","answer":"i am hafiz","category":4,"difficulty":5})
        data = json.loads(res.data)
        pass



#test to search for a particular string in the database for pass
    def test_search_questions(self):
        res=self.client().post("/questions", json= {"searchTerm":"what"})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])


#test to search for a particular string that dont exist
    def test_get_searched_question_that_dont_exist(self):
        res = self.client().post("/questions", json={'searchTerm':'lololololol'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)


#test for getting
    def test_get_quizzes(self):
        res=self.client().post("/quizzes", json={'previous_questions':[],'quiz_category':{'id':1,'type':'Science'}})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(data['question'])
        self.assertTrue(data['question']['category'],3)


#test for getting category for all questions for pass
    def test_get_quiz_questions_by_category(self):
        quiz_category = {'previous_questions':[], 'quiz_category':{'type':'ALL','id':0}}
        res = self.client().post('/quizzes',json=quiz_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)



  #test for quiz without posting the category type for fail
    def test_404_questions_to_play_quiz(self):
        new_quiz = {'previous_questions':[]}
        res = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "could not process your request")





    

    


        




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()