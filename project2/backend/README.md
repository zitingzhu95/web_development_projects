# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createbd trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.


## API Documentation

### Getting Started

Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, http://127.0.0.1:5000/, which is set as a proxy in the frontend configuration.
Authentication: This version of the application does not require authentication or API keys.

### Error Handling
Errors are returned as JSON objects in the following format:
```json
{
    "success": False, 
    "error": 400,
    "message": "Null or invalid syntax in request."
}
```

The API will return five error types when requests fail:
- 400: Null or invalid syntax in request
- 404: Requested page not found
- 405: Method not allowed
- 422: Cannot process request
- 500: Internal server error

### Endpoints
1. GET /categories
- General:
  - Returns a list of Category objects, success value
- Sample: curl http://127.0.0.1:5000/categories
```
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
```
2. GET /questions
- General:
  - Returns a list of Question objects, total question numbers, current category, a list of categories, success value
  - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
- Sample: curl http://127.0.0.1:5000/questions?page=1
```
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
```
- Error
  - If you try fetch a page which does not have any questions, you will encounter an error which looks like this: 
curl -X GET http://127.0.0.1:5000/questions?page=12452512
  - will return
```
{
  "error": 404,
  "message": "resource not found",
  "success": false
}
```


GET /questions
- General:
  - Returns a list of Question objects, total question numbers, current category, a list of categories, success value
  - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1.
- Sample: curl http://127.0.0.1:5000/questions
```


