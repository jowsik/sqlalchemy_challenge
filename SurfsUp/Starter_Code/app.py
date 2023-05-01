# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """Return Last 12 Months of Precipitation Data"""
    # Find the most recent date in the data set.
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    one_year_earlier = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_earlier).all()
    
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_dates = []
    for date, precipitation in results:
        date_dict = {}
        date_dict["date"] = date
        date_dict["prcp"] = precipitation
        all_dates.append(date_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all station names"""
    # Query all stations
    names = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(names))
    
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():
    #Retrieve date one year before the most recent date
    one_year_earlier = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station
    active = session.query(Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= one_year_earlier).all()
    
    session.close()
    
    #Convert a list of tuples into normal list
    all_active = list(np.ravel(active))
    
    return jsonify(all_active)

@app.route("/api/v1.0/<start>/<end>")
@app.route("/api/v1.0/<start>")

    #Retrieve start date from URL
def stats(start="", end=""):
    
    # Using the start date from the previous query, calculate the lowest, highest, and average temperature from that start date to end of dataset
    if end == "":
        start = dt.datetime.strptime(start, "%Y-%m-%d")
        stats_info = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    
        session.close()
        
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(stats_info))
        return jsonify(temps)

    #Convert to datetime object
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")

    # Using the start date from the previous query, calculate the lowest, highest, and average temperature from that start date to end date
    stats_end_info = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    results = list(np.ravel(stats_end_info))
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
    
    