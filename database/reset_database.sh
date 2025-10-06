#!/bin/bash

# Script to completely reset the database
echo "Resetting PostgreSQL database..."
# Stop and remove containers
echo "Stopping containers..."
docker-compose --env-file ../.env down
# Remove volumes (data)
echo "Removing data..."
docker-compose --env-file ../.env down -v

echo "Database reset completely!"

