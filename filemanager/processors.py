import pathlib
from sqlalchemy import exc, and_
import hashlib

from db_utils import database, models
from filemanager.exceptions import SaveToDataBaseError


def remove_file(file: models.Files):
    file_path = f"{file.file_dir}{file.hash_name}"
    rem_file = pathlib.Path(file_path)
    rem_file.unlink()


def save_file(uploaded_file, user):
    hash_name = hashlib.md5(uploaded_file.filename.encode()).hexdigest()

    file_model = models.Files(
        file_name=uploaded_file.filename,
        mimetype=uploaded_file.content_type,
        extension=pathlib.Path(uploaded_file.filename).suffix,
        hash_name=hash_name,
        user_id=user.id
    )

    with database.SessionLocal() as db:
        try:
            db.add(file_model)
            db.commit()
        except exc.IntegrityError as ex:
            raise SaveToDataBaseError(ex)

    return hash_name


def delete_from_storage(hash_name: str, user):
    with database.SessionLocal() as db:
        obj = db.query(models.Files).filter(
            and_(
                models.Files.hash_name == hash_name,
                models.Files.user_id == user.id,
            )
        ).first()
        if not obj:
            raise FileNotFoundError("File Not Found")
        db.delete(obj)
        db.commit()


def download_file_from_storage(hash_name):
    with database.SessionLocal() as db:
        obj = db.query(models.Files).filter(
            models.Files.hash_name == hash_name
        ).first()
    if not obj:
        raise FileNotFoundError("File Not Found")
    path_to_file = pathlib.Path(
        f"{obj.file_dir}/{hash_name}"
    )
    return path_to_file, obj
