from flask import Blueprint, request, send_file
from flask_api import status
from flask_httpauth import HTTPBasicAuth

from db_utils import authentication
from filemanager.processors import save_file, delete_from_storage, download_file_from_storage
from filemanager.exceptions import SaveToDataBaseError

auth = HTTPBasicAuth()

filemanager_bp = Blueprint('filemanager', __name__)


@auth.verify_password
def verify_password(username, password):
    return authentication.auth(
        username=username, password=password
    )


@filemanager_bp.route("/", methods=["POST"])
@auth.login_required
def upload_file():
    current_user = auth.current_user()
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return "There are no files", status.HTTP_400_BAD_REQUEST
    try:
        hash_name = save_file(uploaded_file, current_user)
    except SaveToDataBaseError as ex:
        return str(ex), status.HTTP_409_CONFLICT
    return hash_name


@filemanager_bp.route("/<hash_name>/", methods=["DELETE"])
@auth.login_required
def delete_file(hash_name):
    current_user = auth.current_user()
    if not hash_name:
        return "There is no hash", status.HTTP_400_BAD_REQUEST

    try:
        delete_from_storage(hash_name, current_user)
    except FileNotFoundError as ex:
        return str(ex), status.HTTP_404_NOT_FOUND
    return "Success", status.HTTP_200_OK


@filemanager_bp.route("/<hash_name>/", methods=["POST"])
def download_file(hash_name):
    if not hash_name:
        return "There is no hash", status.HTTP_400_BAD_REQUEST

    try:
        path_to_file, file_obj = download_file_from_storage(hash_name)
    except FileNotFoundError as ex:
        return str(ex), status.HTTP_404_NOT_FOUND
    return send_file(
        path_or_file=path_to_file,
        mimetype=file_obj.mimetype,
        as_attachment=True,
        download_name=file_obj.file_name
    )