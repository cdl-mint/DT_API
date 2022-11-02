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

#CHANGE URL HERE IF DT_API IS RUNNING ON A SEPERATE PHYSICAL MACHINE#
SMARTROOM_DT_URI = "http://smartroom:8001"


async def get_request(client, uri_extension):
    response = await client.get(SMARTROOM_DT_URI+uri_extension)
    return response


async def post_request(client, uri_extension, body_data):
    response = await client.post(SMARTROOM_DT_URI+uri_extension, json=body_data)
    return response

async def delete_request(client, uri_extension):
    response = await client.delete(SMARTROOM_DT_URI+uri_extension)
    return response


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
        

    async with httpx.AsyncClient() as client:          
        r = await post_request(client, url_extension, data)
        if r.status_code == 201:
            write_dt_to_json(data, dt_type, [])
            return r.json()
        else:
            return r


@app.delete("/DTs/{id}")
async def delete_digital_twin(id: str):

    digital_twins = read_in_dts()
    if id in digital_twins:
        twin_to_delete = digital_twins[id]
        twin_type = twin_to_delete['dt_type']

        if twin_type == 'smartroom':
            uri_extension = f'/Rooms/{id}'
        
        async with httpx.AsyncClient() as client:
            r = await delete_request(client, uri_extension)
            if r.status_code == 200:
                delete_dt_from_json(id)
                return r.json()
            else:
                return r
                
@app.get("/DTs", status_code=status.HTTP_200_OK)
async def get_all_dts():
    digital_twins = read_in_dts()
    return digital_twins

@app.get("/DTs/{id}", status_code=status.HTTP_200_OK)
async def get_dt_by_id(id: str):
    digital_twins = read_in_dts()
    if id in digital_twins:
        curr_twin = digital_twins[id]
        return curr_twin
    else:
        raise HTTPException(
            status_code=400, detail=f'ID Not Found.')



#Helper Methods#


def read_in_dts():
     with open("devices.json", 'r+') as f:
        return json.load(f)

def write_dt_to_json(dt, type, device_list):
    with open("devices.json", 'r+') as f:
        devices = json.load(f)
    
        new_data = {}
        new_data['dt_type'] = type 
        new_data["devices"] = device_list

        devices[dt['room_id']] = new_data

        f.seek(0)
        
        json.dump(devices, f, indent = 4)

def delete_dt_from_json(dt):
    with open("devices.json", 'r+') as f:
        devices = json.load(f)
        
        f.truncate(0)

        del devices[dt]

        f.seek(0)
        
        json.dump(devices, f, indent = 4)

def generate_base64_string(length: int):
    return secrets.token_urlsafe(length)


        








            




        





