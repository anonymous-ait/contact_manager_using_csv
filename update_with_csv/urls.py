from django.urls import path 
from .views import ContactView

urlpatterns =[
    path('upload-csv/',ContactView.as_view())
]