### ZipLocate

An API for geolocating zip codes, available at [ziplocate.us](http://ziplocate.us/).

#### Setting up the self-hosted version of the API:

- Clone the source from Github

```
$ git clone https://github.com/nathancahill/ZipLocate.git
```

- Create a virtualenv and install the requirements

```
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

- Edit ```config.example.py``` to ```config.py```

- Create the database models

```
>>> import config
>>> from app import create_app, db
>>> db.create_all(app=create_app(config))
```

- Install GDAL (tutorials available online)
- Install Fiona and Shapely

```
$ pip install Fiona
$ pip install Shapely
```

- Download the latest zip code data

Currently, as of 2014 (502M):

[ftp://ftp2.census.gov/geo/tiger/TIGER2014/ZCTA5/tl_2014_us_zcta510.zip](ftp://ftp2.census.gov/geo/tiger/TIGER2014/ZCTA5/tl_2014_us_zcta510.zip)

Or browse the datasets here, look for ZCTA5 (ZIP Code Tabulation Areas):

[https://www.census.gov/geo/maps-data/data/tiger-line.html](https://www.census.gov/geo/maps-data/data/tiger-line.html)

- Extract the shapefile to the app directory, beside the import.py script.

- Import the data

```
$ python import.py tl_2014_us_zcta510.shp
```

Import process takes a few minutes to complete.

- Start the app
```
$ python cli.py
 * Running on http://127.0.0.1:5000/
```

- Test a zip code query

[http://127.0.0.1:5000/api/v1/80301](http://127.0.0.1:5000/api/v1/80301)