from fastapi import FastAPI
import pandas as pd
from sqlalchemy import create_engine,text
from dtos import SensorDTO, SecurityEvent, DeleteSensor

app=FastAPI()

engine = create_engine(
    "mysql+pymysql://dashboard:Nishtha123@localhost/SENSORS"
)

@app.get("/sensors")
def get_sensors():
    query="""
    SELECT *
    FROM smart_home_iot_dataset
    LIMIT 50;

    """

    df=pd.read_sql(query,engine)

    return df.to_dict(orient="records")

@app.get("/maintenance")
def get_maintenance(limit: int=100,offset:int=0):
    print("API called")
    query= f"""SELECT DISTINCT device_id,
    room,
    device_type,maintenance_due_flag FROM smart_home_iot_dataset
    WHERE maintenance_due_flag=1 LIMIT {limit} OFFSET {offset}"""

    print("Running SQL...")

    df=pd.read_sql(query,engine)

    return {
        "limit": limit,
        "offset": offset,
        "count": len(df),
        "data": df.to_dict(orient="records")
    }

@app.get("/devices")
def get_devices():
    query= """SELECT DISTINCT
    device_id,
    room,
    device_type,
    manufacturer,
    model
    FROM smart_home_iot_dataset;  """

    df=pd.read_sql(query,engine)

    return  df.to_dict(orient="records")
    


@app.get("/room_stats")
def get_stats():
    query=""" SELECT 
    room, AVG(temperature_c), AVG(humidity_pct), AVG(power_consumption_w)
    FROM smart_home_iot_dataset
    GROUP BY room; """
 
    df=pd.read_sql(query,engine)

    return  df.to_dict(orient="records")

@app.get("/failure_risk")
def risky():
    query="""
    SELECT DISTINCT
    device_id, device_type,room,
    failure_within_7days
    FROM smart_home_iot_dataset
    WHERE failure_within_7days=1;
    """

    df=pd.read_sql(query,engine)

    return  df.to_dict(orient="records")

@app.get("/low_battery")
def low_battery():
    query="""
    SELECT device_id,battery_level_pct 
    from smart_home_iot_dataset
    WHERE battery_level_pct<20;
"""

    df=pd.read_sql(query,engine)

    return  df.to_dict(orient="records")

@app.get("/avg_battery_manufacturer")
def avg_battery():
    query="""
    SELECT
    manufacturer,
    AVG(battery_level_pct)
    FROM smart_home_iot_dataset
    GROUP BY manufacturer;
"""

    df=pd.read_sql(query,engine)

    return  df.to_dict(orient="records")

@app.post("/new_reading")
def add_reading(sensor:SensorDTO):
    query=text("""
        INSERT INTO smart_home_iot_dataset
        (
            timestamp,
            device_id,
            device_type,
            household_id,
            room,
            manufacturer,
            model,
            firmware_version,
            protocol,
            battery_level_pct,
            temperature_c,
            humidity_pct,
            power_consumption_w,
            maintenance_due_flag

        )
        VALUES
        (
            :timestamp,
            :device_id,
            :device_type,
            :household_id,
            :room,
            :manufacturer,
            :model,
            :firmware_version,
            :protocol,
            :battery_level_pct,
            :temperature_c,
            :humidity_pct,
            :power_consumption_w,
            :maintenance_due_flag
               
        )
               """)
    
    with engine.begin() as conn:
        conn.execute(query,sensor.model_dump())

    return {
        "message": "Sensor reading added successfully",
        "sensor": sensor
    }




@app.post("/security")
def add_security_event(event: SecurityEvent):

    query = text("""
        INSERT INTO security_logs
        (device_id, event_type, description_, severity)
        VALUES
        (:device_id, :event_type, :description, :severity)
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "device_id": event.device_id,
            "event_type": event.event_type,
            "description": event.description,
            "severity": event.severity
        })

    return {"message": "Security event logged successfully"}





## delete old sensor data
# @app.delete("old_data")
# def delete_oldData(data: )


