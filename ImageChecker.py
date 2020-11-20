# plot one photograph and mask
from os import listdir
import typing
from xml.etree import ElementTree
from numpy import zeros
from numpy import asarray
from matplotlib import pyplot
from PIL import Image
import cv2
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
            masks = zeros([height, width, 1], dtype='uint8')
            for i in range(len(boxes)):
                box = boxes[i]
                row_s, row_e = box[1], box[3]
                col_s, col_e = box[0], box[2]
                masks[row_s:row_e, col_s:col_e, 0] = 1
            # plot image
            image = Image.open(images_dir + '/' + filename)
            pyplot.imshow(image)
            # plot mask
            pyplot.imshow(masks[:, :, :],  alpha=0.5)
            pyplot.show()
            numberOfImagesChecked += 1
            if numberOfImagesChecked >= numToCheck:
                break

    # Find duplicate images
    @classmethod
    def FindDuplicateImages(cls, imageDirectory: str):
        duplicatedImages: typing.List[str] = []
        # Find all images
        for filename in listdir(imageDirectory):
            imageHashOne = cls.CreateImageHashProcess(imageDirectory, filename) 
            if imageHashOne is not None:
                for filenameTwo in listdir(imageDirectory):
                    # Check it isn't the same file
                    if filename != filenameTwo:
                        if imageHashOne == cls.CreateImageHashProcess(imageDirectory, filenameTwo):
                            print("duplicate found:","First Image:", filename, "SecondImage:", filenameTwo)
                            duplicatedImages.append(filename)
        return duplicatedImages

    # Find duplicate images
    @classmethod
    def FindDuplicateImagesTwo(cls, imageDirectory: str, targetDirectory: str):
        duplicatedImages: typing.List[str] = []
        # Find all images
        for filename in listdir(imageDirectory):
            imageHashOne = cls.CreateImageHashProcess(imageDirectory, filename) 
            if imageHashOne is not None:
                for filenameTwo in listdir(targetDirectory):
                    # Check it isn't the same file
                    if filename != filenameTwo:
                        if imageHashOne == cls.CreateImageHashProcess(targetDirectory, filenameTwo):
                            print("duplicate found:","First Image:", filename, "SecondImage:", filenameTwo)
                            duplicatedImages.append(filename)
        return duplicatedImages

    @staticmethod
    def CreateImageHashProcess(imageDirectory: str, filename: str):
        """
        Store the code pattern that creates an Image Hash
        """
        # Check if image
        if '.jpg' in filename:
            image = cv2.imread(os.path.join(imageDirectory,filename))
            # If the image is None then we could not load it from disk (so skip it)
            if image is not None:
                # Convert the image to grayscale and compute the hash
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                imageHash = ImageChecker.DifferenceHash(image)
                return imageHash
        return None
    
    @staticmethod
    def DifferenceHash(image: Image, hashSize: int = 8):
        """
        Create a difference hash for a given image
        """
        # resize the input image, adding a single column (width) so we
        # can compute the horizontal gradient
        resized = cv2.resize(image, (hashSize + 1, hashSize))
        # compute the (relative) horizontal gradient between adjacent
        # column pixels
        diff = resized[:, 1:] > resized[:, :-1]
        # convert the difference image to a hash
        return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

 
    # extract bounding boxes from an annotation file
    @staticmethod
    def extract_boxes(filename: str):
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