from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Import your service and new serializers
from .chatbot_service import chatbot_instance
from .serializers import QuestionSerializer, AnswerSerializer
from django.http import HttpResponse
from django.http import StreamingHttpResponse, JsonResponse
from rest_framework.decorators import api_view

# This view serves your HTML page (no change here)
def index(request):
    return render(request, 'index.html')


def health_check(request):
    """A simple view that returns a 200 OK response."""
    return HttpResponse("OK", status=200)

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
    

async def chat_api_stream(request):
    """
    An asynchronous view that streams the chatbot's response using Server-Sent Events (SSE).
    """
    if request.method == "GET":
        try:
            # We manually parse the JSON here instead of using a DRF serializer
            question = request.GET.get("question")

            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)

            # Return a streaming response that calls our new async service method
            return StreamingHttpResponse(
                chatbot_instance.ask_question_stream(question),
                content_type="text/event-stream"
            )
        except Exception as e:
            # Handle potential errors during streaming
            print(f"Error during stream: {e}")
            # Note: We can't send a JSON error in the middle of a stream, but this handles initial setup errors.
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Only GET requests are allowed"}, status=405)