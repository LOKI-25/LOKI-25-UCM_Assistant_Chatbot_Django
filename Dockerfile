# Dockerfile

# 1. Use an official Python runtime as a parent image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app


RUN apt-get update && apt-get install -y \
    unzip \
    awscli \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python-specific libraries
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


# 5. Copy your project code into the container
COPY . /app/

# 6. Expose the port Django runs on
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]