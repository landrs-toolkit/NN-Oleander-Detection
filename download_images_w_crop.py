import numpy
from PIL import Image, ImageDraw
#code from jialongw - download_image() method modified
# imports
import requests # to get image from the web
import shutil # to save it locally
import os
import sys
import csv
# import cv2
import argparse
from ast import literal_eval

# global variables
project_name = ''
paths = []
label_list = []
image_select = False
ID_list = []
size = None


def set_paths():
    global paths
    for object_label in label_list:
        for item in ['Images', 'Labels', 'Masks']:
            paths.append(os.path.join(project_name, object_label, item))

def make_directories():
    for path in paths:
        try:
            os.makedirs(path) # make directories
        except OSError as e:
            print ("Creation of the directory %s failed: %s" % (path, format(e)))
        else:
            print ("Successfully created the directory %s " % path)

def get_IDs(txtfile):
    try:
        tf = open(txtfile, 'r')
        line_list = [line.rstrip('\n') for line in tf]
        tf.close()
    except FileNotFoundError:
        print('File {} does not exist'.format(txtfile))
        sys.exit()
    else:
        s = set(line_list) # remove deplicates
        return s

def download_images(csv_file):
    global size
    try:
        # read data
        with open(csv_file, 'rt') as file:
            data = csv.reader(file)
            # Sniffer class to deduce the format of a CSV file and detect whether a header row is present
            # along with the built-in next() function to skip over the first row only when necessary
            has_header = csv.Sniffer().has_header(file.read(1024))
            file.seek(0)
            if has_header: # skip header row
                next(data)
            # if size is given, download the limited number of images
            # else, download all
            if size is None:
                data = list(data)
                size = len(data)
            number_of_downloaded = 1
            image_no = [] # tracks the number of images under each label
            for i in range(len(label_list)):
                image_no.append(1)
            for row in data:
            # iterate through the rows
                if number_of_downloaded <= size:
                    # load data
                    asset_ID = row[0] # load image ID
                    asset_url = row[2] # load original image url
                    labels = literal_eval(row[3]) # label entry converted to dictionary
                    if len(labels) == 0: # if no labels created
                        continue         # skip the current row
                    else:
                        objects = labels['objects'] # load label instances
                    if image_select:                 # if textfile was passed to select image for download
                        if asset_ID in ID_list:      # if current ID required
                            ID_list.remove(asset_ID) # remove the asset ID from the list and do the download
                        else: continue               # else if not required, skip the current row
                    # iterate through labels to download images and masks of each label
                    for i in range(len(label_list)):
                        image_downloaded = False
                        n = image_no[i]
                        masks = []
                        mask_index = 1
                        result = 0
                        file_name = ""
                        pnum = 1 # polygon crop num
                        bnum = 1 # box crop num
                        # iterate through the all the labels created on the asset image
                        for object in objects:
                            if object['title'] == label_list[i]:
                                if image_downloaded: 
                                    dir_name = paths[3*i]
                                    if object['title'] == "Oleander Plant":
                                        param = object['polygon'] #takes in crop coord as dict
                                        crop_param = []
                                        for xy in param: #iterates over values and adds to crop_param
                                            crop_param.append((xy["x"],xy["y"]))
                                        polygon_crop(dir_name, file_name, crop_param, file_name + "_polycrop_{}.png".format(pnum))
                                        pnum += 1
                                    if object['title'] == "Not oleander":
                                        param = object['bbox'] #takes in crop coord as dict
                                        crop_param = []
                                        crop_param.append((param["top"],param["left"]))
                                        crop_param.append((param["top"] + param["height"],param["left"]))
                                        crop_param.append((param["top"] + param["height"],param["left"] + param["width"]))
                                        crop_param.append((param["top"],param["left"] + param["width"]))
                                        polygon_crop(dir_name, file_name, crop_param, file_name + "_boxcrop_{}.png".format(bnum))
                                        bnum += 1
                                else:
                                    # download original image if did not
                                    dir_name = paths[3*i]
                                    file_name = '{}{}{}.png'.format(project_name, '0'*(5-len(str(n))), n)
                                    save_image(asset_url, dir_name, file_name)
                                    image_no[i] += 1
                                    image_downloaded = True

                                    # crop polygon
                                    if object['title'] == "Oleander Plant":
                                        param = object['polygon'] #takes in crop coord as dict
                                        crop_param = []
                                        for xy in param: #iterates over values and adds to crop_param
                                            crop_param.append((xy["x"],xy["y"]))
                                        polygon_crop(dir_name, file_name, crop_param, file_name + "_polycrop_{}.png".format(pnum))
                                        pnum += 1

                                    # crop bounding box
                                    if object['title'] == "Not oleander":
                                        param = object['bbox'] #takes in crop coord as dict
                                        crop_param = []
                                        crop_param.append((param["top"],param["left"]))
                                        crop_param.append((param["top"] + param["height"],param["left"]))
                                        crop_param.append((param["top"] + param["height"],param["left"] + param["width"]))
                                        crop_param.append((param["top"],param["left"] + param["width"]))
                                        polygon_crop(dir_name, file_name, crop_param, file_name + "_boxcrop_{}.png".format(bnum))
                                        bnum += 1
                    #             # download masks of labeled objects
                    #             mask_url = object['instanceURI'] # mask instance URI
                    #             dir_name = paths[3*i+1]
                    #             file_name = '{}{}{}_mask{}.png'.format(project_name, '0'*(5-len(str(n))), n, mask_index)
                    #             save_image(mask_url, dir_name, file_name)
                    #             mask_index += 1 # increment mask index
                    #             masks.append(file_name)
                    #             for mask in masks:
                    #                 r = cv2.imread(os.path.join(dir_name, file_name)).astype('float32')
                    #                 result = result + r
                    #     if image_downloaded:
                    #         # overlay masks
                    #         result = 255*result
                    #         result = result.clip(0, 255).astype('uint8')
                    #         # save overlaid mask
                    #         dir_name = paths[3*i+2]
                    #         file_name = '{}{}{}_mask.png'.format(project_name, '0'*(5-len(str(n))), n)
                    #         cv2.imwrite(os.path.join(dir_name, file_name), result)
                    #         print('Mask successfully generated:  ', os.path.join(dir_name, file_name))
                    number_of_downloaded += 1 # increment number of downloaded asset
                else: break
    except FileNotFoundError:
        print('File {} does not exist'.format(txtfile))
        sys.exit()
    if not data:
        raise ValueError('No data available')

