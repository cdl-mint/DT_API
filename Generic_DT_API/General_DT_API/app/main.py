"""Module fastapi for creating RESTAPI in python."""
from fastapi import FastAPI, status
from model import DigitalTwin_Model, Room_Object
from session import settings
import requests
import uvicorn
tags_metadata = [
    {
         "name": "Digital Twins",
         "description": "Generic API to access use-cases based on digital-twin",
    },
]
app=FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION, openapi_tags=tags_metadata)

AQURL = 'http://localhost:8001/'
ROBOTURL = 'http://localhost:8000'
SMARTROOMURL = 'https://airquality.se.jku.at/smartroomairquality-test/'

@app.post("/DT/Create/",status_code=201, tags=["Digital Twins"])
def create_digital_twin(request_body:DigitalTwin_Model):
    """create digital twin like Rooms"""
    data={}
    data['dt_id']=request_body.dt_id
    data['dt_type']=request_body.dt_type
    data['dt_name']=request_body.dt_name
    print(data)
    print(request_body)
    url=AQURL+'DigitalTwin'
    headers = {"Content-Type": "application/json"}
    response=requests.post(url,json=data,headers=headers,timeout=None)
    if response.status_code == 201:
        return {'Digital Twin is created successfully'}
    elif response.status_code != 201:
        return {"error": "Failed to post data to the URL."}

@app.post("/DT/Add_Details/{dt_type}",status_code=201, tags=["Digital Twins"])
def add_digital_twin_details(dt_type:str,request:Room_Object):
 """add details to twin - eg.room details"""
 if len(dt_type)!=0:
  if dt_type=='Rooms':
   data={}
   data['dt_id']=request.room_id
   data['room_size']=request.room_size
   data['measurement_unit']=request.measurement_unit
   print(data)
   url=AQURL+dt_type
   headers = {"Content-Type":"application/json"}
   response=requests.post(url,json=data,headers=headers,timeout=None)
   if response.status_code == 201:
    return {'Digital Twin details are added successfully'}
   else:
    return {"error": "Failed to post data to the URL."}
  else:
      return {'dt_type'+{dt_type}+'is mismatched'}
@app.get("/DT/{dt_type}",tags=["Digital Twins"], status_code=status.HTTP_200_OK)
def get_all_twin(dt_type:str):
    """get digital twin based on dt_type"""
    if len(dt_type)!=0:
        url=SMARTROOMURL+dt_type
        print(url)
        response=requests.get(url,timeout=None)
        print(response.json())
    return response.json()

@app.get("/DT/{dt_type}/{dt_id}",tags=["Digital Twins"], status_code=status.HTTP_200_OK)
def get_specific_twin(dt_type:str,dt_id:str):
    """get specific digital twin with dt_type and dt_id"""
    if (len(dt_type)!=0 and len(dt_id)!=0):
        url=SMARTROOMURL+dt_type+'/'+dt_id
        print(url)
        response=requests.get(url,timeout=None)
    return response.json()
@app.post("/DT/{dt_type}/{dt_id}/{use_case}/{command}",status_code=status.HTTP_200_OK, tags=["Digital Twins"])
def execute_commands_on_usecase(use_case:str,command:str,dt_type:str,dt_id:str):
    """execute commands on use cases"""
    if(len(use_case)!=0 and  len(dt_type)!=0 and len(command)!=0 and len(dt_id)!=0):
        if use_case=='AirQuality':
            url=SMARTROOMURL+dt_type+'/'+dt_id+'/'+use_case+'/'
            print(url)
            response=requests.get(url,timeout=None)
            return response.json()
        elif use_case=='SmartRoom':
            url=SMARTROOMURL+dt_type+'/'+dt_id+'/'+'Ventilators/SmartPlug1/Activation'
            print(url)
            response=requests.post(url,timeout=None)
            return {'Ventilator is operated successfully'}
        else:
            url=ROBOTURL+'/Robots/Gripper'
            print(url)
            response=requests.post(url,timeout=None)
            return {'Robot is operated successfully'}
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")