@echo off
py -m venv paqs-query-python-env

call paqs-query-python-env\Scripts\activate

pip install -r requirements.txt

echo Virtual environment setup and dependencies installed successfully.
pause
