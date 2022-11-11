# Generic DT API

## Requirements
- The repository needs to be cloned to the desired server host.
- The host needs to have [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed. 


## Installation
On first startup a ```devices.json``` with an empty JSON Object ```{}``` needs to be created in the ```DT_API\api``` folder. To start the application open the ```DT_API``` folder and start the docker composition with the command ```docker compose up```.

## Functionality
The API stores digital twins and devices in the ```devices.json``` file. For each digital twin type the API performs REST request to the respective APIs to create DTs and devices as well as interact with those. 
The spots where the functionality can be extended are marked in the ```main.py``` file. 

