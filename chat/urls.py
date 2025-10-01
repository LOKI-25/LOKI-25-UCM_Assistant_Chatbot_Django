# In chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Point to the new ChatAPIView, using .as_view() for class-based views
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('health/', views.health_check, name='health_check'),
     path('api/chat/stream/', views.chat_api_stream, name='chat_api_stream'),
]