import calendar
from textual.widgets import Input
from textual import events
from custom_validators import ValidMinMax, ValidDay
from constants import *

class YearInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinMax(Constants.YEAR_MIN, Constants.YEAR_MAX, "year").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1)
        elif event.key == "down":
            if ValidMinMax(Constants.YEAR_MIN, Constants.YEAR_MAX, "year").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1)

class MonthInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinMax(Constants.MONTH_MIN, Constants.MONTH_MAX, "month").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMinMax(Constants.MONTH_MIN, Constants.MONTH_MAX, "month").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

class DayInput(Input):
    def on_key(self, event: events.Key) -> None:
        max_day = calendar.monthrange(self.app.selected_date.year, self.app.selected_date.month)[1]
        if event.key == "up":
            if ValidDay(self.app).validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidDay(self.app).validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

class HourInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinMax(Constants.HOUR_MIN, Constants.HOUR_MAX, "hour").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMinMax(Constants.HOUR_MIN, Constants.HOUR_MAX, "hour").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

class MinuteInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinMax(Constants.MINUTE_MIN, Constants.MINUTE_MAX, "minute").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMinMax(Constants.MINUTE_MIN, Constants.MINUTE_MAX, "minute").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)
