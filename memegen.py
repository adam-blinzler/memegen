# Notes:
#          All images in processing folder need to be of 1 type ( png, jpg, or jpeg )

import os
import glob
import shutil
import argparse
#requires install of pillow
from PIL import Image, ImageDraw, ImageFont

delim_default = '-'
indent = "    "
image_types = ['png', 'PNG','jpg', 'JPG','jpeg', 'JPEG']

def draw_on_image(i, new_frame, frame_configs, font_name = 'arial.ttf', font_size = 44, color = 'white', shadowcolor = 'black'):
    draw_frame = ImageDraw.Draw(new_frame) 
    font = ImageFont.truetype(font_name, size=font_size)
    # Loop through multiple writes on the same frame
    for config in frame_configs:
        x = config['x']
        y = config['y']
        message = config['text']
         # thin border ( add +- to other coord for thick )
        draw_frame.text((x-1, y), message, font=font, fill=shadowcolor)
        draw_frame.text((x+1, y), message, font=font, fill=shadowcolor)
        draw_frame.text((x, y-1), message, font=font, fill=shadowcolor)
        draw_frame.text((x, y+1), message, font=font, fill=shadowcolor)
        # draw the message on the background
        draw_frame.text((x, y), message,  font=font, fill=color)

    return new_frame

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
                    frame = draw_on_image(i, frame, frame_configs[i])
                    frame.save(file, os.path.splitext(file)[1][1:])
                    print(indent + file)
        else:
            print("No files in working directory.")
    else:
        print("No files found of any type : " ', '.join(image_types))
    return

def add_frame_config(frame_configs, line):
    # dissector for fames in config file
    cols = line.split(';')
    if not int(cols[0]) in frame_configs:
        frame_configs.update( { int(cols[0]) : [ { 'text' : cols[1], 'x' :  int(cols[2]), 'y' : int(cols[3])} ] } )
    else:
        frame_configs[int(cols[0])].append({ 'text' : cols[1], 'x' :  int(cols[2]), 'y' : int(cols[3])})
    return frame_configs

def frame_config_reader(lines):
    # dissector for config file
    path = False
    frame_configs = dict()
    for line in lines:
        if line[0] == "#":
            pass
        elif ":path" in line[0:5]:
            path = line.split(';')[1]
            if not os.path.isdir(path):
                print("Path in config file is not valide : " + path )
                path = False
        else:
            cols = line.split(';')
            if '-' in cols[0]:
                for i in range(int(cols[0].split('-')[0]),int(cols[0].split('-')[1])+1):
                    temp_line = [str(i)]
                    temp_line.extend(cols[1:])
                    frame_configs = add_frame_config(frame_configs,';'.join(temp_line))
            else:
                frame_configs = add_frame_config(frame_configs, line)  
    
    return path, frame_configs

def get_frame_configs(config_file):
    # read config file
    if os.path.isfile(config_file):
        print("Using Text Config file ...")
        print(indent + config_file)
        
        frame_configs = dict()
        with open(config_file, 'r') as f:
            f_lines = f.readlines()
        path, frame_configs = frame_config_reader(f_lines)
    if path:
        return path, frame_configs
    else:
        return False, False

def memegen(config_path, file_delim = delim_default):
    # main function for memegen
    path, frame_configs = get_frame_configs(config_path)
    if frame_configs:
        add_text(path,frame_configs, file_delim)
    return

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
            return args.config_path, file_delim

    print("Invalid configuration file path.\n")
    parser.print_help()
    return False, None

""" ------
   MAIN
""" 
if __name__ == "__main__":
    memegen(*args())
    
    print("Script Finished")
