from base_model import *
from datetime import datetime

class TimeSlot(BaseModel):
    id = AutoField()
    start_at = DateTimeField()
    end_at = DateTimeField()
    tags = []
    note = CharField(null=True)
    created_at = DateTimeField(default=datetime.now())

    def get_difference(self):
        """ returns the time difference between start and end as a tuple (hours, minutes)"""
        diff = self.end_at - self.start_at
        return (diff.seconds//3600, (diff.seconds//60)%60)
    
    def add_tag(self, new_tag):
        self.tags.append(new_tag)

    def remove_tag(self, old_tag):
        self.tags.remove(old_tag)

class Tag(BaseModel):
    id = AutoField()
    time_slot_id = ForeignKeyField(TimeSlot, on_delete="CASCADE")
    tag = CharField()

def init_db():
    db.connect()
    db.create_tables([TimeSlot, Tag])

def close_db():
    db.close()