memegen is a program to add text to an image set. If you have a series of images and them recombine then you have a meme gif.  
All movie manipulation is expected to be done seperately in a program like ffmpeg
  
# Requirements  
  python3.x  
  python packages: pillow  
  
# Usage  
    > python memegen.py path/to/config/file
 Optional  
    -d for frame count delimiter in the filename  
  
# configuration file  
  1. File must be comma or semicolon style csv in first line but not both  
  1. before a line to add comments  
  1. frame number supports multiple frames  
     ex. 1-5 would apply text to all frames 1 to 5 inclusive  
  1. x and y allows for movement with > seperator  
  1. Required in the file:  
    :path,path/to/frames/dir  
  1. Change global font size with line:  
    :font_size,< size >  
