import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


from flask import Flask, jsonify


# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

def date_prev_year():
    # Create the session
    session = Session(engine)

    # Define the most recent date in the Measurement dataset
    # Then use the most recent date to calculate the date one year from the last date
    most_recent_date = session.query(func.max(Measurement.date)).first()[0]
    first_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Close the session                   
    session.close()

    # Return the date
    return(first_date)
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

#############################################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all dates and prcp"""
    # Query all prcp
    results_last_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_prev_year()).all()
   

    session.close()

     # Convert list of tuples into dictionary
    all_precepitation=[]
    for date,prcp in results_last_year:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precepitation.append(precipitation_dict)

    return jsonify(all_precepitation)

#########################################################################
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#########################################################################
@app.route("/api/v1.0/tobs")
def temptobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations for the previous year"""
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    tobs_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= date_prev_year()).all()


    session.close()

    # Convert list of tuples into dictionary
    all_tobs=[]
    for date,tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

#########################################################################
@app.route("/api/v1.0/<start>")
def temp_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #variable for specified start date format
    spec_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    
    """Return a JSON list For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date"""
    start_calc_list = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    calc_results = session.query(*start_calc_list).filter(func.strftime('%Y-%m-%d', Measurement.date) >= spec_date).all()

    session.close()

    return (
        f"Temperature from {start} to 2017-08-23 (the latest measurement in database):<br/>"
        f"Minimum temperature: {round(calc_results[0][0], 1)} <br/>"
        f"Average temperature: {round(calc_results[0][1], 1)} <br/>"
        f"Maximum temperature: {round(calc_results[0][2], 1)} "
    )
    

#########################################################################
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
   # Create our session (link) from Python to the DB
    session = Session(engine)

    #changing date format type
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date =  dt.datetime.strptime(end, '%Y-%m-%d').date()

    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    start_calc_list = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    #query date calculations
    date_temp = session.query(*start_calc_list).filter(func.strftime('%Y-%m-%d', Measurement.date) >= start_date).filter(func.strftime('%Y-%m-%d', Measurement.date) <= end_date).all()
    
    session.close()

    return (
        f"Temperature from {start} to {end}:<br/>"
        f"Minimum temperature: {round(date_temp[0][0], 1)} <br/>"
        f"Average temperature: {round(date_temp[0][1], 1)} <br/>"
        f"Maximum temperature: {round(date_temp[0][2], 1)} "
    )



if __name__ == '__main__':
    app.run(debug=True)
