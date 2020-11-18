# plot one photograph and mask
from os import listdir
from xml.etree import ElementTree
from numpy import zeros
from numpy import asarray
from matplotlib import pyplot
from PIL import Image
import os
import random

"""
Check images are masked correctly by showing them with mask one by one
"""

# class that defines and loads the Image then shows their masks
class ImageChecker():
    # load the dataset definitions
    @classmethod
    def Check_images(cls, images_dir: str, annotations_dir: str, numToCheck: int = 4):
        numberOfImagesChecked = 0
        # find all images
        for filename in listdir(images_dir):
            correctAnnotFileName = None
            # has the annotation been found yet
            annotationFound = False
            for annotFilename in listdir(annotations_dir):
                # load and parse the file
                try:
                    tree = ElementTree.parse(annotations_dir + '/' + annotFilename)
                except:
                    continue
                # get the root of the document
                root = tree.getroot()
                # create annotation file
                for annotContainsFileName in root.findall('.//filename'):
                    if annotContainsFileName.text.rstrip('\n') == filename.rstrip('\n'):
                        correctAnnotFileName = annotFilename
                        annotationFound = True
                        break
                if annotationFound == True:
                    break
            if annotationFound == False:
                print("No annotation found for:", filename)
                continue
            boxes, width, height = cls.extract_boxes(annotations_dir + '/' + correctAnnotFileName)
            # create one array for all masks, each on a different channel
            masks = zeros([height, width, len(boxes)], dtype='uint8')
            for i in range(len(boxes)):
                box = boxes[i]
                row_s, row_e = box[1], box[3]
                col_s, col_e = box[0], box[2]
                masks[row_s:row_e, col_s:col_e, i] = 1
            # plot image
            image = Image.open(images_dir + '/' + filename)
            pyplot.imshow(image)
            # plot mask
            pyplot.imshow(masks[:, :, 0], cmap='gray', alpha=0.5)
            pyplot.show()
            numberOfImagesChecked += 1
            if numberOfImagesChecked >= numToCheck:
                break

 
    # extract bounding boxes from an annotation file
    @staticmethod
    def extract_boxes(filename):
        # load and parse the file
        tree = ElementTree.parse(filename)
        # get the root of the document
        root = tree.getroot()
        # extract each bounding box
        boxes = list()
        for box in root.findall('.//bndbox'):
            xmin = int(box.find('xmin').text)
            ymin = int(box.find('ymin').text)
            xmax = int(box.find('xmax').text)
            ymax = int(box.find('ymax').text)
            coors = [xmin, ymin, xmax, ymax]
            boxes.append(coors)
        # extract image dimensions
        width = int(root.find('.//size/width').text)
        height = int(root.find('.//size/height').text)
        return boxes, width, height