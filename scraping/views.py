from calendar import c
from django.shortcuts import render
from django.http import HttpResponse,Http404
from django.conf import settings
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import random  
import string  
# Create your views here.


def hello(request):
    return render(request,"html/Scraping.html")

def download(request):
    path="Result/Scraping/Test"+request.POST["name"]+".txt"
    file_path = os.path.join(settings.BASE_DIR, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
def CollectData(request):
    Links=[]
    List=[]
    total=0
    state=False
    url=request.POST["site"]
    Request=requests.get(url,verify=False)
    Soup=BeautifulSoup(Request.text,"html.parser")
    if("mosaiquefm" in url):
        AllFigures=Soup.find_all("figure")
        for element in AllFigures:
            try:
                if "/ar/%" in element.find("a")["href"]:
                    Links.append("https://www.mosaiquefm.net"+element.find("a")["href"])
            except: 
                continue
        for Link in Links:
            List+=crawling(Link)
    if("babnet"in url):
        ListToBeScraped=list(set(FindingAllLinks(url)))
        print("Number of links about to be Scraped :",len(ListToBeScraped))
        try :
            for idx,item in enumerate(ListToBeScraped):
                L=babnet(item,idx)
                total+=len(L)
                List+=L
        except : 
            print("Bad Connection")
        print("Total of Scraped Paragraphs : ",total)
    if ("shemsfm" in url ):
        AllFigures=Soup.find_all("figure")
        Links=[]
        for element in AllFigures:
            try :
                if "/ar/%" in element.find("a")["href"]:
                    Links.append("https://www.shemsfm.net"+element.find("a")["href"])
            except: 
                continue
        Links=list(set(Links))
        List=ShamesFM(Links)
    if("jawahara" in url):
        Soup=Soup.find("div",{"class":"article"})
        Listet = ["https://www.jawharafm.net"+elem.find("a")["href"] for elem in Soup.find_all("div",{"class":"elem_ev"})]
        for url in Listet:
            List+=JawharaFM(url)
    if("interieur" in url ):
        Soup=Soup.find('div',{"class","col-sm-9 padding-right"})
        A=list(set(["https://www.interieur.gov.tn/"+item["href"] for item in Soup.find_all("a",{"href":True}) if "actualite" in item["href"]]))
        List=Interieur(A)
    num=len(List)
    if(num>0):
        state=True
        message=f"Successfully Scraped {num} paragraphs."
    if(num==0):
        message="Scraping process failed... Try later "
    name=randomname(5)
    Save(List,name)
    return render(request,"html/result.html",{
        'state':state,
        'message':message,
        'name':name,
    })

################Functions##################################
def Interieur(links):#Fonction pour collecter les paragraphs
    List=[]
    for idx ,link in enumerate(links):
        print(f"Scraping {idx+1}/{len(links)} ...")
        Soup=BeautifulSoup(requests.get(link,verify=False).text,"html.parser")
        Paragraphs=Soup.find("div",{"class":"single-blog-post"}).find_all("p")
        SmallList=[paragraph.text for paragraph in Paragraphs if len(paragraph.text)>100] 
        List+=SmallList
    return List
def JawharaFM(url):
    List=[]
    print("Scraping",url)
    Soup=BeautifulSoup(requests.get(url).text,"html.parser")
    bs=Soup.find("div",{"class":"article_text"})
    for item in bs.find_all("p"):
        List+=item.text.split("\n")
    return List
def ShamesFM(ListURL):
    List=[]
    for url in ListURL:
        print(f"Scraping : {url}")
        req=requests.get(url)
        Bs=BeautifulSoup(req.text,"html.parser")
        paragraphs=Bs.find_all("p")
        List1=[item.text for item in paragraphs]
        print(f"{len(List1)} paragraph Found.")
        List+=List1
    print(f"Done Scraping Total Amount of paragraphs :{len(List)}")
    return List
def babnet(url,idx):
    r=requests.get(url)
    Soup=BeautifulSoup(r.text,"html.parser")
    for s in Soup.find_all("div",attrs={"class":"entry-content"}):
        List=[]
        for item in s.text.split("\n"):
            if len(item)>100:
                List.append(item)
        List=list(set(List))
        print(f"{len(List)} Paragraphs Scraped from Link {idx+1}" )
    return List
def FindingAllLinks(url):
    req=requests.get(url)
    DelicousSoup=BeautifulSoup(req.text,"html.parser")
    DelicousSoup=DelicousSoup.find("div",{"class":"block category-listing"})
    List=[]
    for Link in DelicousSoup.find_all("a",href=True):
        if("rttdetail" in Link["href"]) or ("cadredetail" in Link["href"]):
            List.append("https://www.babnet.net/"+Link["href"])
    return List

def clean_diacritics (text):
    arabic_diacritics = re.compile("""
                             ّ    | # Shadda
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    text = re.sub(arabic_diacritics, '', text)
    return text
def StripingExtraSpaces(text):
    return ' '.join(text.split()) 
def Save(listParagraph,name):
    print('Saving & cleaning data ...')
    listParagraph=[clean_diacritics(elem) for elem in listParagraph]
    df=pd.DataFrame(listParagraph,columns=["paragraph"])
    df["paragraph"] = df["paragraph"].str.replace('[^\w\s]',' ')
    df["paragraph"] = df["paragraph"].str.replace(f'\n','',regex=True)
    df["paragraph"] = df["paragraph"].str.replace(f'\t','',regex=True)
    df["paragraph"] = df["paragraph"].str.replace('\"',' ',regex=True)
    df["paragraph"] = df["paragraph"].str.replace('\'',' ',regex=True)
    df["paragraph"] = df["paragraph"].str.replace(r'[a-zA-Z?]','',regex=True)
    df["paragraph"].apply(StripingExtraSpaces)
    df=df.drop_duplicates(subset=None,keep="first")
    listParagraph=[item for item in df["paragraph"]]
    with open("Result/Scraping/Test"+name+".txt", 'w', encoding='utf-8') as file:
        for element in listParagraph :
            file.write(element+"\n\n")
    print(f'{len(listParagraph)} Paragraphs Saved')
def crawling(url):
    req=requests.get(url)
    List=[]
    DeliSoup=BeautifulSoup(req.text,"html.parser")
    Soup=DeliSoup.find("div",{"class":"desc"})
    for elm in Soup.find_all("p"):
        List.append(elm.text)
    print(len(List)," Paragraph Crawled") 
    return List
def randomname(length):
    name=''.join((random.choice(string.ascii_letters) for x in range(length)))
    return name