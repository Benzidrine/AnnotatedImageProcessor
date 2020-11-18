import os
import CommonLibrary
from PIL import Image
from xml.etree import ElementTree
from ImageDeleter import ImageDeleter
from ImageChecker import ImageChecker

# ------------------
# The purpose of this is to process license plate number photos and their annotations into a coherently numbered set of image files and matching annotation
# ------------------

# Initial number if no images found
currentStartingNumber = 0  

# Find the latest number
directory = 'Processed/Images'
annotsDirectory = 'Processed/Annots'

# Loop through raw images to save as jpeg in images directory with numbered filename
rawDirectory = 'RawImages'
rawAnnotsDirectory = 'RawAnnots'

for filename in os.listdir(directory):
    if filename.endswith(".jpg"):
        tempFilename = filename.replace(".jpg","")
        tempNumber, trySuccess = CommonLibrary.IntTryParse(tempFilename)
        if (trySuccess and (tempNumber > currentStartingNumber)):
            currentStartingNumber = tempNumber

# Delete those images with no annotation
imageDeleter = ImageDeleter()
imageDeleter.DeleteUnannotated(rawDirectory + '/',rawAnnotsDirectory + '/')

# Check a few images 
imageChecker = ImageChecker()
imageChecker.Check_images(rawDirectory + '/',rawAnnotsDirectory + '/')

for filename in os.listdir(rawDirectory):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        currentStartingNumber += 1
        tempImage = Image.open(rawDirectory + '/' + filename)
        tempImage = tempImage.convert('RGB')
        newFileName = str(currentStartingNumber) + '.jpg'
        tempImage.save(directory + '/' + newFileName)
        # Find the annotation for image
        for annotFilename in os.listdir(rawAnnotsDirectory):
            # has the annotation been found yet
            annotationFound = False
            # load and parse the file
            try:
                tree = ElementTree.parse(rawAnnotsDirectory + '/' + annotFilename)
            except:
                continue
            # get the root of the document
            root = tree.getroot()
            # create annotation file
            for annotContainsFileName in root.findall('.//filename'):
                if annotContainsFileName.text == filename:
                    # Change filename in annotation file to reflect new name
                    annotContainsFileName.text = newFileName;
                    newXmlFile = open(os.path.join(annotsDirectory,str(currentStartingNumber)) + '.xml', 'w+')
                    docString = ElementTree.tostring(root, encoding='unicode')
                    newXmlFile.write(docString)
                    annotationFound = True
                    break
            if annotationFound == True:
                break

# Delete those images with no annotation
imageDeleter = ImageDeleter()
imageDeleter.ClearOutImagesAndAnnotations('RawImages/','RawAnnots/')