# Generic DT API

## Requirements
- The repository needs to be cloned to the desired server host.
- The host needs to have [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed. 


## Installation
On first startup a ```devices.json``` with an empty JSON Object ```{}``` needs to be created in the [```DT_API\api```](./api) folder. To start the application open the ```DT_API``` folder and start the docker composition with the command ```docker compose up```.

## Functionality
The API stores digital twins and devices in the ```devices.json``` file. For each digital twin type the API performs REST request to the respective APIs to create DTs and devices as well as interact with those. The application currently supports the [smartroom digital twin API](https://github.com/cdl-mint/smartroom-usecase). However, the generic API is designed to be extended easily. The spots where the functionality can be extended are marked in the [```main.py```](./api/main.py) file. 
To view an Open API documentation of the REST endpoints available go into a browser and request the ```\docs``` ressource.


