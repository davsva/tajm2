class TimeSlot:

    def __init__(self, start_at, end_at):
        self.id = None
        self.start_at = start_at
        self.end_at = end_at
        self.tags = []
        self.note = None
        self.created_at = None

    def get_difference(self):
        """ returns the time difference between start and end as a tuple (hours, minutes)"""
        diff = self.end_at - self.start_at
        return (diff.seconds//3600, (diff.seconds//60)%60)
    
    def add_tag(self, new_tag):
        self.tags.append(new_tag)

    def remove_tag(self, old_tag):
        self.tags.remove(old_tag)
