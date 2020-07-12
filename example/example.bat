IF EXIST frames RD /S /Q frames
python "../gifextract/gifextract.py"
python "../memegen.py" "ex.csv"
ffmpeg -framerate 7 -i .\frames\memegen\ex-%%02d.png -y output.gif