from django.urls import path
from . import views
urlpatterns = [
    path('', views.prediction,name="prediction"),
    path("result/",views.results,name="results")
]