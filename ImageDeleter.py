from os import listdir
from xml.etree import ElementTree
from numpy import zeros
from numpy import asarray
from matplotlib import pyplot
from PIL import Image
import os

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