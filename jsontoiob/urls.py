from django.urls import path
from . import views

urlpatterns = [
    path("",views.hello,name="json"),
    path("transresult/",views.result,name="trans"),
    #path("Telecharger/", views.Telecharger,name="Telecharger"),
]
