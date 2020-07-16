# Dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
import datetime as dt


###################################################
# Database Setup
###################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Assign the classes to respective tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session
session = Session(engine)


####################################################
# Flask Setup
###################################################
app = Flask(__name__)


####################################################
# Flask Routes
####################################################

#----------------------
# Home page route
#List all routes that are available.
#----------------------
@app.route("/")
def home():
    return ("Hawaii homepage. These are the available routes: <br/>"
    "/api/v1.0/precipitation<br/>"
    "/api/v1.0/stations<br/>"
    "/api/v1.0/tobs<br/>"
    "Please enter start date in below api in the format YYYY-MM-DD<br/>"
    "/api/v1.0/<start><br/>"
    "Please enter start and end dates in below api in the format YYYY-MM-DD<br/>"
    "/api/v1.0/<start>/<end>")

#----------------------
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
#----------------------
 
@app.route("/api/v1.0/precipitation")
def precipitation():   
     
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
                   filter(Measurement.date.between('2016-08-01', '2017-08-01')).all()

    precipitation= []
    for result in prcp_results:
        row = {"date":"prcp"}
        row["date"] = result[0]
        row["prcp"] = float(result[1])
        precipitation.append(row)

    return jsonify(precipitation)

#----------------------
# Station route
# Return a json list of stations from the dataset.
#----------------------
@app.route("/api/v1.0/stations")
def stations(): 
     stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc()).all()
    station_List = []
    for s in stations:
        station_List.append({"station":s[0],"name":s[1]})

    return jsonify(station_List)

#----------------------
# Observed temperature route
# Return a json list of Temperature Observations (tobs) for the previous year
#----------------------
@app.route("/api/v1.0/tobs")
def tobs():
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = most_recent[0]
    year_before = last_date.replace(year = (last_date.year - 1))
    year_before = year_before.strftime("%Y-%m-%d")

    tobs = session.query(Station.name,Measurement.date, Measurement.tobs).filter(Measurement.station==Stations.station).filter(Measurement.date>=year_before).order_by(Measurement.date).all()
    tobs_List = []
    for t in tobs:
       tobs_List.append({"station":t[0],"date":t[1],"temperature observation":t[2]})
    
    return jsonify(tobs_List)

#----------------------
# Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
#----------------------
@app.route("/api/v1.0/<start>")
def start(start):

    start_date = datetime.strptime(start, '%Y-%m-%d')
   
    minimum = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    #print(f"Minimum temp: {minimum}")
    average = session.query(func.round(func.avg(Measurement.tobs))).filter(Measurement.date >= start_date).scalar()
    # print(f"Average temp: {average}")
    maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).scalar()
    # print(f"Maximum temp: {maximum}")
    
    result = [{"Minimum":minimum},{"Maximum":maximum},{"Average":average}]
    
    return jsonify(result)

#----------------------
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def StartEnd(start,end):

     start_date = datetime.strptime(start, '%Y-%m-%d')
     end_date = datetime.strptime(end, '%Y-%m-%d')

     minimum = session.query(func.min(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date)).scalar()
     # print(f"Minimum temp: {minimum}")
     average = session.query(func.round(func.avg(Measurement.tobs))).filter(Measurement.date.between(start_date, end_date)).scalar()
     # print(f"Average temp: {average}")
     maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date.between(start_date, end_date)).scalar()
     # print(f"Maximum temp: {maximum}")
        
     result = [{"Minimum":minimum},{"Maximum":maximum},{"Average":average}]
    
     return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)