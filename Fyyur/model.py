#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from argparse import Action
from ast import Str
from dataclasses import dataclass
from email.policy import default
import json
from tabnanny import filename_only
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import Model, SQLAlchemy
from sqlalchemy import func, inspect, or_
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    shows_id = db.relationship('Show', backref='Venue', lazy=True)

    def convert_to_dict(self):
      dict = {}
      for attributes, values in self.__dict__.items():
        dict[attributes] = values
      return dict

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows_id = db.relationship('Show', backref='Artist', lazy=True)

    def convert_to_dict(self):
      dict = {}
      for attributes, values in self.__dict__.items():
        dict[attributes] = values
      return dict



class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
    start_time = db.Column(db.String(120))

    def convert_to_dict(self):
      dict = {}
      for attributes, values in self.__dict__.items():
        dict[attributes] = values
      return dict