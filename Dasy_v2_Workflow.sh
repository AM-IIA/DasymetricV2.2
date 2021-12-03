#!/bin/sh
ls -l
cp LIDAR_heights.zip /vsizip/LIDAR_heights.zip
cp UrbanAtlas.zip /vsizip/UrbanAtlas.zip
cp Buildings.zip /vsizip/Buildings.zip
cp POPBari_2020.zip /vsizip/POPBari_2020.zip

export PYTHONPATH=$PYTHONPATH:/usr/share/qgis/python:/usr/share/qgis/python/plugins:/usr/lib/python3/dist-packages:/usr/lib/python3/dist-packages/qgis/
export LD_LIBRARY_PATH=/usr/lib
export PATH=$PATH:/usr
export XDG_RUNTIME_DIR=/home 
export RUNLEVEL=3

export GDAL_FILENAME_IS_UTF8=YES

Xvfb :99 -ac -noreset &
export DISPLAY=:99
python3 DasymetricV2.py >> test.txt
