from pydantic import BaseModel
from sqlite3 import Timestamp

#room,raspi,robot

class DigitalTwin_Model(BaseModel):
    dt_id:str 
    dt_type:str
    dt_name:str
    class Config:
        orm_mode=True

class Room_Object(BaseModel):
    room_id: str
    room_size:int
    measurement_unit:str
  
    class Config:
        orm_mode = True

class Update_RoomObject(BaseModel):
    room_size:int
    measurement_unit:str
  
    class Config:
        orm_mode = True

class AirQuality_Properties_Object(BaseModel):
    room_id: str
    device_id:str
    ventilator:str
    co2:float
    co2measurementunit:str
    temperature:float
    temperaturemeasurementunit:str
    humidity:float
    humiditymeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True

class AirQuality_Temperature_Object(BaseModel):
    room_id: str
    ventilator:str
    temperature:int
    temperaturemeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True

class AirQuality_Humidity_Object(BaseModel):
    room_id: str
    ventilator:str
    humidity:int
    humiditymeasurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True     

class AirQuality_Co2_Object(BaseModel):
    room_id: str
    ventilator:str
    co2:int
    co2measurementunit:str
    time:Timestamp
    
    class Config:
        orm_mode = True             

