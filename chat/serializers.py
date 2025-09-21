# In chat/serializers.py
from rest_framework import serializers

class QuestionSerializer(serializers.Serializer):
    """Validates the incoming question from the user."""
    question = serializers.CharField(max_length=500, required=True)

class AnswerSerializer(serializers.Serializer):
    """Formats the outgoing answer from the chatbot."""
    answer = serializers.CharField()