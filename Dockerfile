# Using Python 3.12 slim image
FROM python:3.12-slim-bullseye AS base

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.2

# Copy only files necessary for dependencies to avoid cache busting
COPY poetry.lock pyproject.toml ./

# Export poetry dependencies to requirements.txt and install them
RUN poetry export -o requirements.txt --without-hashes
RUN pip install --no-cache-dir -r requirements.txt

# Install uvicorn with performance extras
RUN pip install uvicorn[standard]

# Add the rest of the application files
COPY . .

# Optional: Create a non-root user to run the application
RUN addgroup --system app && adduser --system --group app
USER app

# Expose the application on port 8000
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
