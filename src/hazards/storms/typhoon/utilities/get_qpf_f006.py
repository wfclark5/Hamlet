import sys
import os
import urllib2
import datetime
import time
import psycopg2
from subprocess import call, Popen

# pull the last hours worth of precip data 
os.system("wget http://www.srh.noaa.gov/ridge2/Precip/qpfshp/latest/latest_rqpf_f006.tar.gz -O latest_rqpf_f006.tar.gz")
os.system("mv latest_rqpf_f006.tar.gz latest_rqpf_f006.tar")
os.system("tar xvf latest_rqpf_f006.tar")

latest_rqpf_f00g_shp = './latest/last_1_hours.shp'
last_hr_shp2pgsql = 'ogr2ogr -f "PostgreSQL" PG:"user=postgres dbname=hamlet password=password" {} -t_srs EPSG:4326 -nln latest_rqpf_f006 -overwrite'.format(latest_rqpf_f00g_shp)
print last_hr_shp2pgsql
call(last_hr_shp2pgsql, shell = True)


conn_string = "dbname='hamlet' user=postgres port='5432' host='127.0.0.1' password='password'"

print "Connecting to database..."

try:
	conn = psycopg2.connect(conn_string)
except Exception as e:
	print str(e)
	sys.exit()

print "Connected!\n"

drop_cur = conn.cursor()

#creating views that show where the roads are potentially flooded or exposed to icy conditions

drop_cur.execute("""drop table if exists roads_flooded_bunco cascade;""")

drop_cur.execute("""drop table if exists roads_flooded_se_heavy cascade;""")

drop_cur.execute("""drop table if exists roads_flooded_se_moderate cascade;""")

drop_cur.execute("""drop table if exists roads_flooded_se_light cascade;""")

drop_cur.execute("""drop table if exists roads_flooded_se_drizzle cascade;""")

conn.commit()
drop_cur.close()

flooded_cur = conn.cursor() 

flooded_cur.execute("""
create table roads_flooded_bunco as 
select
a.gid,
street_nam,
sum(b.globvalue),
a.geom
from conterlines_poly as a
inner join last_1hr_prcp as b 
on st_dwithin(a.geom::geometry(MULTIpolygon, 4326), b.wkb_geometry::geometry(point, 4326), 0.025)
group by a.gid, a.street_nam, a.geom;""")

flooded_cur.execute("""create table roads_flooded_se_heavy as 
select
gid
street_nam,
sum(b.globvalue),
a.geom
from se_road_polys as a
inner join last_1hr_prcp as b 
on st_dwithin(a.geom::geometry(MULTIpolygon, 4326), b.wkb_geometry::geometry(point, 4326), 0.025)
where b.globvalue >= 1
group by a.gid, a.geom;""")

flooded_cur.execute("""create table roads_flooded_se_moderate as 
select
gid
street_nam,
sum(b.globvalue),
a.geom
from se_road_polys as a
inner join last_1hr_prcp as b 
on st_dwithin(a.geom::geometry(MULTIpolygon, 4326), b.wkb_geometry::geometry(point, 4326), 0.025)
where b.globvalue >= .5
group by a.gid, a.geom;
""")

flooded_cur.execute("""create table roads_flooded_se_light as 
select
gid
street_nam,
sum(b.globvalue),
a.geom
from se_road_polys as a
inner join last_1hr_prcp as b 
on st_dwithin(a.geom::geometry(MULTIpolygon, 4326), b.wkb_geometry::geometry(point, 4326), 0.025)
where b.globvalue >= .25
group by a.gid, a.geom;""")

flooded_cur.execute("""create table roads_flooded_se_drizzle as 
select
gid
street_nam,
sum(b.globvalue),
a.geom
from se_road_polys as a
inner join last_1hr_prcp as b 
on st_dwithin(a.geom::geometry(MULTIpolygon, 4326), b.wkb_geometry::geometry(point, 4326), 0.025)
where b.globvalue >= .1 and b.globvalue <= .25
group by a.gid, a.geom;""")


conn.commit()
flooded_cur.close()