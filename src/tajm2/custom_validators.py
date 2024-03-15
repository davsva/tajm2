""" the module holds all custom validators """

import calendar
from textual.validation import ValidationResult, Validator


class ValidMinMax(Validator):
    """Validates that a value is between a min and a max value"""

    def __init__(self, valid_min, valid_max, entity):
        super().__init__()
        self.min = valid_min
        self.max = valid_max
        self.entity = entity

    def validate(self, value: str) -> ValidationResult:
        if value.isdigit() and int(value) >= self.min and int(value) <= self.max:
            return self.success()
        else:
            return self.failure(f"That's not a valid {self.entity}")


class ValidDay(Validator):
    """Validates that a value is between the first and last day given the app's
    selected_date year and month"""

    def __init__(self, app):
        super().__init__()
        self.app = app

    def validate(self, value: str) -> ValidationResult:
        max_day = calendar.monthrange(
            self.app.selected_date.year, self.app.selected_date.month
        )[1]
        if value.isdigit() and int(value) >= 1 and int(value) <= max_day:
            return self.success()
        else:
            return self.failure("That's not a valid day within the month")
