from base_model import *
from datetime import datetime

class TimeSlot(BaseModel):
    start_at = DateTimeField()
    end_at = DateTimeField()
    note = CharField(null=True)
    created_at = DateTimeField(default=datetime.now())

    def get_difference(self):
        """ returns the time difference between start and end as a tuple (hours, minutes)"""
        diff = self.end_at - self.start_at
        return (diff.seconds//3600, (diff.seconds//60)%60)
    
class Tag(BaseModel):
    tag = CharField(primary_key=True)

class TimeSlotTag(BaseModel):
    timeslot = ForeignKeyField(TimeSlot)
    tag = ForeignKeyField(Tag)

    class Meta:
        primary_key = CompositeKey('timeslot', 'tag')

def init_db():
    db.connect()
    db.create_tables([TimeSlot, Tag, TimeSlotTag])

def close_db():
    db.close()