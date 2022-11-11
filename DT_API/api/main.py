from base64 import urlsafe_b64decode
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import requests
import httpx
import asyncio
import json
import secrets


app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#CHANGE URL HERE IF DT_API IS RUNNING ON A SEPERATE PHYSICAL MACHINE     #
# If multiple different REST APIs for digital twins should be supported, #
# it is better to not use a constant base URI, but fully define them in  #
# the respective places in the methods.                                  #

SMARTROOM_DT_URI = "http://smartroom:8001"


"""Helper Method to perform get requests"""
async def get_request(client, uri_extension):
    response = await client.get(SMARTROOM_DT_URI+uri_extension, timeout=10.0)
    return response

"""Helper Method to perform post requests"""
async def post_request(client, uri_extension, body_data):
    response = await client.post(SMARTROOM_DT_URI+uri_extension, json=body_data, timeout=10.0)
    return response

"""Helper Method to perform delete requests"""
async def delete_request(client, uri_extension):
    response = await client.delete(SMARTROOM_DT_URI+uri_extension, timeout=10.0)
    return response


"""Creates digital twin with the given digital twin type"""
""" Request Body is 1:1 forwarded in the Request"""
@app.post("/DTs/{dt_type}", status_code=status.HTTP_201_CREATED)
async def create_digital_twin(dt_type: str, request: Request):

    digital_twins = read_in_dts()

    id = generate_base64_string(5)

    while id in digital_twins:
        id = generate_base64_string(5)
    

    if dt_type == "smartroom":

        data = await request.json()
        data['room_id'] = id
        url_extension = "/Rooms"

    ## ADD OTHER DT TWIN TYPES HERE AND CREATE THE DATA FOR THE REST REQUEST ##

    
    else:
        raise HTTPException(
                status_code=400, detail=f'No valid DT Type')
        

    async with httpx.AsyncClient() as client:          
        r = await post_request(client, url_extension, data)
        if r.status_code == 201:
            write_dt_to_json(data, dt_type, {})
            return r.json()
        else:
            return r

"""Deletes Digital Twin with the given ID"""
@app.delete("/DTs/{id}")
async def delete_digital_twin(id: str):

    digital_twins = read_in_dts()
    if id in digital_twins:
        twin_to_delete = digital_twins[id]
        twin_type = twin_to_delete['dt_type']

        if twin_type == 'smartroom':
            uri_extension = f'/Rooms/{id}'

            ## ADD OTHER DT TWIN TYPES HERE AND CREATE THE DATA FOR THE REST REQUEST ##

        else:
            raise HTTPException(
            status_code=400, detail=f'No valid DT Type.')
        
        async with httpx.AsyncClient() as client:
            r = await delete_request(client, uri_extension)
            if r.status_code == 200:
                delete_dt_from_json(id)
                return r.json()
            else:
                return r
                
"""Returns all the DTs. Important: Does not query Data from the Database, only the devices.json"""                
@app.get("/DTs", status_code=status.HTTP_200_OK)
async def get_all_dts():
    digital_twins = read_in_dts()
    return digital_twins


"""Returns the DT with the given, if existing. Important: Does not query Data from the Database, only the devices.json"""
@app.get("/DTs/{id}", status_code=status.HTTP_200_OK)
async def get_dt_by_id(id: str):
    digital_twins = read_in_dts()
    if id in digital_twins:
        curr_twin = digital_twins[id]
        return curr_twin
    else:
        raise HTTPException(
            status_code=400, detail=f'ID Not Found.')

