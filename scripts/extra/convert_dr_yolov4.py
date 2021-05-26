import os
import re
import sys

"""
Update Notes: (@yej117)

- The result.txt written format seems to be un-matched in the current yolov4 version.
    
    The current predicted results are written in the following format:

    Enter Image Path:  Detection layer: 139 - type = 28 --> line_prev
    Detection layer: 150 - type = 28 
    Detection layer: 161 - type = 28 
    $filepath: Predicted in 1091.078000 milli-seconds. --> line_jpg
    $class: $score%        (left_x:     5   top_y:  363   width:  158   height:  126)
    $class: $score%        (left_x:   145   top_y:  415   width:   21   height:   23)

- Using Regular expression for reading the results

- Move the original result.txt to input/detection-results/backup/

"""

# make sure that the cwd() in the beginning is the location of the python script (so that every path makes sense)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

IN_FILE = 'result.txt'

# change directory to the one with the files to be changed
parent_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
parent_path = os.path.abspath(os.path.join(parent_path, os.pardir))
DR_PATH = os.path.join(parent_path, 'input','detection-results')
#print(DR_PATH)
os.chdir(DR_PATH)

#global stripsym
if sys.platform == "linux":
    stripsym = "/"
elif sys.platform == "win32" or sys.platform == "cygwin":
    stripsym = "\\"


SEPARATOR_KEY = 'Enter Image Path:'
IMG_FORMAT = '.jpg'

# define the regular expression for reading the results
TERM = re.compile("(?P<class>\w+): (?P<score>\d+)\%\s+\(left_x:\s+(?P<xmin>-?\d+)\s+top_y:\s+(?P<ymin>-?\d+)\s+width:\s+(?P<width>-?\d+)\s+height:\s+(?P<height>-?\d+)\)")


line_prev = None
line_jpg = None
image_path = None
outfile = None
with open(IN_FILE) as infile:
    for line_no, line in enumerate(infile):
        if SEPARATOR_KEY in line:
            image_path = None
            line_jpg = line_no + 3
            line_prev = line_no
        elif line_no == line_jpg:
            image_path = line.split(':')[0]
            image_name = image_path.split(stripsym)[-1].split(".")[0]
            # close the previous file
            if outfile is not None:
                outfile.close()
            # open a new file
            outfile = open(os.path.join(DR_PATH, image_name + '.txt'), 'w')
        elif image_path != None:
            results = TERM.search(line)
            class_name = results["class"]
            confidence = int(results["score"])
            left = int(results["xmin"])
            top = int(results["ymin"])
            width = int(results["width"])
            height = int(results["height"])
            right = left + width
            bottom = top + height
            outfile.write("{} {} {} {} {} {}\n".format(class_name, float(confidence)/100, left, top, right, bottom))

# Backup the original result.txt
if not os.path.exists("backup"):
    os.makedirs("backup")

os.rename(IN_FILE, "backup/"+IN_FILE)
