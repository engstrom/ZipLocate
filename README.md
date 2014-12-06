### ZipLocate

An API for zip code geolocation, available at [ziplocate.us](http://ziplocate.us/).

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

#### Download ZCTA5 data

ZCTA5 is an approximation of zip code polygons based on US census data.

Currently, as of 2014 (502M):

[ftp://ftp2.census.gov/geo/tiger/TIGER2014/ZCTA5/tl_2014_us_zcta510.zip](ftp://ftp2.census.gov/geo/tiger/TIGER2014/ZCTA5/tl_2014_us_zcta510.zip)

Or browse the datasets here, look for ZCTA5 (ZIP Code Tabulation Areas):

[https://www.census.gov/geo/maps-data/data/tiger-line.html](https://www.census.gov/geo/maps-data/data/tiger-line.html)

#### Basic zip code centroid approximation

For advanced, population density based centroid, skip to the __Advanced__ section.

- Install GDAL (tutorials available online)
- Install Fiona and Shapely

```
$ pip install Fiona
$ pip install Shapely
```

- Extract and import the ZCTA5 data

```
$ unzip tl_2014_us_zcta510.zip
$ python import.py tl_2014_us_zcta510.shp
```

Import process takes a few minutes to complete.

#### Advanced zip code centroid approximation

For a more useful approximation of the center of zip code polygons, we can use population data to estimate population density and weight the center point around centers of population. This is considerable more complicated, if basic approximation is enough for you, you can skip this.

- Install Postgres and PostGIS (tutorials available online)

- Grab block level population centers from the latest US Census

Available here: [https://www.census.gov/geo/reference/centersofpop.html](https://www.census.gov/geo/reference/centersofpop.html). Block level is the highest granularity available.

```
$ wget https://www.census.gov/geo/reference/docs/cenpop2010/blkgrp/CenPop2010_Mean_BG.txt
```

- Create a georeferenced table in Postgres and copy the CSV in:

```
> CREATE TABLE centers(statefp VARCHAR(2),
                       countyfp VARCHAR(3),
                       tractce VARCHAR(6),
                       blkgrpce VARCHAR(1),
                       population INTEGER,
                       latitude FLOAT,
                       longitude FLOAT);
> COPY centers FROM 'CenPop2010_Mean_BG.txt' DELIMITER ',' CSV HEADER;
> AddGeometryColumn('centers', 'point', '4326', 'POINT', 2);
> UPDATE centers SET point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
> CREATE INDEX point_idx ON centers USING GIST(point);
```

- Extract and import the ZCTA5 data

```
$ unzip tl_2014_us_zcta510.zip
$ shp2pgsql tl_2014_us_zcta510 | psql
```

```
> AddGeometryColumn('tl_2014_us_zcta510', 'center', 4326, 'POINT', 2);
> UpdateGeometrySRID('tl_2014_us_zcta510', 'geom', 4326);
> CREATE INDEX zcta5_idx ON tl_2014_us_zcta510 USING GIST(geom);
```

- Calculate the population weighted center

```
> UPDATE
      tl_2014_us_zcta510
  SET
      center = (
          SELECT
              ST_SetSRID(
                  ST_Point(
                      SUM(ST_X(point) * population) / NULLIF(SUM(population), 0),
                      SUM(ST_Y(point) * population) / NULLIF(SUM(population), 0)
                  ),
              4326)

              FROM (
                  SELECT
                      centers.point,
                      centers.population
                  FROM
                      centers
                  WHERE
                      ST_Contains(tl_2014_us_zcta510.geom, centers.point)
              ) q
          );
```

- Use basic centroid approximation for zip code areas with no census data

```
> UPDATE tl_2014_us_zcta510 set center = ST_Centroid(geom) where center is null;
```

- Copy data to the API’s model (a table called 'zip')

```
> INSERT INTO zip (zip, lat, lng) (
      SELECT zcta5ce10 AS zip, ST_Y(center) AS lat, ST_X(center) AS lng FROM tl_2014_us_zcta510
);
```

#### Bonus: Canadian Postal Codes

- Download the postal codes from [Geocoder.ca](http://geocoder.ca/?freedata=1) and donate to their [legal defense fund](http://geocoder.ca/?sued=1) (currently being sued because they provide an open alternative to the expensive Canada Post database).

We only need the first 3 columns, postal code, latitude and longitude, so cut these to output.csv.

```
$ wget http://geocoder.ca/onetimedownload/Canada.csv.gz
$ gzip -d Canada.csv.gz
$ cut -f 1,2,3 -d , Canada.csv > output.csv
```

- Import into the database

```
> COPY zip from 'output.csv’ DELIMITER ',' CSV;
```

#### Start the API

```
$ python cli.py
 * Running on http://127.0.0.1:5000/
```

- Test a zip code query

[http://127.0.0.1:5000/api/v1/80301](http://127.0.0.1:5000/api/v1/80301)

### Clients

- __iOS__: https://github.com/jPaolantonio/ZipLocateiOS
- __PHP__: https://github.com/ins0/php-simple-ziplocate
- __Go__: https://github.com/kureikain/go-ziplocate
