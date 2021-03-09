# NN-Oleander-Detection
NN based Oleander Detection From Drone Imagery
## Usage Example
### Download Images
#### Command line options:
##### `-p/--projname`: project name
Project name by which the output root directory will be named
##### `-l/--labels`: labels
Labels of image annotation, sub-directories will be created for each label
##### `-csv/--csvfile`: csv file
CSV file exported from Labelbox which contains data of annotated images
##### `-txt/--txtfile`: test file
Text file which contains IDs of images selected for downloaded (optional)
##### `-s/--size`: number of images
Maximum number of images to be downloaded (optional)
##### Example
```sh
python download_image.py -p ExampleProject -l "Label 1","Label 2" -csv Example.csv -txt Example.txt -s 1
```
### NN Training
Upload to your Google Drive a zipped folder of the images downloaded
Mount your Google Drive to the notebook
Unzip the folder to load the images on the hosted server
Run the blocks to set up and train the NN
  * You may change the number of epochs to train for based on the size of your dataset
## Credits
The NN Training notebook is based on [TORCHVISION OBJECT DETECTION FINETUNING TUTORIAL](https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html)
