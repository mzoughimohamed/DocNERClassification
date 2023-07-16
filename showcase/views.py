from django.shortcuts import render,HttpResponse
from django.http import HttpResponse,Http404
import os
from django.conf import settings

# Create your views here.
def homepage(request):
    return render(request,"html/Homepage.html")
def Telecharger(request):
    path="Result/Dataset/DTest"+request.POST["name"]+".txt"
    file_path = os.path.join(settings.BASE_DIR,path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
def download(request):
    path="Result/Scraping/Test"+request.POST["name"]+".txt"
    file_path = os.path.join(settings.BASE_DIR, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404