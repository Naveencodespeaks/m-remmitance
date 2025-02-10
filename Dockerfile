FROM python:3.8.10-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-dev --no-interaction --no-ansi
COPY . /app/
EXPOSE 8000
ENV PORT=8000
RUN poetry run alembic -c /app/project/alembic.ini upgrade head
CMD ["poetry", "run", "uvicorn", "application:app", "--host", "0.0.0.0", "--port", "8000"]
