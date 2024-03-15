""" the time_slot module defines the database model using peewee ORM """

from datetime import datetime
from peewee import (
    DateTimeField,
    CharField,
    ForeignKeyField,
    CompositeKey,
)

try:
    from base_model import BaseModel, db
except ImportError:
    from .base_model import BaseModel, db


class TimeSlot(BaseModel):
    """defines the TimeSlot"""

    start_at = DateTimeField()
    end_at = DateTimeField()
    note = CharField(null=True)
    created_at = DateTimeField(default=datetime.now())

    def get_difference(self):
        """returns the time difference between start and end as a tuple (hours, minutes)"""
        diff = self.end_at - self.start_at
        return (
            diff.seconds // 3600,  # pylint: disable=E1101
            (diff.seconds // 60) % 60,  # pylint: disable=E1101
        )

    def __str__(self):
        return f"start_at={self.start_at} end_at={self.end_at} note={self.note}"


class Tag(BaseModel):
    """defines the Tag"""

    tag = CharField(primary_key=True)


class TimeSlotTag(BaseModel):
    """defines the TimeSlotTag"""

    timeslot = ForeignKeyField(TimeSlot)
    tag = ForeignKeyField(Tag)

    class Meta:
        """defines the Meta"""

        primary_key = CompositeKey("timeslot", "tag")


def init_db():
    """initializes the db"""
    db.connect()
    db.create_tables([TimeSlot, Tag, TimeSlotTag])


def close_db():
    """closes the db connection"""
    db.close()
