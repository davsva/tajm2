from peewee import *

db = SqliteDatabase('time_slots.db', pragmas={'foreign_keys': 1})

class BaseModel(Model):
    class Meta:
        database = db
