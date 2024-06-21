# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
import os

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# database connection

# RELATIVE PATH
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# ABSOLUTE PATH
# script_dir = "C:\\Users\\USER\\FOLDER\\sqlalchemy-challenge\\SurfsUp"
# os.chdir(script_dir)
# absolute_path = os.path.join(script_dir, "Resources", "hawaii.sqlite")
# engine = create_engine(f"sqlite:///{absolute_path}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

# Create an app
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query for the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    
    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    stations_data = session.query(Station.station).all()
    
    # Convert the query results to a list
    stations_list = [station[0] for station in stations_data]
    
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    # Find the most active station ID
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
                                 .group_by(Measurement.station)\
                                 .order_by(func.count(Measurement.station).desc())\
                                 .first()[0]
    
    # Calculate the date one year from the last date in the data set
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query the last 12 months of temperature observation data for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago
    ).all()
    
    # Convert the query results to a list
    temperature_list = [tobs for date, tobs in temperature_data]
    
    return jsonify(temperature_list)


@app.route("/api/v1.0/<start>")


@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start=None, end=None):
    # Select the desired columns and filter by date
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    if not end:
        # Calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
        results = session.query(*sel).filter(Measurement.date >= start).all()
    else:
        # Calculate TMIN, TAVG, and TMAX for dates between the start and end date inclusive
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert the query results to a list
    temperature_stats_list = list(np.ravel(results))
    
    return jsonify(temperature_stats_list)

# Run the Flask app:
if __name__ == '__main__':
    app.run(debug=True)


