#!/bin/bash

# Create a virtual environment
python3 -m venv paqs-query-python-env

# Activate the virtual environment
source paqs-query-python-env/bin/activate

# Install the required Python packages
pip install -r requirements.txt

# Inform the user that the setup is complete
echo "Virtual environment setup and dependencies installed successfully."

