from os import listdir
import typing
from xml.etree import ElementTree
from numpy import zeros
from numpy import asarray
from matplotlib import pyplot
from ImageChecker import ImageChecker
from PIL import Image
import os
import cv2

"""
Delete those images that are unannotated
"""
# class that deletes images
class ImageDeleter():
    @classmethod
    def ClearOutImagesAndAnnotations(cls, images_dir: str, annotation_dir: str):
        """
        Clear out images
        """
        for filename in listdir(images_dir):
            os.remove(os.path.join(images_dir,filename))
        for filename in listdir(annotation_dir):
            os.remove(os.path.join(annotation_dir,filename))

    @classmethod 
    def DeleteImagesWithoutBox(cls, images_dir: str, annotations_dir: str):
        """
        Delete Images that don't have a box in their annotation
        """        
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
            boxes, width, height = ImageChecker.extract_boxes(annotations_dir + '/' + correctAnnotFileName)
            if len(boxes) < 1:
                print("Deleted Image that didn't have box:", filename)
                os.remove(os.path.join(images_dir,filename))
    
    @classmethod
    def DeleteFromListOfImageNames(cls, listOfImages: typing.List[str], images_dir: str):
        for filename in listOfImages:
            for filenameTwo in listdir(images_dir):
                if filename == filenameTwo:
                    print("Deleted Image:", filename)
                    os.remove(os.path.join(images_dir,filename))

    # Find duplicate images and delete them
    @classmethod
    def DeleteDuplicateImages(cls, imageDirectory: str):
        HashList = {}
        # Create Hash List
        for filename in listdir(imageDirectory):
            HashList[filename] = cls.CreateImageHashProcess(imageDirectory, filename)

        # Find all images
        for filename in listdir(imageDirectory):
            imageHashOne = cls.CreateImageHashProcess(imageDirectory, filename) 
            if imageHashOne is not None:
                for key, hash in HashList.items():
                    # Check it isn't the same file
                    if filename != key:
                        if imageHashOne == hash:
                            print("duplicate deleted:","First Image:", filename, "SecondImage:", key)
                            os.remove(os.path.join(imageDirectory,filename))
                            break

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

        
    @classmethod
    def DeleteUnannotated(cls, images_dir: str, annotations_dir: str):
        """
        delete unannotated images
        """
        numberDeleted = 0
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
                os.remove(os.path.join(images_dir,filename))
                numberDeleted += 1
                print(filename + " deleted")
        print("Number Deleted: " + str(numberDeleted))