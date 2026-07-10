from pydantic import BaseModel

class SensorDTO(BaseModel):
    timestamp: str
    device_id:str
    device_type:str
    household_id:str
    room: str
    manufacturer:str
    model:str
    firmware_version:str
    protocol:str
    battery_level_pct:float
    temperature_c:float
    humidity_pct:float
    power_consumption_w:float
    maintenance_due_flag:int 

    
class SecurityEvent(BaseModel):
    device_id: str
    event_type: str
    description: str
    severity: str

class DeleteSensor(BaseModel):
    device_id:str