from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
from flask_cors import CORS, cross_origin
import urllib.request
import json
from flask import Flask, jsonify, request
import cv2
from pathlib import Path
import re

subscription_key = "8f6206b450a04b0ab2e9c700d1fc1247"
endpoint = "https://intellsrvison.cognitiveservices.azure.com/"

##FLASK FRAMEWORK
app = Flask(__name__)

# if not cors_origins:
CORS(app)

@app.route("/",methods=["POST"])
@cross_origin()
def main():

    if request.method == "POST":
        dataAll=json.loads(request.get_data())

    fileName = dataAll['fileName']

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    # Get an image with text
    #read_image_url = "https://intellisr2storage.blob.core.windows.net/images/documents_needed_au_student_visa_650x300.jpg"
    read_image_url = "https://intellisr2storage.blob.core.windows.net/images/"+fileName

    path=str(Path.cwd())+"/images/"+fileName
    # download an image for validation
    urllib.request.urlretrieve(read_image_url,path)
    #detectCorners(path)

    # Open the image
    read_image = open(path, "rb")

    # Call API with image and raw response (allows you to get the operation location)
    read_response = computervision_client.read_in_stream(read_image, raw=True)

    # Get the operation location (URL with an ID at the end) from the response
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]

    # Call the "GET" API and wait for it to retrieve the results 
    while True:
        read_result = computervision_client.get_read_result(operation_id)
        if read_result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    # Print the detected text, line by line
    if read_result.status == OperationStatusCodes.succeeded:
        for text_result in read_result.analyze_result.read_results:
            response=ocr(text_result.lines,fileName)
    
    return jsonify(response)

def ocr(text_result,name):
    type=name.split("_")[0]
    if type=='drivinglicensefront':
        ocrData={}
        i=0
        for line in text_result:
                print(line.text)
                first=line.text.split(" ")[0]
                i=i+1
                if first=='5.':
                    ocrData["LID"]=line.text.replace("5.", "")
                elif first=='4d.':
                    ocrData["NIC"]=line.text.replace("4d.", "")    
                elif first=='1,2.':
                    name=line.text.replace("1,2.", "")
                    if text_result[i].text.split(" ")[0] != '8.':
                        name=name+" "+text_result[i].text
                    ocrData["name"]=name
                elif first=='8.':
                    ad=line.text.replace("8.", "")
                    if text_result[i].text.split(" ")[0] != '3.' or line.text.split(".")[0] != 3:
                        if text_result[i].text.split(" ")[0] == 'SL':
                            ad=ad+" "+text_result[i+1].text
                        else:
                            ad=ad+" "+text_result[i].text    
                    ocrData["address"]=ad  
                elif first=='3.' or line.text.split(".")[0] == 3:
                    ocrData["dob"]=line.text.replace("3. ", "")               
                
        print(ocrData)                       
        return ocrData
    elif type=='drivinglicensefrontold':
        ocrData={}
        for line in text_result:
                print(line.text)
                first=line.text.split(":")[0]
                if first=='DL No':
                    ocrData["LID"]=line.text.split(":")[1]
                elif first=='ID No':
                    ocrData["NIC"]=line.text.split(":")[1]    
        print(ocrData)                       
        return ocrData
    elif type=='newnicfront':
        ocrData={}
        i=0
        for line in text_result:
                print(line.text)
                first=line.text.split(" ")[0]
                matchDOB = re.search(r'(\d+/\d+/\d+)',line.text)
                matchNIC = re.findall(r'(\d{12})',line.text)
                i=i+1
                if matchNIC:
                    ocrData["NIC"]=matchNIC[0]
                elif matchDOB:
                    ocrData["DOB"]=matchDOB.group(1)    
                elif first=='Name :' or  first=='Name:':
                    name=line.text.replace("Name :", "")
                    name=name.replace("Name:", "")
                    if 'Sex' in text_result[i].text:
                        name=name
                    else:    
                        name=name+" "+text_result[i].text
                        if 'Sex' in text_result[i+1].text:
                            name=name
                        else:    
                            name=name+" "+text_result[i+1].text    
                    ocrData["Name"]=name           
                
        print(ocrData)                       
        return ocrData
    elif type=='newnicback':
        for line in text_result:
                print(line.text)
        return 4
    elif type=='oldnicfront':
        ocrData={}
        for line in text_result:
                matchNIC9 = re.findall(r'(\d{9})',line.text)
                matchNIC12 = re.findall(r'(\d{12})',line.text)
                if matchNIC9 or matchNIC12:
                    ocrData["NIC"]=line.text
        print(ocrData)             
        return ocrData
    elif type=='oldnicback':
        #can be ignored
        for line in text_result:
                print(line.text)
        return 'oldnicback'
    elif type=='passport':
        ocrData={}
        i=0
        for line in text_result:
                print(line.text)
                matchNIC = re.findall(r'[0-9]{5,15}[A-Z]{1}$',line.text)
                passport = re.findall("PASSPORT",line.text)
                detName = re.findall("<",line.text)
                matchPassportNo = re.findall(r'^[A-Z]{1,2}[0-9]{7,10}$',line.text)
                i=i+1
                if matchNIC:
                    ocrData["NIC"]=matchNIC[0]
                    matchDOB = re.search(r'(\d+/\d+/\d+)',text_result[i-2].text)
                    if matchDOB:
                        ocrData["DOB"]=matchDOB.group(1)    
                elif matchPassportNo:
                    ocrData["passportNo"]=matchPassportNo[0]
                elif detName:
                    Names=line.text.split("<")
                    name=""
                    matchPassportNo2 = re.findall(r'^[A-Z]{1,2}[0-9]{7,10}$',Names[0])
                    if matchPassportNo2:
                        ocrData["passportNo2"]=Names[0]
                    else:    
                        for words in Names:
                            name=name+" "+words
                        ocrData["name"]=name                  
        print(ocrData)                       
        return ocrData

def detectCorners(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 120, 255, 1)

    corners = cv2.goodFeaturesToTrack(canny,4,0.5,50)

    for corner in corners:
        x,y = corner.ravel()
        cv2.circle(image,(x,y),5,(36,255,12),-1)

    cv2.imshow('canny', canny)
    cv2.imshow('image', image)
    cv2.waitKey()

if __name__ == '__main__':
    app.run(debug=True)