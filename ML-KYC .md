# Deployment Concerns

## Front End Integration

### Source Code Integration

#### Resources

* 6 files to host Tensorflow js
Host these files as static content that can access by url
* One is the main
model.json
* Five Ancillary ones
group1-shard1of5.bin
group1-shard2of5.bin
group1-shard3of5.bin
group1-shard4of5.bin
group1-shard5of5.bin

#### Integration Steps

1. Host those 6 files as static content that can access by url
2. Replace MODEL_URL constatnt inside index.html file with url of model.json file.
3. Replace (accountName,sasString,containerName,containerURL) with to your azure storage account details.
4. Integrate content of the index.html file with any front end application.

###  SaaS Service

1.Azure storage account with container to store images to access as urls.

## Back End Integration

### Source Code Integration

#### Resources

* flask server details TBD

-/backend
   app.py
   requirements.txt
   
* pip resources file

#### Integration Steps

1. RUN pip install -r /requirements.txt.
2. Replace (subscription_key,endpoint) with your azure computer vision keys.
3. Replace Image_container with your azure storage account container url.

### SaaS Service

1. blob storage - include pricing and docs link
https://azure.microsoft.com/en-us/pricing/details/storage/blobs/#pricing

2. Computer vision services - include pricing and docs link
please checkout the OCR section
https://azure.microsoft.com/en-us/pricing/details/cognitive-services/computer-vision/#pricing

## Model Maintainance 

### Retrain Model

1. Insert images in to folders and run colab notebook.
https://colab.research.google.com/drive/1z2u8arJhdLL559YAPkRC6k492gNv4jDe?usp=sharing
2. Download the 6 TF js model files and rehost into same environment.

## Ongoing Monitoring
