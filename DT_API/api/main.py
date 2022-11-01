from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from config import settings
import requests
import httpx
import asyncio
import json






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
    return response.json


async def post_request(client, uri_extension, body_data):
    response = await client.post(SMARTROOM_DT_URI+uri_extension, json=body_data)
    return response.json


@app.post("/DTs/{dt_type}", status_code=status.HTTP_201_CREATED)
async def create_digital_twin(dt_type: str, request: Request):

    digital_twins = read_in_dts()

    id = len(digital_twins)+1

    if dt_type == "smartroom":

        data = request.json()
        data['room_id'] = id

        async with httpx.AsyncClient() as client:          
            r = await post_request(client, "/Rooms", await request.json())
            r.raise_for_status()




def read_in_dts():
     with open("devices.json", 'r+') as f:
        return json.load(f)

        

        








            




        





