# In ucm_chatbot_project/urls.py
from django.contrib import admin
from django.urls import path, include # Add include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')), # Include your chat app's URLs
]