# -*- coding: utf-8 -*-
"""prediction_models_App.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_5H-Dcz_EDwSZm6ayxLwdZAPVm87uZEm
"""

import os
import tensorflow as tf
from tensorflow import keras
import tensorflow.keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import numpy as np

import cv2
from tensorflow.keras.preprocessing.image import array_to_img
from random import seed
from random import randint
from tqdm import tqdm, tqdm_notebook
from keras.preprocessing.image import ImageDataGenerator
import sys
from flask_ngrok import run_with_ngrok
from flask import Flask,request
from flask_cors import CORS
from flask import send_file
from PIL import Image
sys.path.append("/content/drive/MyDrive/Soumaya - PFE/results/saved_models/")
from load_models import *

def get_model(model_name,detection_type,augmentation=None):
    if(detection_type=="mask_classification"):
        return mask_models[model_name]
    elif(detection_type=="no_mask_classification"):
        if(augmentation=="augmentation"):
            return aug_models[model_name]
        elif(augmentation=="no_augmentation"):
            return no_aug_models[model_name]

    
def load_image(img_path, show=False,img_size=224,rescale=True):
    img = image.load_img(img_path, target_size=(img_size, img_size))
    img_tensor = image.img_to_array(img)                    
    img_tensor = np.expand_dims(img_tensor, axis=0)
    if rescale==True:
        img_tensor /= 255.                                 
    if show:
        if rescale==True:
            plt.imshow(img_tensor[0])  
        else:
            new_im=img_tensor / 255. 
            plt.imshow(new_im[0]) 
        plt.axis('off')
        plt.show()
    return img_tensor

def prediction_classification(model_name,img_path,detection_type,augmentation=None):
    model = get_model(model_name,detection_type,augmentation)
    if(model_name=="InceptionV3"):
        image_size=299
    else:
        image_size=224
    if(model_name=="VGG16" or model_name=="VGG19") and (augmentation=="augmentation"):
        resc=False
    else:
        resc=True
    new_image = load_image(img_path,img_size=image_size,rescale=resc)
    pred = model.predict(new_image)
#     print(pred)
    res={}
    res['model_name']=str(model_name)
    if(model_name=="VGG16" or model_name=="VGG19") and (augmentation=="augmentation"):
        if(pred[0][0]>0.5):
            res['accuracy']=round(pred[0][0]*100,5)
            res['test']='un Tumeur detecté'
        else:
            res['accuracy']=100-round(pred[0][0]*100,5)
            res['test']='Aucun Tumeur detecté'
    else:
        preds = np.argmax(pred, axis=1)
#         print(preds)
        if(preds==0):
            res['accuracy']=round(pred[0][0]*100,5)
            res['test']='Aucun Tumeur detecté'
        else:
            res['accuracy']=round(pred[0][1]*100,5)
            res['test']='un Tumeur detecté'
    return res

def unet_prediction(imgPath):
    seed(1)
    value = randint(0, 1000)
    image = cv2.imread(imgPath)
    ImgHieght = 256
    ImgWidth = 256
    img = cv2.resize(image ,(ImgHieght, ImgWidth))
    img = img / 255
    img = img[np.newaxis, :, :, :]
    pred=unet.predict(img)
    im=np.squeeze(pred)
    im=im*1000
    new_img_path="/content/drive/MyDrive/Soumaya - PFE/results/predicted_segmentation_images/predicted_unet_images/unet_"+str(value)+os.path.basename(imgPath)
    max=im[0][0]
    res={}
    k=0
    l=0
    for i in range(0,256):
      for j in range(0,256):
        if im[i][j]>max:
          max=im[i][j]
          k=i
          l=j
    if max>500:
      cv2.imwrite(new_img_path,im)
      res['test']="Un Tumeur detecté"
      print("un Tumeur detecté")
    else:
      cv2.imwrite(new_img_path,image)
      res['test']="Aucun tumeur detecté"
      print("Aucun tumeur detecté")
    res['image_path']= new_img_path
    print("im[",k,"][",l,"]=",max)
    return res

def get_image_location(request,UPLOAD_FOLDER):
  image = request.files['image']
  if image:
    image_location = os.path.join(
        UPLOAD_FOLDER,
        image.filename
    )
  image.save(image_location)
  return image_location