from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Import your service and new serializers
from .chatbot_service import chatbot_instance
from .serializers import QuestionSerializer, AnswerSerializer

# This view serves your HTML page (no change here)
def index(request):
    return render(request, 'index.html')


class ChatAPIView(APIView):
    """
    API View to handle chatbot questions using DRF.
    """
    def post(self, request, *args, **kwargs):
        # Use the serializer to validate the incoming data
        question_serializer = QuestionSerializer(data=request.data)
        
        if question_serializer.is_valid():
            question = question_serializer.validated_data['question']
            
            # Use the chatbot service to get an answer
            print(f"Received question via DRF: {question}")
            answer_text = chatbot_instance.ask_question(question)
            print(f"Generated answer: {answer_text}")

            # Use the answer serializer to format the response
            response_data = {'answer': answer_text}
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        # If validation fails, return a 400 Bad Request with the errors
        return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)