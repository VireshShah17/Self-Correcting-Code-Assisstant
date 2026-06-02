# Start with a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# The agent will dynamically add new pip installs below this line:
RUN pip install requests