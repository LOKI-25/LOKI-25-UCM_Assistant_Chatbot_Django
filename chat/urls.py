# In chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Point to the new ChatAPIView, using .as_view() for class-based views
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
]