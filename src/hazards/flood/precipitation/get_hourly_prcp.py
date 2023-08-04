import sys
import os
import urllib2
import datetime
import time
import psycopg2
from subprocess import call, Popen

# pull the last hours worth of precip data 
os.system("wget http://www.srh.noaa.gov/ridge2/Precip/qpehourlyshape/latest/last_1_hours.tar.gz -O last_1_hours.tar.gz")
os.system("mv last_1_hours.tar.gz last_1_hours.tar")
os.system("tar xvf last_1_hours.tar")

last_1hr_shp = './latest/last_1_hours.shp'
last_hr_shp2pgsql = 'ogr2ogr -f "PostgreSQL" PG:"user=postgres dbname=hamlet password=password" {} -t_srs EPSG:4326 -nln last_1hr_qpe -overwrite'.format(last_1hr_shp)
call(last_hr_shp2pgsql, shell = True)

