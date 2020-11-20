from ImageDeleter import ImageDeleter

imageDeleter = ImageDeleter()
imageDeleter.DeleteUnannotated('RawImages/','RawAnnots/')
imageDeleter.DeleteImagesWithoutBox('RawImages/','RawAnnots/')
#imageDeleter.DeleteUnannotated('Processed/Images/','Processed/Annots/')
#imageDeleter.DeleteImagesWithoutBox('Processed/Images/','Processed/Annots/')