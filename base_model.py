""" module that holds the base database configuration """

from peewee import Model, SqliteDatabase

db = SqliteDatabase("time_slots.db", pragmas={"foreign_keys": 1})


class BaseModel(Model):
    """a BaseModel for all Models in our app making use of the same SQLite database"""

    class Meta:
        """the Meta class"""

        database = db
