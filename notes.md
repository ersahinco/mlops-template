Docker build-up commands in sequence!
poetry lock --no-update
poetry install
rm -rf ./pgdata       
rm -rf ./postgresql-test
docker-compose down -v
docker volume prune -f
docker-compose build
docker-compose up
docker exec -it 58e0cad2284b089c2762ed9219baa49d22e638e13f9331934edff5e0511610fe psql postgresql://postgres:password123@localhost:5432/fastapiDB

alembic revision --autogenerate -m "create_arxiv_model"
alembic upgrade head


Error Note 1:
The error you're encountering, MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place?, indicates an issue with asynchronous handling in SQLAlchemy when trying to access the results attribute of the QueryRecord model.

Issue Explanation:
This error usually occurs when the ORM relationship is accessed outside of an asynchronous context that is capable of performing I/O operations. This can happen if SQLAlchemy tries to lazy-load a relationship property without being inside a proper async context.

Solution:
To avoid this issue, ensure that all relationships are eagerly loaded when fetching data that includes relationships. This way, all the necessary data is loaded within the correct async context.

Error Note 2:
The error The unique() method must be invoked on this Result, as it contains results that include joined eager loads against collections indicates that when you use joinedload to eagerly load collections, SQLAlchemy requires the unique() method to be called on the result to ensure unique rows in the collection.

Changes to be made:
Invoke the unique() method on the result when querying with joined eager loads.

Error Note 3:
Commenting out the mocker.patch('requests.get', return_value=MockResponse(mock_feed_data, 200)) line bypasses the mocking mechanism and allows the actual requests.get call to go through. This indicates that the issue lies in the mocking logic.

To resolve this issue properly, let's ensure that the mock is correctly configured to simulate the requests.get call and return the expected mock response.

Error Note 4:
The 422 Unprocessable Entity status code indicates that the request payload does not meet the validation requirements defined by the QueryTimestampRequest model. This usually means that the FastAPI endpoint expected the request payload to be in JSON format, but it received query parameters instead.

In the GET request, query parameters are used, but the FastAPI endpoint expects the request body to be a JSON object. To fix this, we need to modify the endpoint to accept query parameters instead of a request body for the timestamp filters.