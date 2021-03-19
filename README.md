# NN-Oleander-Detection
This repository contains scripts to support the training of NNs to detect Oleander plants in drone imagery.
The scripts to download images will work with csv file exported from [Labelbox](https://labelbox.com/).
The training notebook is mostly easily used in [python notebooks](https://nbviewer.jupyter.org/github/jupyter/notebook/blob/master/docs/source/examples/Notebook/What%20is%20the%20Jupyter%20Notebook.ipynb#).

[Google Colaboratory](https://colab.research.google.com/notebooks/intro.ipynb) is recommended when you require a Jupyter notebook environment with a ready-to-use GPU in the Cloud.

Currently scripts provided carry out 3 processes:
1. Fetching images from the web
2. Cropping the images according to labels 
3. Saving images in directories intended to prepare them for use in the PyTorch based NN training workflow described in [TorchVision Object Detection Finetuning Tutorial](https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html)

To use these scripts with this pipeline, first execute as described below, after which the tutorial steps may be followed as is.

## Prerequisites
Python3 and python modules:
Numpy, Pillow, OpenCV, Requests
There are multiple ways of installing the above, 1 approach is to use Anaconda.  If you use this approach the following will work on most operating systems from a terminal:
1. Install Anaconda for whichever OS you are using follow their [docs](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)
2. Create and activate a conda environment and the run the following and the example
```bash
$ conda create --name MyNewPythonEnvironment
$ conda activate MyNewPythonEnvironment
$ conda install pillow opencv requests
```

## Usage Example
### Download Images
```sh
$ python download_image.py -p ExampleProject -l "Label 1","Label 2" -csv Example.csv -txt Example.txt -s 1
```
#### Command line options:
##### `-p/--projname`: project name
Project name by which the output root directory will be named
##### `-l/--labels`: labels
Labels of image annotation, sub-directories will be created for each label
##### `-csv/--csvfile`: csv file
CSV file exported from Labelbox which contains data of annotated images
##### `-txt/--txtfile`: text file (optional)
Text file which contains IDs of images selected for downloaded
##### `-s/--size`: number of images (optional)
Maximum number of images to be downloaded

### NN Training
Upload to your Google Drive a zipped folder of the images downloaded

Mount your Google Drive to the notebook

Unzip the folder to load the images on the hosted server

Run the blocks to set up and train the NN
  * You may change the number of epochs to train for based on the size of your dataset
## Credits
The NN Training notebook is based on [TorchVision Object Detection Finetuning Tutorial](https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html)
