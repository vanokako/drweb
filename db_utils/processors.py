import hashlib

from flask import request


def create_hash():
    # Do not send file as parameter because
    # this function is used as on_update function
    uploaded_file = request.files.get('file')
    hash_name = hashlib.md5(uploaded_file.read()).hexdigest()
    uploaded_file.seek(0)
    return hash_name
