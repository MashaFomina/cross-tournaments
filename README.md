
## Description
This project is backend for a weekend competitions when several teams run around the city and do all kinds of technological tasks. The team that gave the most amount of correct answers wins. If there are two teams with the same count of tasks than the team wins which has the smallest fine time (it is calculated automatically based on used hints, count of wrong answers and time spent on doing task).

An envelope with a username and password is given to the team at the beginning of the tournament. The team logins to the application and sees the tasks.

The each task has:
- title
- geolocation where to run
- task description (text up to 300 characters without markup)
- input for entering the answer (each answer is a line, each task has exactly one correct answer)
- three hints (each hint is a text without markup up to 300 characters)
- status for concrete authenticated user (done - 2, progress - 1, planned - 0)

Teams run around the city, solve tasks. Tasks can be solved in any
sequence. The entire tournament lasts 5 hours. The application stops accepting responses from teams after 5 hours 
after the tournament's beginning. The tournament has 6-8 tasks.

## Project Tools
- Django

## Requirements
- SQLite
- Python 3.7 +
- pip 19.2.3 +

## Getting Started
Once you have cloned this repo to your local environment:

```bash
# install Django, dependencies and check
pip install -r requirements.txt

# if you want change database configure db in cross-tournaments/settings.py (by degault used SQLite)

# create migration for database
>> python manage.py makemigrations tournaments

# apply migration
>> python manage.py sqlmigrate tournaments 0001
>> python manage.py migrate

# create superuser
python manage.py createsuperuser

# run tests, test runner creats a test database
python manage.py test

# run server
python manage.py runserver
```

## Api endpoints and login:
- http://127.0.0.1:8000/admin - administration panel to add tournaments, tasks and hints
- http://127.0.0.1:8000/api-auth/login/ - login page (temporary to have access to swagger)

POST methods can be executed only by users in group `players`.

**All next endpoints are available only for authenticated users:**
- http://127.0.0.1:8000/api_doc/ - swagger documentation
- http://127.0.0.1:8000/tournaments/ - return list of tournaments
- http://127.0.0.1:8000/tournaments/users/{tournament_pk}/ - returns list of users (players) with progress.
- http://127.0.0.1:8000/tournaments/tasks/{tournament_pk} - returns list of tasks filtered by tournament for the current authenticated user.
- http://127.0.0.1:8000/tournaments/hints/{id}/ - open hint on task (method POST)
- http://127.0.0.1:8000/tournaments/tasks/{id}/ - submit response on task (method POST, use JWT-token or Basic Auth). Example of body:
```
{"response": "itgiviuiuvy"}
```

## Access to protected views (http `Authorization` header):
- Basic Auth
```
Authorization: Basic base64('admin:admin')
```
- JWT

# use JWT
To verify that Simple JWT is working, you can use curl to issue a couple of test requests:
```
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "masha", "password": "masha"}' \
  http://localhost:8000/api/token/
```

You can use the returned access token to prove authentication for a protected view:
```
curl \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTY4MTA5MjU4LCJqdGkiOiIxOWFhMmI0NGVlYzk0M2M3OWIxMjdiMzNiZTFlYmNjZiIsInVzZXJfaWQiOjJ9.IxpFZTIQXUszG0voCyjkF10nKuIKsxFRKV-nWg3d__k" \
  http://localhost:8000/tournaments/tasks/1/
```

When this short-lived access token expires, you can use the longer-lived refresh token to obtain another access token:
```
curl \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' \
  http://localhost:8000/api/token/refresh/

...
{"access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNTY3LCJqdGkiOiJjNzE4ZTVkNjgzZWQ0NTQyYTU0NWJkM2VmMGI0ZGQ0ZSJ9.ekxRxgb9OKmHkfy-zs1Ro_xs1eMLXiR17dIDBVxeT-w"}
```