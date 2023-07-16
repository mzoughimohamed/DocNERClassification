from django.urls import path
from . import views

urlpatterns = [
    path("",views.hello,name="scrap"),
    path("download/",views.CollectData,name="download"),
    #path("down/",views.download,name="down"),
]