"""Adds a device with the given device type to a Digital Twin. """
""" Request Body is 1:1 forwarded in the Request"""
@app.post("/DTs/{dt_id}/devices/{device_type}")
async def post_device_to_dt(dt_id: str, device_type: str, request: Request):
    digital_twins = read_in_dts()

    data = await request.json()

    if dt_id in digital_twins:
        curr_twin = digital_twins[dt_id]

        if curr_twin['dt_type'] == 'smartroom':
            if device_type == 'light':
                uri_extension = f'/Rooms/{dt_id}/Lights'
                device_id = data['light_id']
            elif device_type == 'plug':
                uri_extension = f'/Rooms/{dt_id}/Power_Plugs'
                device_id = data['plug_id']
            elif device_type == 'motion_sensor':
                uri_extension = f'/Rooms/{dt_id}/Motion_Sensors'
                device_id = data['sensor_id']

        ## ADD OTHER DT TWIN TYPES/DEVICES HERE AND CREATE THE DATA FOR THE REST REQUEST ##

            else:
                raise HTTPException(
                status_code=400, detail=f'No valid Device Type')
            

        async with httpx.AsyncClient() as client:          
            r = await post_request(client, uri_extension, data)
            if r.status_code == 201:
                write_device_to_dt(dt_id, device_type, device_id)
                return r.json()
            else:
                return r
    else:
        raise HTTPException(
            status_code=400, detail=f'ID Not Found.')

"""Return devices for a Digital Twin. Important: Does not query Data from the Database, only the devices.json"""
@app.get("/DTs/{dt_id}/devices")
async def get_all_devices_of_dt(dt_id: str):
    digital_twins = read_in_dts()

    if dt_id in digital_twins:
        curr_twin = digital_twins[dt_id]

        return curr_twin['devices']

    else:
        raise HTTPException(
            status_code=400, detail=f'ID Not Found.')

"""Returns a specific device from a Digital Twin. Important: Does not query Data from the Database, only the devices.json"""
@app.get("/DTs/{dt_id}/devices/{device_id}")
async def get_device_from_dt_by_id(dt_id: str, device_id: str):
    digital_twins = read_in_dts()

    if dt_id in digital_twins:
        curr_twin = digital_twins[dt_id]

        if device_id in curr_twin['devices']:
            
            return curr_twin['devices'][device_id]

        else: 
            raise HTTPException(
            status_code=400, detail=f'Device Not Found.')            

    else:
        raise HTTPException(
            status_code=400, detail=f'ID Not Found.')

"""Deletes a specific device from a Digital Twin"""
@app.delete("/DTs/{dt_id}/devices/{device_id}")
async def delete_device_from_dt_by_id(dt_id: str, device_id: str):
    digital_twins = read_in_dts()

    if dt_id in digital_twins:
        curr_twin = digital_twins[dt_id]

        if device_id in curr_twin['devices']:

            device = curr_twin['devices'][device_id]

            if device['device_type'] == 'light':
                uri_extension = f"/Rooms/{dt_id}/Lights/{device_id}"

            elif device['device_type'] == 'plug':
                uri_extension = f"/Rooms/{dt_id}/Power_Plugs/{device_id}"

            elif device['device_type'] == 'motion_sensor':
                uri_extension = f"/Rooms/{dt_id}/Motion_Sensors/{device_id}"

            ##ADD OTHER DEVICE TYPES HERE##
            
            else:
                raise HTTPException(
                status_code=400, detail=f'No valid Device Type')

            async with httpx.AsyncClient() as client:          
                r = await delete_request(client, uri_extension)
                if r.status_code == 200:
                    delete_device_from_json(dt_id, device_id)
                    return r.json()
                else:
                    return r
            
           

        else: 
            raise HTTPException(
            status_code=400, detail=f'Device Not Found.')            

    else:
        raise HTTPException(
        status_code=400, detail=f'ID Not Found.')

