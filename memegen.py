# Notes:
#          All images in processing folder need to be of 1 type ( png, jpg, or jpeg )

import os
import glob
import shutil
import argparse
#requires install of pillow
from PIL import Image, ImageDraw, ImageFont

csv_delim = ';'
delim_default = '-'
indent = "    "
image_types = ['png', 'PNG','jpg', 'JPG','jpeg', 'JPEG']
font_size_default = 44

##############################################
class frame_type:
    def __init__(self, f_number):
        self.frame_number = f_number
        self.font_name = 'arial.ttf'
        self.color = 'white'
        self.shadowcolor = 'black'
        self.actions = list()
        return

    def add_action(self,text,x,y,font_size):
        self.actions.append({ 'text' : text, 'x' :  int(x), 'y' : int(y), 'font_size' : int(font_size)})
        return

    def draw_on_image(self, new_frame):
        draw_frame = ImageDraw.Draw(new_frame)

        # Loop through multiple writes on the same frame
        for config in self.actions:
            font = ImageFont.truetype(self.font_name, size=config['font_size'])
            x = config['x']
            y = config['y']
            message = config['text']
             # thin border ( add +- to other coord for thick )
            draw_frame.text((x-1, y), message, font=font, fill=self.shadowcolor)
            draw_frame.text((x+1, y), message, font=font, fill=self.shadowcolor)
            draw_frame.text((x, y-1), message, font=font, fill=self.shadowcolor)
            draw_frame.text((x, y+1), message, font=font, fill=self.shadowcolor)
            # draw the message on the background
            draw_frame.text((x, y), message,  font=font, fill=self.color)

        return new_frame

###########################################
def make_working_folder(files):
    working_folder = os.path.join(os.path.split(files[0])[0],"memegen")
    base_folder = working_folder
    i = 0
    # Don't overwrite directories, create unique
    while os.path.isdir(working_folder):
        working_folder = base_folder + '_' + str(i)
        i += 1
    os.mkdir(working_folder)

    print("Making working copy of images ...")
    print(indent + working_folder)
    for file in files:
        shutil.copy(file,working_folder)

    return working_folder, get_files(working_folder)

def get_files(path):
    # Collect all images files in path
    # No check for if they are numbered
    for file_type in image_types:
        files = glob.glob(path + '\*.' + file_type)
        if len(files) > 0:
            return files
    return False

def add_text(path, frame_configs, file_delim):
    files = get_files(path)
    if files:
        working_folder, files = make_working_folder(files)
        if files:
            print("Adding text ... ")
            for file in files:
                # Get frame number from filename
                if file_delim in os.path.splitext(os.path.split(file)[1])[0]:
                    i = int(os.path.splitext(os.path.split(file)[1])[0].split(file_delim)[1])
                else:
                    i = int(os.path.splitext(os.path.split(file)[1])[0])

                if i in frame_configs:
                    frame = Image.open(file)
                    frame = frame_configs[i].draw_on_image(frame)
                    img_type = os.path.splitext(file)[1][1:]
                    if img_type == 'jpg':
                        img_type = 'jpeg'
                    frame.save(file, img_type)
                    print(indent + file)
        else:
            print("No files in working directory.")
    else:
        print("No files found of any type : " ', '.join(image_types))
    return

def add_frame_config(frame_configs, line, font_size):
    # dissector for fames in config file
    cols = line.split(csv_delim)
    if cols[0]:
        if len(cols) > 5:
            font_size = cols[4]

        if not int(cols[0]) in frame_configs:
            frame_configs.update( { int(cols[0]) : frame_type(int(cols[0])) })

        frame_configs[int(cols[0])].add_action(cols[1],cols[2], cols[3],font_size)

    return frame_configs

def get_path(lines):
    for line in lines:
        if ":path" in line[0:5]:
            path = line.split(csv_delim)[1]
            if os.path.isdir(path):
                print("Path found",path)
                return path
            else:
                print("Path in config file is not valid : " + path )
    return False

def get_font_size(lines):
    font_size = font_size_default
    for line in lines:
        if ":font_size" in line:
            font_size = int(line.split(csv_delim)[1])
    return font_size

def frame_config_reader(lines):
    # dissector for config file
    path = get_path(lines)

    if path:
        font_size = get_font_size(lines)

        frame_configs = dict()

        for line in lines:
            if line[0] in ['#',':']:
                pass
            else:
                cols = line.split(csv_delim)
                if '-' in cols[0]:
                    for i in range(int(cols[0].split('-')[0]),int(cols[0].split('-')[1])+1):
                        temp_line = [str(i)]
                        temp_line.extend(cols[1:])
                        frame_configs = add_frame_config(frame_configs,csv_delim.join(temp_line), font_size)
                else:
                    frame_configs = add_frame_config(frame_configs, line,font_size)

        return path, frame_configs
    else:
        return False, dict()

def set_delim(line):
    global csv_delim
    if not csv_delim in line:
        if ',' in line:
            csv_delim = ','
            return True
        else:
            print("Could not determine the delimitation of csv file. Use only ; or ,")
            return False
    return True
    
def get_frame_configs(config_file):
    # read config file
    if os.path.isfile(config_file):
        print("Using Text Config file ...")
        print(indent + config_file)

        with open(config_file, 'r') as f:
            f_lines = f.readlines()

        if set_delim(f_lines[0]):
            return frame_config_reader(f_lines)

    return False, dict()

def memegen(config_path, file_delim = delim_default):
    # main function for memegen
    path, frame_configs = get_frame_configs(config_path)
    if frame_configs:
        add_text(path,frame_configs, file_delim)
    return

def is_ascii(file_path):
    with open(file_path) as f:
        header = f.readlines()[0]

    try:
        header.encode().decode('ascii')
    except UnicodeDecodeError:
        print("ERROR - File is not ascii ANSI formated.")
        return False

    return True

def args():
    parser = argparse.ArgumentParser(description="Add text to a series of images.")
    parser.add_argument('config_path', nargs='?', help='The path to the input configuration file')
    parser.add_argument('-d', '--delim', type=str, help='Use if frames have a deliminator before frame numbers')
    args = parser.parse_args()

    if args.delim:
        if len(args.d) == 1:
            file_delim = args.d
    else:
        file_delim = delim_default
    if args.config_path:
        if os.path.isfile(args.config_path):
            if is_ascii(args.config_path):
                return args.config_path, file_delim

    print("Invalid configuration file path.\n")
    parser.print_help()
    return False, None

############
#   MAIN
############
if __name__ == "__main__":
    memegen(*args())

    print("Script Finished")
