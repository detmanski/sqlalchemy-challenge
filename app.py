import warnings
warnings.filterwarnings('ignore')
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///starter_code/Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(autoload_with=engine)

measurement = Base.classes.measurement
station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
            f"Available Routes:<br/>"
            f"Precipitation: /api/v1.0/precipitation<br/>"
            f"Stations: /api/v1.0/stations<br/>"
            f"Temperature for one year: /api/v1.0/tobs<br/>"
            f"Temperature from start date(yyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
            f"Temperature from start to end date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    """Return the last 12 months of precipitation data"""
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= '2016-08-23').\
    order_by(measurement.date).all()
    session.close()
    values = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        values.append(prcp_dict)

    return jsonify(values)  

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of all stations"""
    station_results = session.query(measurement.id, measurement.station).all()
    session.close()
    station_values = []
    for id, station in station_results:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_values.append(station_dict)

    return jsonify(station_values)  

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Return a list of dates and temperatures for the last 12 months of data"""
    last_year_results= session.query(measurement.date).\
        order_by(measurement.date).first()
    print(last_year_results)
    last_year_values = []
    for date in last_year_results:
        last_year_dict = {}
        last_year_dict['date'] = date
        last_year_values.append(last_year_dict)
    print(last_year_values)
    query_start = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    print(query_start)
    active_station = session.query(measurement.station, func.count(measurement.station)).\
        order_by(func.count(measurement.station).desc()).\
        group_by(measurement.station).first()
    most_active_station = active_station[0]
    session.close()
    print(most_active_station)
    active_last_year_results = session.query(measurement.date, measurement.tobs, measurement.station).\
        filter(measurement.date > query_start).\
        filter(measurement.station == most_active_station)
    active_last_year_values = []
    for date, tobs, station in active_last_year_results:
        active_dict = {}
        active_dict["date"] = date
        active_dict["tobs"] = tobs
        active_dict["station"] = station
        active_last_year_values.append(active_dict)

    return jsonify(active_last_year_values) 

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    """Return a list of min, max and average temperatures for a given date"""
    start_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()
    start_values = []
    for min, avg, max in start_results:
        start_dict = {}
        start_dict["min"] = min
        start_dict["avg"] = avg
        start_dict["max"] = max
        start_values.append(start_dict)
    
    return jsonify(start_values)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    """Return a list on min, max and average temperatures for a given start and end date"""
    start_end_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date<= end).all()
    session.close()
    start_end_values = []
    for min, avg, max in start_end_results:
        start_end_dict = {}
        start_end_dict["min"] = min
        start_end_dict["avg"] = avg
        start_end_dict["max"] = max
        start_end_values.append(start_end_dict)
    
    return jsonify(start_end_values)
    
if __name__== '__main__':
    app.run(debug=True)
