#!/bin/sh

export PYTHONPATH=$PYTHONPATH:/usr/share/qgis/python:/usr/share/qgis/python/plugins:/usr/lib/python3/dist-packages:/usr/lib/python3/dist-packages/qgis/
export LD_LIBRARY_PATH=/usr/lib
export PATH=$PATH:/usr

export GDAL_FILENAME_IS_UTF8=YES

Xvfb :99 -ac -noreset &
export DISPLAY=:99
python3 DasymetricV2.py >> test.txt