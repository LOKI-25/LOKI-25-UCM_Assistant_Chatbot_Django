#!/bin/sh
# entrypoint.sh

# 1. Download the knowledge base from S3
# Make sure to replace <your-bucket-name> with the actual name of your S3 bucket
echo "Downloading knowledge base from S3..."
aws s3 cp s3://ucm-chatbot-kb/ucmo_chroma_store.zip /app/ucmo_chroma_store.zip

# 2. Unzip the knowledge base
echo "Unzipping knowledge base..."
unzip /app/ucmo_chroma_store.zip -d /app/

# 3. Start the application server
echo "Starting Gunicorn server..."
gunicorn -c gunicorn.conf.py ucm_chatbot_project.wsgi:application

