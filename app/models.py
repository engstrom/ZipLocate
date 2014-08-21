"""Models
"""

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Zip(db.Model):
    __tablename__ = 'zip'

    id = db.Column(db.Integer, primary_key=True)
    zip = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

    def __init__(self, zip, lat, lng):
        self.zip = zip
        self.lat = lat
        self.lng = lng
