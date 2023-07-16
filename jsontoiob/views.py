from django.shortcuts import render
import random
import json
import string
import os
from django.conf import settings
from django.http import Http404, HttpResponse
import spacy 
from spacy.tokens import DocBin
from tqdm import tqdm
# Create your views here.
def hello(request):
    return render(request,"html/info.html")

def result(request):
    message="Failed to Transform. Please try again later."
    Number=0
    state=False
    if request.method=="POST":
        file=request.FILES["file"]
        if ".json" in file.name:
                dic= json.load(file)
                Classes=dic["classes"]
                Annotations=dic["annotations"]
                Diclass={item:0 for item in Classes}
                print(f"Number of pragraphs :{len(dic['annotations'])}")
                for item in Annotations:
                    for subitem in item[1]["entities"]:
                        Diclass[subitem[2]]+=1
                Number=len(dic['annotations'])
                nlp=spacy.load("xx_sent_ud_sm")
                db=DocBin()
                for text, annot in tqdm(Annotations): # data in previous format
                    doc = nlp.make_doc(text) # create doc object from text
                    ents = []
                    for start, end, label in annot["entities"]: # add character indexes
                        span = doc.char_span(start, end, label=label, alignment_mode="contract")
                        if span is None:
                            print("Skipping entity")
                        else:
                            if not(label in ["RELIGION","GASTRONOMIE","MODE","DIVERTISSEMENT"]):
                                ents.append(span)
                    doc.ents = ents # label the text with the ents
                    db.add(doc)
                name=randomname(8)
                documents=list(db.get_docs(nlp.vocab))
                with open("Result/Dataset/DTest"+name+".txt","w") as tf:
                    IOBFormater(documents,tf)
                message="Please download your IOB file."
                state=True
                Class=[]
                Values=[]
                for key , item in Diclass.items():
                    Class.append(key)
                    Values.append(item)
                print(Class)
                print(Values)
        else :
            message="We recommend using NER JSON format with file extension json"
    message2=f"Number of annoted documents is: {Number}"
    return render(request,"html/resultdata.html",{
        'name':name,
        'state':state,
        'message':message,
        "mes":message2,
        "class":Class,
        "values":Values,

    })
def Telecharger(request):
    path="Result/Dataset/DTest"+request.POST["name"]+".txt"
    file_path = os.path.join(settings.BASE_DIR,path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def randomname(length):
    name=''.join((random.choice(string.ascii_letters) for x in range(length)))
    return name
def IOBFormater(Documents,file):
    for doc in Documents:
        for elem in doc:
            if(elem.ent_iob_!="O"):
                stri= str(elem.text+" "+elem.ent_iob_+"-"+elem.ent_type_)+"\n"
                file.write(stri)
            elif " "in elem.text:
                print(elem.text,"Skipped")
            else :
                stri= str( elem.text+" "+elem.ent_iob_)+"\n"
                file.write(stri)
        file.write("\n")