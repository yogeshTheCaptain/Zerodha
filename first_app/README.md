## Create a conda/virtual enviroment
```
conda create -n zerodha_first_app python=3.13
```

## Python Check
```
conda activate zerodha_first_app

python --version

Python 3.13.5

conda deactivate
```

## Install Requirements
```
pip install -r requirements.txt
```

## Create Zerodha Config File Inside first_app folder
```
filename = "zerodha_config.py"


email = "abc@gmail.com"
password = "password"

user_id = "client_id/phone_number"

api_key = "kite_api_key"
api_secret = "kite_api_secret"

totp_key = "totp_secret_key"

```

## Run Python File
```
python -m code_files.automated_login   

python -m code_files.process_data       
```

