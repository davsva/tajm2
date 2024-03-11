import calendar
from textual.validation import ValidationResult, Validator

class ValidMinMax(Validator):

    def __init__(self, min, max, entity):
        self.min = min
        self.max = max
        self.entity = entity
  
    def validate(self, value: str) -> ValidationResult:
        if value.isdigit() and int(value) >= self.min and int(value) <= self.max: 
            return self.success()
        else:
            return self.failure(f"That's not a valid {self.entity}")

class ValidDay(Validator):

    def __init__(self, app):
        self.app = app

    def validate(self, value: str) -> ValidationResult:
        max_day = calendar.monthrange(self.app.selected_date.year, self.app.selected_date.month)[1]
        if value.isdigit() and int(value) >= 1 and int(value) <= max_day: 
            return self.success()
        else:
            return self.failure("That's not a valid day within the month")
