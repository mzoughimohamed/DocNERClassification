from cgitb import html
from django.shortcuts import render,HttpResponse
import re
import spacy
from spacy.displacy import render as rend
# Create your views here.
def prediction(request):
    return render(request,"html/Prediction.html")

def results(request):
    Succes=False
    message="Unable to Classify the document"
    labels=[]
    Values=[]
    entites={}
    counter={}
    html=''
    Conversion={"POLITIQUE":"Political",
        "ECONOMIE":"Economical",
        "SANTÉ":"Healthcare",
        "CULTURE ET ART":"Cultural & artistic",
        "MÉDIAS":"Media",
        "SPORT":"Sports",
        "SECURITÉ ET DEFENSE":"Security & defense issues",
        "TECHNOLOGIE":"Tech",
        "EDUCATION":"Educational"}
    if request.method=="POST":
        data=request.POST
        nlp=spacy.load("/home/mzoughimed/Documents/PFE/showcase/showcase/output/model-best")
        doc=nlp(preprocess(data["paragraph"]))
        Entities=[elem.label_ for elem in doc.ents]
        Counter={elem.label_:0 for elem in doc.ents}
        for elem in Entities:
            Counter[elem]+=1
        Percent={key:round(100*value/total,2) for total in (sum(Counter.values()),) for key , value in Counter.items() }
        labels=[elem for elem in Counter]
        Values=[value for key,value in Percent.items()]
        Occurance=[value for key,value in Counter.items()]
        if len(labels)>0:
            Succes=True
            genre=max(Percent,key=Percent.get)
            message=f"The document tend to be a  {Conversion[genre]} document."
            entites=[{"Class":labels[i],"Percent":Values[i]} for i in range(len(labels))]
            counter=[{"Class":labels[i],"Percent":Occurance[i]} for i in range(len(labels))]
            colors = {"POLITIQUE": "aqua",
            "ECONOMIE":"dodgerblue",
            "MÉDIAS":"purple",
            "SANTÉ":"blueviolet",
            "CULTURE ET ART":"azure",
            "SPORT":"cornflowerblue",
            "TECHNOLOGIE":"crimson",
            "SECURITÉ ET DEFENSE":"dimgrey",
            "EDUCATION":"indigo"
            }
            options = {"ents": ["POLITIQUE","ECONOMIE","SANTÉ","CULTURE ET ART","MÉDIAS","SPORT","SECURITÉ ET DEFENSE","TECHNOLOGIE","EDUCATION"], "colors": colors}
            html=rend(doc,style='ent',jupyter=False)#,options=options)
            html=''.join(html.split('\n'))
            print(counter)
            print(entites)
        context={
            'Succes':Succes,
            'labels':labels,
            'values':Values,
            'message':message,
            'entites':counter,
            'html':html,
        }
    return render(request,"html/Prediction.html",context)

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
def process(text):
    text=clean_diacritics(text)
    text = re.sub('[^\w]+|_',' ', text, flags=re.U)
    text=re.sub(r'[a-zA-Z?]','',text)
    text=re.sub(f'\n','',text)
    text=re.sub(f'\t','',text)
    text=re.sub('\'','',text)
    text=re.sub('\"','',text)
    text =re.sub(" +"," ",text)
    return text
def preprocess(text):
    text=process(text)
    text = re.sub("[إأٱآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    return text