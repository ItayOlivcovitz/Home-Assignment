#!/bin/bash

# Define the desired number of replicas
replicas=5

# Get the current number of running 'app' service containers
current_replicas=$(docker ps --filter "name=app" --format "{{.ID}}" | wc -l)

# Check if the current number of replicas matches the desired number
if [ "$current_replicas" -eq "$replicas" ]; then
  echo "The 'app' service already has $replicas replicas. No scaling needed."
else
  # Scale the 'app' service to the specified number of replicas
  echo "Scaling the 'app' service to $replicas replicas..."
  docker-compose up -d --scale app=$replicas
  echo "The 'app' service has been scaled to $replicas replicas."
fi

# Start an interactive Bash session
exec bash
