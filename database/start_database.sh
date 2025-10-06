#!/bin/bash


# Start containers
echo "Starting containers..."
docker-compose --env-file ../.env up

sleep 10

# Check status
echo "Checking container status..."
docker-compose ps


