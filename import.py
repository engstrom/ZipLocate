"""Import zip codes from ZCTA5 shapefile
"""


import sys

import fiona
from shapely.geometry import shape

import config
from app import create_app
from app.models import db, Zip

if len(sys.argv) != 2:
    print 'Run script with shapefile as an argument: python import.py shapefile.shp'
    exit()

db.app = create_app(config)

with fiona.open(sys.argv[1]) as f:
    for record in f:
        centroid = shape(record['geometry']).centroid

        z = Zip(record['properties']['ZCTA5CE10'], centroid.y, centroid.x)
        db.session.add(z)

db.session.commit()