def save_image(image_url, dir_name, file_name):
    # Open the url image, set stream to True, this will return the stream content.
    # stream = True to guarantee no interruptions
    r = requests.get(image_url, stream = True)
    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        # Open a local file with wb ( write binary ) permission.
        with open(os.path.join(dir_name, file_name), 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print('Image sucessfully downloaded: ', os.path.join(dir_name, file_name))
    else:
        print("Image couldn\'t be retreived")

def polygon_crop(dir_name, im_file, crop_param, save_filename):
    #code to poly crop - https://stackoverflow.com/questions/22588074/polygon-crop-clip-using-python-pil

    # read image as RGB and add alpha (transparency)
    im = Image.open(os.path.join(dir_name, im_file)).convert("RGBA")

    # convert to numpy (for convenience)
    imArray = numpy.asarray(im)

    # create mask
    polygon = crop_param
    maskIm = Image.new('L', (imArray.shape[1], imArray.shape[0]), 0)
    ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)
    mask = numpy.array(maskIm)

    # assemble new image (uint8: 0-255)
    newImArray = numpy.empty(imArray.shape,dtype='uint8')

    # colors (three first columns, RGB)
    newImArray[:,:,:3] = imArray[:,:,:3]

    # transparency (4th column)
    newImArray[:,:,3] = mask*255

    # back to Image from numpy
    im_crop = Image.fromarray(newImArray, "RGBA")
    im_crop.save(os.path.join(dir_name, save_filename))

# def get_avg_dim(img_params):
#     # for image in folder
#     # add h,w to list img_params
#     # find mean https://www.geeksforgeeks.org/python-column-mean-in-tuple-list/

#     def avg(list): # returns average of elements in a tuple
#         return sum(list)/len(list) 
                
#     average = tuple(map(avg, zip(*img_params))) 

#     return average

# def box_crop(im_file, avg_height, avg_width, crop_param):
#     # keep cropping and saving files until max possible
#     # boxes with height weight cut out per image
#     im = Image.open(im_file)
#     im_width, im_height = int(im.size)
#     left = 0 # left most coord of image
#     upper = 0 # top most coord
#     im_num = 1

#     while left < im_width and upper < im_height:
#         if left + avg_width > im_width or upper + avg_height > im_height:
#             im_crop = im.crop((left, upper, im_width, im_height))
#             left = im_width
#             upper = im_height
#             im_crop.save("{}_boxcrop_{}.png".format(im_file, im_num)
        
#         im_crop = im.crop((left, upper, left + avg_width, upper + avg_height)) # crop to size of avg polygon param
#         im_crop.save("{}_boxcrop_{}.png".format(im_file, im_num)
#         left += avg_width 
#         upper += avg_height # traverse to next section of img
#         im_num += 1

if __name__=='__main__':
    # define the name of the directory to be created
    parser = argparse.ArgumentParser()
    # -p PROJECT_NAME -l LABELS -csv CSV_FILE -txt TXT_FILE -size NUMBER OF IMAGES
    parser.add_argument('-p', '--projname', help = 'Project name')
    parser.add_argument('-l', '--labels', help = 'Labels (separated by commas)')
    parser.add_argument('-csv', '--csvfile', help = 'CSV filename')
    parser.add_argument('-txt', '--txtfile', help = 'Text filename to download specified images')
    parser.add_argument('-s', '--size', help = 'Number of images to be downloaded', type=int)
    args = parser.parse_args()

    if len(sys.argv) == 1:
        print('-h for help')
    else:
        project_name = args.projname
        project_labels = args.labels.split(',')
        for label in project_labels:
            label_list.append(label)
        set_paths()
        make_directories()
        csv_file = args.csvfile
        if args.txtfile is not None:
            image_select = True
            ID_list = get_IDs(args.txtfile)
        if args.size is not None:
            size = args.size
        download_images(csv_file)
        if ID_list: # if ID list still has items after the download
            print('Images with the following IDs were not availble:')
            for item in ID_list:
                print(item)
        else: print('All completed')