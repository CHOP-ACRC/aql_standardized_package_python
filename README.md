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
2. Add base files and code in this directory to perform query development. The query-specific files (ie. code, specs, etc.) will be placed within the request_name directory in a folder of the same name used for request_name. This folder name (defaults to new-paqs-request if no request_name is provided) is the string that should be passed into the prompt for creating the package. 
3. Initiate local git to the newly renamed directory and removes .git from the standard framework code

```sh
path/to/aql_standardized_package_python/shell/new_paqs_request.sh request_name
```
request_name : This string will be the folder name created in the current directory where the subsequent files and folders resides.

## Edit query.py with query-specific code

Edit the code/query.py script for the particular query. An example script has been provided. Add additional packages to the requirements.txt file as needed and include relevant codesets in the specs/ folder. 

## Packaging

Packaging a query for testing and distribution involves two steps.

#### Step 1 : Preparing a workplan

Workplan development is a semi-automated process. Navigate to request_info.qmd file in R-studio. R-code chunks have been automated to obtain information from your query package by default. However, the chunk following output files should be edited to reflect the directory from a sample test run to populated the expected results files.

The query package name will be reflective of the input name chosen when running build_package.sh; if you'd like to change the query package name, edit the `params$query_name` in the first R-code chunk. Edit the Request summary free-text and Execution Process sections of the workplan to reflect your query.

**Note that workplan cannot be rendered from R-studio. It's a part of an automated pakaging script. See Step 2 below.**

#### Step 2 : Developing a query package

Packaging is an automated process which can be executed by running following the line in your top-level directory.

```bash
shell/build_package.sh
```

The script will generated a prompt to enter the name of the folder where the query code lives. The script will also require the workplan to be edited and prepared as the workplan is a part of the packaging script.

## Note
This package does not currently have the correct code inplace for the native programming language version of the package. Testing the native programming code will not work since the logic has not been added for that yet. 