# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt



# 5. Copy your project code into the container
COPY . /app/

# RUN chmod +x /app/entrypoint.sh


# 6. Expose the port Django runs on
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]