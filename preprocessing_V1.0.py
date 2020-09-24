# Written by Niall Beggan 23-9-2020
# To learn about editing txt files in python 
# For a project with Patrick Moreau, to automatically
# read image information from whatsapp and log it to a database.


## This program must run in a folder that contains two separate .txt exports of the whatsapp chat,
## a new and old one with some difference between them and also the associated chat images.
## Once finished this program deletes the old .txt and renames the new file as "oldfile"
## It also DELETES ALL WHATSAPP .JPG FILES IN THE FOLDER THIS PROGRAM IS RUN!!

## USE WITH CAUTION!!!!!

##################### Import libraries #####################

import cv2
import os
from os import path
from os import listdir

##################### Assign variables #####################

oldChatfilename = "oldfile.txt"
newestChatfilename = "WhatsApp Chat with Practice group.txt"

trainingImageKey = ".jpg (file attached)"
trainingImageKey2 = "Training\n"

def preprocessing():
    imageStrings = list()
    outputImageList = list()

    if not(path.exists("output")) :
        os.mkdir("output") # make output folder
    outputPath = "output"

    ##################### Open text files #####################

    oldChat = open(oldChatfilename, "r+")
    newestChat = open(newestChatfilename, "r+")

    ##################### Find last line of oldChat #####################
    string_list = oldChat.readlines()
    lastLine = len(string_list)
    lastlineString = string_list[lastLine-1]

    ###################### Find location of that line in the newest chat #####################
    string_list2 = newestChat.readlines()
    newMessagesStart = string_list2.index(lastlineString)
    newMessagesStart += 1
    length = len(string_list2)
    string_list3 = string_list2[newMessagesStart:length]

    ##################### Search for 'training' images (unique charachter combinations) #####################

    # Search for following substring ".jpg (file attached)"
    imageList = [i for i in string_list3 if trainingImageKey in i] # This image could be random OR training images
    # Search for following line "Training"
    for i in imageList :
        locationInOriginalFile = string_list3.index(i)
        if(string_list3[locationInOriginalFile+1] == trainingImageKey2) :  # Add that line to list of image ID strings
            imageStrings.append(string_list3[locationInOriginalFile])

    ##################### Search for that image in the directory, copy, rename and move to output directory #####################
    # Unique ID number because otherwise if someone sends in two images the first image is overwritten
    UniqueID = 0
    for i in imageStrings :
        UniqueID += 1
        splitString = i.split()
        # Remove ':' , '/' and ',' they cause problems
        name = splitString[3].replace(":","")
        date = splitString[0].replace('/','_')
        date = date.replace(',','')
        image = cv2.imread(splitString[4])
        # cv2.imwrite(name + "_" + date + "_" + str(UniqueID) + ".jpg" ,image) # outputs images in current folder
        cv2.imwrite(os.path.join(outputPath , (date + "-" + name + "-" + str(UniqueID) + ".jpg")), image)
        outputImageList.append(date + "-" + name + "-" + str(UniqueID) + ".jpg")
        
    ##################### Clean up and reset #####################

    # Update oldchat and delete newchat
    oldChat.close()
    newestChat.close()

    os.remove(oldChatfilename) # Old chat deleted
    os.rename(newestChatfilename, oldChatfilename) # New chat becomes old chat

    # delete original photos
    fileList = os.listdir()
    jpgList = [i for i in fileList if ".jpg" in i]
    whatsappJpgList = [i for i in fileList if "-WA" in i]
    count = 0
    for i in whatsappJpgList :
        os.remove(whatsappJpgList[count])
        count += 1

    # Done
    return outputImageList
