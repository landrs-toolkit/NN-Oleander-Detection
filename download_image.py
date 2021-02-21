# imports
import requests # to get image from the web
import shutil # to save it locally
import os
import sys
import csv
import cv2
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
    for object_label in object_labels:
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
                        # iterate through the all the labels created on the asset image
                        for object in objects:
                            if object['title'] == label_list[i]:
                                if image_downloaded: pass
                                else:
                                    # download original image if did not
                                    dir_name = paths[3*i]
                                    file_name = '{}{}{}.png'.format(project_name, '0'*(5-len(str(n))), n)
                                    save_image(asset_url, dir_name, file_name)
                                    image_no[i] += 1
                                    image_downloaded = True
                                # download masks of labeled objects
                                mask_url = object['instanceURI'] # mask instance URI
                                dir_name = paths[3*i+1]
                                file_name = '{}{}{}_mask{}.png'.format(project_name, '0'*(5-len(str(n))), n, mask_index)
                                save_image(mask_url, dir_name, file_name)
                                mask_index += 1 # increment mask index
                                masks.append(file_name)
                                for mask in masks:
                                    r = cv2.imread(os.path.join(dir_name, file_name)).astype('float32')
                                    result = result + r
                        if image_downloaded:
                            # overlay masks
                            result = 255*result
                            result = result.clip(0, 255).astype('uint8')
                            # save overlaid mask
                            dir_name = paths[3*i+2]
                            file_name = '{}{}{}_mask.png'.format(project_name, '0'*(5-len(str(n))), n)
                            cv2.imwrite(os.path.join(dir_name, file_name), result)
                            print('Mask successfully generated:  ', os.path.join(dir_name, file_name))
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