"""Returns Operational Parameters for a device of a specific Digital Twin"""
@app.get("/DTs/{dt_id}/devices/{device_id}/GetParameters")
async def get_paramters(dt_id: str, device_id: str, request: Request):
    digital_twins = read_in_dts()

    data = await request.json()

    if dt_id in digital_twins:
        curr_twin = digital_twins[dt_id]

        if device_id in curr_twin['devices']:

            device = curr_twin['devices'][device_id]

            if curr_twin['dt_type'] == "smartroom":

                if device['device_type'] == 'light':
                    uri_extension = f"/Rooms/{dt_id}/Lights/{device_id}/GetOperations"

                elif device['device_type'] == 'plug':
                    uri_extension = f"/Rooms/{dt_id}/Power_Plugs/{device_id}/GetOperations"

                elif device['device_type'] == 'motion_sensor':
                    uri_extension = f"/Rooms/{dt_id}/Motion_Sensors/{device_id}/GetOperations"
                                
                else:
                    raise HTTPException(
                    status_code=400, detail=f'No valid Device Type')

            ##ADD OTHER DT TYPES/DEVICE TYPES HERE##


            async with httpx.AsyncClient() as client:          
                r = await post_request(client, uri_extension, data)
                if r.status_code == 200:
                    return r.json()
                else:
                    return r


        else: 
            raise HTTPException(
            status_code=400, detail=f'Device Not Found.')          


    else:
        raise HTTPException(
        status_code=400, detail=f'ID Not Found.')

"""Executes the given command on the given device in the given Digital Twin"""
@app.post("/DTs/{dt_id}/devices/{device_id}/ExecuteCommand/{command}")
async def execute_command(dt_id: str, device_id: str, command: str):
     digital_twins = read_in_dts()

     if dt_id in digital_twins:
        curr_twin = digital_twins[dt_id]

        if device_id in curr_twin['devices']:
            
            device = curr_twin['devices'][device_id]

            if curr_twin['dt_type'] == "smartroom":

                if command == 'toggle':

                    if device['device_type'] == 'light':
                        uri_extension = f"/Rooms/{dt_id}/Lights/{device_id}/Activation"
                        body = {}

                    elif device['device_type'] == 'plug':
                        uri_extension = f"/Rooms/{dt_id}/Power_Plugs/{device_id}/Activation"
                        body = {}
            
                    else:
                        raise HTTPException(
                        status_code=400, detail=f'No valid Device Type')
                
                ##Other Commands with Elif here


                else:
                    raise HTTPException(
                    status_code=400, detail=f'No valid command')

            ##ADD OTHER DT TYPES HERE

            async with httpx.AsyncClient() as client:          
                r = await post_request(client, uri_extension, body)
                if r.status_code == 200:
                    return r.json()
                else:
                    return r

        else: 
            raise HTTPException(
            status_code=400, detail=f'Device Not Found.')          


     else:
        raise HTTPException(
        status_code=400, detail=f'ID Not Found.')

    




#Helper Methods to interact with the json file#
#Data Management can be changed to SQL#

"""Loads Digital Twins from the JSON file"""
def read_in_dts():
     with open("devices.json", 'r+') as f:
        return json.load(f)

"""Writes Digital Twin to JSON file"""
def write_dt_to_json(dt, type, device_list):
    with open("devices.json", 'r+') as f:
        devices = json.load(f)
    
        new_data = {}
        new_data['dt_type'] = type 
        new_data["devices"] = device_list

        devices[dt['room_id']] = new_data

        f.seek(0)
        
        json.dump(devices, f, indent = 4)

"""Deletes Digital Twins from the JSON file"""
def delete_dt_from_json(dt):
    with open("devices.json", 'r+') as f:
        devices = json.load(f)
        
        f.truncate(0)

        del devices[dt]

        f.seek(0)
        
        json.dump(devices, f, indent = 4)

"""Generates random 5 character base64 string"""
def generate_base64_string(length: int):
    return secrets.token_urlsafe(length)

"""Writes device to JSON file"""
def write_device_to_dt(dt_id, type, device_id):    
    with open("devices.json", 'r+') as f:
        devices = json.load(f)

        new_device = {}
        new_device['device_type'] = type 
        devices[dt_id]['devices'][device_id] = new_device

        f.seek(0)
        json.dump(devices, f, indent = 4)

"""Deletes device from JSON file"""
def delete_device_from_json(dt_id, device_id):
    with open("devices.json", 'r+') as f:
        devices = json.load(f)

        f.truncate(0)

        del devices[dt_id]['devices'][device_id]

        f.seek(0)

        json.dump(devices, f, indent = 4)


        



    


        








            




        





