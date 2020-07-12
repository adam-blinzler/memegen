memegen is a program to add text to an image. If you have a series of images and then recombine then you have a meme gif.  
All movie manipulation is expected to be done seperately. Recommended ffmpeg
  
Usage  
   >python memegen.py   path/to/config/file  
   Optional  
         - d for frame count delimiter  
  
configuration file  
   1. File must be semicolon style csv with delim ;  
   2. before a line to add comments  
   3. frame number supports multiple frames  
      ex. 1-5 would apply that text to all frames 1 to 5 inclusive  
   4. Parameters  
      Required anywhere in file:  
         :path;path/to/frames/dir  