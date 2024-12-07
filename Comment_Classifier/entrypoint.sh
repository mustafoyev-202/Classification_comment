#!/bin/bash
set -e 

function wait_for_db() {
  echo "Waiting for the database to be ready..."
  for i in {1..10}; do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
      echo "Database is ready!"
      return
    fi
    echo "Database is not ready yet. Retrying in 2 seconds..."
    sleep 2
  done
  echo "Database did not become ready in time. Exiting."
  exit 1
}

wait_for_db

echo "Importing CSV into the database..."
python database.py || {
  echo "Failed to import CSV. Exiting."
  exit 1
}

echo "Starting the API..."
exec "$@"
