Backend - Trivia API
Setting up the Backend
Install Dependencies
Python 3.7 - Follow instructions to install the latest version of python for your platform in the python docs

Virtual Environment - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the python docs

PIP Dependencies - Once your virtual environment is setup and running, install the required dependencies by navigating to the /backend directory and running:

pip install -r requirements.txt
Key Pip Dependencies
Flask is a lightweight backend microservices framework. Flask is required to handle requests and responses.

SQLAlchemy is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in app.pyand can reference models.py.

Flask-CORS is the extension we'll use to handle cross-origin requests from our frontend server.

Set up the Database
With Postgres running, create a trivia database:

createbd trivia
Populate the database using the trivia.psql file provided. From the backend folder in terminal run:

psql trivia < trivia.psql
Run the Server
From within the ./src directory first ensure you are working using your created virtual environment.

To run the server, execute:

flask run --reload
The --reload flag will detect file changes and restart the server automatically.

API Documentation
Getting Started
Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, http://127.0.0.1:5000/, which is set as a proxy in the frontend configuration. Authentication: This version of the application does not require authentication or API keys.

Error Handling
Errors are returned as JSON objects in the following format:

{
    "success": False, 
    "error": 400,
    "message": "Null or invalid syntax in request."
}
The API will return five error types when requests fail:

400: Null or invalid syntax in request
404: Requested page not found
405: Method not allowed
422: Cannot process request
500: Internal server error
Endpoints
GET /categories
General:
Returns a list of Category objects, success value
Sample: curl http://127.0.0.1:5000/categories
{
  "categories": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "success": true
}
GET /questions
General:
Returns a list of Question objects, total question numbers, current category, a list of categories, success value
Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
Sample:
curl http://127.0.0.1:5000/questions?page=1
will return

{
  "categories": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "currentCategory": [
    "Science", 
    "Art", 
    "Geography", 
    "History", 
    "Entertainment", 
    "Sports"
  ], 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 5, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    }, 
    
 [...]
 
  ], 
  "success": true, 
  "totalQuestions": 23
}
Error
If you try fetch a page which does not have any questions, you will encounter an error which looks like this:
curl -X GET http://127.0.0.1:5000/questions?page=12452512
will return

{
  "error": 404,
  "message": "resource not found",
  "success": false
}
Delete /questions/<question_id>
General:
Deletes specific question based on given id
Sample:
curl -X DELETE http://127.0.0.1:5000/questions/10
will return

{
  "deleted": 10,
  "success": true
}
Post /questions
General:
Deletes specific question based on given id
Sample:
curl -X POST http://127.0.0.1:5000/questions -H "Content-Type: application/json" -d '{"question": "add_question", "answer": "add", "difficulty": 1, "category": 1}'  
will return

{
  "success_insert": true
}
Post /search_questions
General:
Return any questions for whom the search term is a substring of the question.
Sample:
curl -X POST http://127.0.0.1:5000/search_questions -H "Content-Type: application/json" -d '{"searchTerm": "who"}'  
will return

{
  "current_category": null, 
  "questions": [
    {
      "answer": "Maya Angelou", 
      "category": 4, 
      "difficulty": 2, 
      "id": 5, 
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    }, 
    {
      "answer": "George Washington Carver", 
      "category": 4, 
      "difficulty": 2, 
      "id": 12, 
      "question": "Who invented Peanut Butter?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }
  ], 
  "success": true, 
  "total_questions": 3
}
GET /categories/int:category_id/questions
General:
Return a list of questions based on category.
Sample:
curl -X GET http://127.0.0.1:5000/categories/2/questions 
will return

{
  "current_category": 2, 
  "questions": [
    {
      "answer": "Escher", 
      "category": 2, 
      "difficulty": 1, 
      "id": 16, 
      "question": "Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
    }, 
    {
      "answer": "Mona Lisa", 
      "category": 2, 
      "difficulty": 3, 
      "id": 17, 
      "question": "La Giaconda is better known as what?"
    }, 
    {
      "answer": "One", 
      "category": 2, 
      "difficulty": 4, 
      "id": 18, 
      "question": "How many paintings did Van Gogh sell in his lifetime?"
    }, 
    {
      "answer": "Jackson Pollock", 
      "category": 2, 
      "difficulty": 2, 
      "id": 19, 
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    }
  ], 
  "success": true, 
  "total_questions": 4
}
POST /quizzes
General:
Get questions to play the quiz
take category and previous question parameters and return a random questions within the given category,
Sample:
curl -X POST http://127.0.0.1:5000/quizzes -H "Content-Type: application/json" -d '{"previous_questions": [], "quiz_category" : {"type" : "Science", "id" : "1"}}'
will return

{
  "question": {
    "answer": "add", 
    "category": 1, 
    "difficulty": 1, 
    "id": 39, 
    "question": "add_question"
  }, 
  "success": true
}
