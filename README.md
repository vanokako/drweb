# Dr. Web test task

API for working with file local storage.

## Methods:

* POST /files/ - upload file to server
* DELETE /files/{ hash }/ - remove file from server
* POST /files/{ hash }/ - download file

## Run alembic migrarion
```commandline
pip install -r requirements.txt
alembic upgrade head
```
