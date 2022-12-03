from sqlalchemy import and_
from sqlalchemy import exc

from db_utils import database, models


def auth(username, password):
    with database.SessionLocal() as db:
        try:
            user = db.query(models.Users).where(
                and_(
                    models.Users.username == username,
                    models.Users.password == password
                )
            ).one()
            return user
        except exc.NoResultFound:
            return None
