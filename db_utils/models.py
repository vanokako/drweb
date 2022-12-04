import hashlib
import pathlib
import os

from flask import request
from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, event, UniqueConstraint
)

from db_utils.database import Base


def create_hash(context):
    name = context.get_current_parameters()["file_name"]
    hash_name = hashlib.md5(name.encode())
    return hash_name.hexdigest()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Files(Base):
    __tablename__ = 'files'
    __table_args__ = (
        UniqueConstraint('file_name', 'hash_name'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    hash_name = Column(
        String,
        nullable=False,
        onupdate=create_hash
    )
    mimetype = Column(String, nullable=False)
    extension = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    @property
    def file_dir(self) -> str:
        file_directory = os.getenv("UPLOAD_FOLDER", "./store")
        hash_preffix = self.hash_name[:2]
        path_dir = f"{file_directory}/{hash_preffix}/"
        return path_dir


@event.listens_for(Files, 'after_insert')
def save_file_to_dir(mapper, connection, target):
    uploaded_file = request.files.get('file')
    pathlib.Path(target.file_dir).mkdir(parents=True, exist_ok=True)
    uploaded_file.save(pathlib.Path(f"{target.file_dir}/{target.hash_name}"))


@event.listens_for(Files, 'before_delete')
def delete_file_from_dir(mapper, connection, target):
    path = pathlib.Path(target.file_dir)
    path_to_file = path / target.hash_name
    path_to_file.unlink()
    if not any(path.iterdir()):
        path.rmdir()
