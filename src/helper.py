"""
@brief: Helper functions for the Auto-eraser.

@author: Rahul Karanam

@date: 2022-05-01
"""

# Importing the libraries

import numpy as np
import cv2
import time
import os
import copy
import mxnet as mx
from gluoncv import data, utils, model_zoo
from coco_names import COCO_INSTANCE_CATEGORY_NAMES as category_names

def filter_detections(objects_to_mask,class_ids, scores, boxes, masks):
    
    
    """
    @brief: Filters the detections based on the objects to mask.
            It removes the detections that are not in the objects to mask.
            
            Args:
                objects_to_mask: list of objects to mask
                class_ids: list of class ids
                scores: list of scores
                boxes: list of bounding boxes
                masks: list of masks
            Returns:
                class_ids: list of class ids updated
                scores: list of scores updated
                boxes: list of bounding boxes updated
                masks: list of masks updated
    """
    objects_to_be_removed = [] # list of objects to be removed
    for i in objects_to_mask:   # i is the object to be masked
        if i in objects_to_mask:    # if the object is in the list
            objects_to_be_removed.append(category_names.get(i)) # get the name of the object
            
    obj_idx = []   # indices of objects to be removed

    for i in range(class_ids.size): # loop over all detections
        if objects_to_be_removed.count(int(class_ids[i])) == 0: # if the object is not in the list of objects to be removed
            obj_idx.append(i) # append the index of the object
            
    class_ids = np.delete(class_ids, obj_idx) # delete the objects to be removed from the class_ids
    scores = np.delete(scores, obj_idx) # delete the objects to be removed from the scores
    boxes = np.delete(boxes, obj_idx, 0) # delete the objects to be removed from the boxes
    masks = np.delete(masks, obj_idx, 0) # delete the objects to be removed from the masks
    
    return class_ids, scores, boxes, masks


def tranform_detections(masks,original_image,inflate_size):
    
    """
    @brief: Transforms the detections to the desired format for inpainting.
    
    Args:
        masks: list of masks
        original_image: original image
        inflate_size: size of the inflate
        
    Returns:
        img_copy: image before output
        img_output: image after output
    """
     
    img_copy = original_image.copy() # copy the original image
    
    for mask in masks: # loop over all masks 
        k = 0 # k is the row index
        for rows in img_copy: # loop over all rows
            i = 0    # i is the column index
            for element in rows: # loop over all elements
                if (mask[k, i] != 0): # if the element is not black
                    rows[i] = [255, 255, 255] # set the element to white
                i = i + 1 # increment the column index
            k = k + 1 # increment the row index
    img_output = img_copy.copy() # copy the image before output
    k = 0 # k is the row index
    for row in img_copy: # loop over all rows
        i = 0   # i is the column index
        for element in row: # loop over all elements
            if np.array_equal(element, [255, 255, 255]):    # if the element is white (not black)
                if not only_white_px(img_output,k,i): # if the pixel is not only white
                    img_output = cv2.circle(img_output, (i, k), inflate_size, (255,255,255),0) # inflate the pixel
            i = i + 1 # increment the column index
        k = k + 1 # increment the row index
        
    mask_output = img_output.copy() # copy the image output
    
    j = 0 # j is the row index
    for row in mask_output:
        i = 0 # i is the column index
        for element in row:
            if not np.array_equal(element, [255, 255, 255]):
                row[i] = [0, 0, 0]
                
            i = i + 1
        j = j + 1
        
    return img_output, mask_output
    
    
    
    
    

            
        
def only_white_px(img,k,i):
    
    """
    @brief:Checks if the pixel is white or not.

    Args: img: image
        k: row index
        i: column index
        
    Returns: True if the pixel is white, False otherwise

    """
    try:
        if np.array_equal(img[k+1][i], [255, 255, 255]): # if the pixel is white
            return False
    except:
        pass
    try:
        if np.array_equal(img[k-1][i], [255, 255, 255]): # if the pixel is white 
            return False
    except:
        pass

    try:
        if np.array_equal(img[k][i+1], [255, 255, 255]):
            return False
    except:
        pass
    try:    
        if np.array_equal(img[k][i-1], [255, 255, 255]):
            return False
    except:
        pass
    
    return True