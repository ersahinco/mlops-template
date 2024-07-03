# MLOps Engineer Assessment Project

This project demonstrates the use of Python, FastAPI, SQLAlchemy, and Docker Compose to interact with a PostgreSQL database and the arXiv API. It's designed to fetch publication data based on criteria such as author, title, or journal, showcasing core MLOps capabilities.

## Notes
- **Project Structure**:
  - `main.py`: Entry point of the application.
  - API Core Functions: Located in `app/api/endpoints/arxiv.py`
  - Models: Located in `app/models.py`
  - Schemas: Located in `app/schemas/requests` and `app/schemas/responses`
  - Tests: Located in `app/tests/test_arxiv/test_arxiv_endpoints.py`
  - **GitHub Workflows**: Example github workflow is included in the project folder.
    - `dev_build.yml`: Builds and pushes Docker images to Docker Hub.
    - `tests.yml`: Runs unit tests using pytest.
    - `type_check.yml`: Performs type checking and code formatting checks.
  - **Test Coverage**: The test coverage is not 100%, causing failures in the GitHub workflow. This can be resolved by adding more detailed test cases.
  - **JWT Authentication**: The template includes JWT components; however, they are not utilized for endpoint authentication in this use case.

## Tech requirements

- **FastAPI**: Used to build RESTful endpoints, simplifying both development and testing processes.
- **SQLAlchemy ORM**: Handles database operations, providing a high level of abstraction from SQL code.
- **Docker Compose**: Ensures simple setup and orchestration of the application and database services.
- **Alembic**: Manages database migrations to keep the schema aligned with the current application state.
- **Pytest**: Enables comprehensive testing to ensure functionality and reliability of API endpoints.

## Getting Started

### Prerequisites

- Docker and Docker Compose must be installed on your system.

### Installation

1. Clone or download the project folder from the repository.
2. Navigate to the project folder: `cd mlops-template`
3. Launch the services with Docker Compose: `docker-compose up -d`

### Running the Application

- Access the Swagger UI at [http://localhost:8000/](http://localhost:8000/) to interact with the API. 
- The `/arxiv` endpoints can be directly tested using the "Try it out" feature in Swagger UI. Simply provide the necessary parameters or request body depending on the endpoint and execute the requests. No authentication is required to access these endpoints.


### Running Tests

- Run the tests using the following command: `pytest`

## API Endpoints

Brief descriptions of each endpoint:

- `POST /arxiv/search`: Searches the arXiv API for articles based on author, title, or journal.
- `GET /arxiv/queries`: Retrieves query records within a specified timestamp range.
- `GET /arxiv/results`: Provides stored query results, supporting pagination for large datasets.

## Contact

For any queries or further information, please email [ersahinco@gmail.com](mailto:ersahinco@gmail.com).
