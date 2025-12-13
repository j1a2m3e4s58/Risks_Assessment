from django.urls import path
from . import views

urlpatterns = [
    # The main dashboard page
    path('', views.dashboard, name='dashboard'),
    
    # The hidden URL that triggers the download
    path('export-csv/', views.export_risks_csv, name='export-csv'),
]