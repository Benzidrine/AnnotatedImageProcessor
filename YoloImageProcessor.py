import os
import CommonLibrary
from PIL import Image
from xml.etree import ElementTree

# ------------------
# The purpose of this is to process license plate number photos and their annotations into a coherently numbered set of image files and matching annotation
# ------------------

class YoloImageProcessor:
    """
    Process raw images to fit in with yolo requirements
    Note as written currently it is intend for single class training
    """
    @classmethod
    def Convert(cls, rawImageDirectory: str, rawAnnotationDirectory: str, outputImageDirectory: str, outputAnnotationDirectory: str):
        """
        Begin converting images and annotations from raw to yolo appropriate formats
        """
        currentStartingNumber = cls.FindStartNumber(rawImageDirectory)
        # Loop through raw images to save as jpeg in images directory with numbered filename
        for filename in os.listdir(rawImageDirectory):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                currentStartingNumber += 1
                tempImage = Image.open(os.path.join(rawImageDirectory,filename))
                tempImage = tempImage.convert('RGB')
                newFileName = str(currentStartingNumber) + '.jpg'
                tempImage.save(outputImageDirectory + '/' + newFileName)
                # Find the annotation for image
                for annotFilename in os.listdir(rawAnnotationDirectory):
                    # has the annotation been found yet
                    annotationFound = False
                    # load and parse the file
                    try:
                        tree = ElementTree.parse(rawAnnotationDirectory + '/' + annotFilename)
                    except:
                        continue
                    # get the root of the document
                    root = tree.getroot()
                    # create annotation file
                    for annotContainsFileName in root.findall('.//filename'):
                        if annotContainsFileName.text == filename:
                            # Change annotation to file for yolo
                            boxes = list()
                            for box in root.findall('.//bndbox'):
                                xmin = int(box.find('xmin').text)
                                ymin = int(box.find('ymin').text)
                                xmax = int(box.find('xmax').text)
                                ymax = int(box.find('ymax').text)
                                coors = [xmin, xmax, ymin, ymax]
                                boxes.append(coors)
                            # Get image size
                            with open(os.path.join(outputAnnotationDirectory,str(currentStartingNumber)) + '.txt', 'w+') as f1:
                                for box in boxes:
                                    coorX, coorY, coorW, coorH = cls.coordinateCvt2YOLO(tempImage.size, box)
                                    f1.write("0 " + str(coorX) + " " + str(coorY) + " " + str(coorW) + " " + str(coorH))
                            break
                    if annotationFound == True:
                        break

    @staticmethod
    def coordinateCvt2YOLO(size, box):
        """
        Takes the PASCAL VOC Format box and returns a YOLO type format
        """

        dw = 1. / size[0]
        dh = 1. / size[1]

        # (xmin + xmax / 2)
        x = (box[0] + box[1]) / 2.0
        # (ymin + ymax / 2)
        y = (box[2] + box[3]) / 2.0

        # (xmax - xmin) = w
        w = box[1] - box[0]
        # (ymax - ymin) = h
        h = box[3] - box[2]

        x = x * dw
        w = w * dw
        y = y * dh
        h = h * dh
        return (round(x, 3), round(y, 3), round(w, 3), round(h, 3))

    @staticmethod
    def FindStartNumber(inputImageDirectory):
        """
        Find the number for which to start labeling images
        The intention is that images begin from 0.jph - infitinity.jpg
        """
        # Initial number if no images found
        currentStartingNumber = 0  
        for filename in os.listdir(directory):
            if filename.endswith(".jpg"):
                tempFilename = filename.replace(".jpg","")
                tempNumber, trySuccess = CommonLibrary.IntTryParse(tempFilename)
                if (trySuccess and (tempNumber > currentStartingNumber)):
                    currentStartingNumber = tempNumber
        return currentStartingNumber
        
