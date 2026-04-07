#!/bin/sh

echo "Waiting for database..."
until python manage.py dbshell --silent; do
  echo "Database is unavailable - sleeping"
  sleep 2
done
echo "Database is up"

echo "Running migrations..."
python manage.py migrate --no-input

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000