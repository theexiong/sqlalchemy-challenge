# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///..///hawaii.sqlite")

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
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation</br>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert query results from precipitation analysis to dict
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()


    #Create dict with date as key and prcp as value
    precip_data = []
    for date, prcp in data:
        data_dict = {}
        data_dict["date"] = date
        data_dict["prcp"] = prcp
        precip_data.append(data_dict)
    
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    #Return json list of stations
    stations = session.query(Station.station).all()

    all_stations = list(np.ravel(stations))
    return jsonify(all_stations)
    

@app.route("/api/v1.0/tobs")
def tobs():
    #query dates and temps of most active station for previous year of data
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
              filter(Measurement.station == "USC00519281").\
                filter(Measurement.date >= previous_year).all()

    #return json list of temps
    Most_Active_temp_data = list(np.ravel(results))
    return jsonify(Most_Active_temp_data)

@app.route("/api/v1.0/<start>")
def start_date(start):

    cannonicalized = start.replace(" ", "")
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_day = session.query(*sel).\
                filter((Measurement.date) >= start).all()

    start_dates = list(np.ravel(start_day))
    return jsonify(start_dates)


@app.route("/api/v1.0/<start>/<end>")
def start_end_dates(start, end):

    new_start = start.replace(" ", "")
    new_end = end.replace(" ", "")
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_end_day = session.query(*sel).\
                filter((Measurement.date) >= start).\
                filter((Measurement.date) <= end).all()

    start_end_dates = list(np.ravel(start_end_day))
    return jsonify(start_end_dates)


session.close()

if __name__ == '__main__':
    app.run(debug=True)