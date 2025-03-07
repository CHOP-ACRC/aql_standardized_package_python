# Package to inititate a new request for PAQS written in Python
Standardized repo for initiating new requests for PAQS queries using Python. 

## Pre-requisites
1. Ensure Python 3 is downloaded to your machine. Our existing packages are compatible with **Python version 3.9 to 3.12.8** Instructions for downloading recent versions of Python can be found at [python.org](python.org).
2. Docker (image for Python pre-installed minimum required libraries and drivers for backend databases. Available on [pcornetqf docker hub](https://hub.docker.com/u/pcornetqf)), development and testing can be performed within a container itself
3. Currently only supports bash for new request and packaging

# Steps to create a new development/testing and packaging environment for PAQS

## Open terminal and clone this repo

```sh
git clone https://github.com/Query-Fulfillment/aql_standardized_package_python.git
```

This local repo should be kept as a standard repo for new requests and should be regularly checked for updates on the remote. 
The `~/shell/new_paqs_request.sh` will allow you to create new requests specific to the query. Follow the instructions below to generate a development environment for a new request.

## cd into the directory where you want to write the code for the new request

```sh
cd path/to/new/request
```

## Execute new_paqs_request.sh

This step will perform the following tasks in order: 

1. Create a new directory with the request_name that is passed in the code below (within the current working directory) 
2. Add base files and code in this directory to perform query development
3. Initiate local git to the newly renamed directory and removes .git from the standard framework code

```sh
path/to/aql_standardized_code_python/shell/new_paqs_request.sh request_name
```
request_name : This string will be the folder name created in the current directory where the subsequent files and folders resides.

### Respond to the required prompts to obtain a new query development environment

### Prompt 1 : Enter request name

This prompt will create a parent folder inside request_name folder where query package code can live. The intention of creating this folder is to have more than one request's code within this directory for easier compartmentalization should the need be.

This step should provide a development environment. Development can be performed on your local machine and tested in a docker container or can be developed within a container itself.

