import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///starter_code/Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station
app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
            f"Availabld Routes:<br/"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs"
            f"/api/v1.0/<start>"
            f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return the last 12 months of precipitation data"""
    values = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= '2016-08-23').\
    order_by(measurement.date).all()
    return jsonify(values)
session.close()

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of all stations"""
    stations = session.query(session.query(measurement.station, func.count(measurement.station)).\
    order_by(func.count(measurement.station).desc()).\
    group_by(measurement.station).all())
    return jsonify(stations)
session.close()

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Return a list of dates and temperatures for the last 12 months of data"""
    most_active = session.query(measurement.station, func.count(measurement.station)).\
    order_by(func.count(measurement.station).desc()).\
    group_by(measurement.station).first()
    most_active_station = most_active[0]
    tobs = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == most_active_station).\
    filter(measurement.date >= '2016-08-18').\
    order_by(measurement.date).all()
    return jsonify(tobs)
session.close()

@app.route("api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    """Return a list of min, max and average temperatures for a given date"""
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    values = []
    for min, avg, max in results:
        dict = {}
        dict["min"] = min
        dict["avg"] = avg
        dict["max"] = max
        values.append(dict)
    return jsonify(values)
session.close()

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    """Return a list on min, max and average temperatures for a given start and end date"""
    results_2 = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date<= end).all()
    values_2 = []
    for min, avg, max in results:
        dict = {}
        dict["min"] = min
        dict["avg"] = avg
        dict["max"] = max
        values_2.append(dict)
    return jsonify(values_2)
session.close()

if __name__== '__main__':
    app.run(debug=True)
