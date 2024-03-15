""" module that holds custom Inputs """

from textual.widgets import Input
from textual import events

try:
    from custom_validators import ValidMinMax, ValidDay
except ImportError:
    from .custom_validators import ValidMinMax, ValidDay

try:
    from constants import Constants
except ImportError:
    from .constants import Constants


class YearInput(Input):
    """the YearInput with up and down key bindings"""

    def on_key(self, event: events.Key) -> None:
        """called when a key is pressed"""
        if event.key == "up":
            if (
                ValidMinMax(Constants.YEAR_MIN, Constants.YEAR_MAX, "year")
                .validate(str(int(self.value) + 1))
                .is_valid
            ):
                self.value = str(int(self.value) + 1)
        elif event.key == "down":
            if (
                ValidMinMax(Constants.YEAR_MIN, Constants.YEAR_MAX, "year")
                .validate(str(int(self.value) - 1))
                .is_valid
            ):
                self.value = str(int(self.value) - 1)


class MonthInput(Input):
    """the MonthInput with up and down key bindings"""

    def on_key(self, event: events.Key) -> None:
        """called when a key is pressed"""
        if event.key == "up":
            if (
                ValidMinMax(Constants.MONTH_MIN, Constants.MONTH_MAX, "month")
                .validate(str(int(self.value) + 1))
                .is_valid
            ):
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if (
                ValidMinMax(Constants.MONTH_MIN, Constants.MONTH_MAX, "month")
                .validate(str(int(self.value) - 1))
                .is_valid
            ):
                self.value = str(int(self.value) - 1).zfill(2)


class DayInput(Input):
    """the DayInput with up and down key bindings"""

    def on_key(self, event: events.Key) -> None:
        """called when a key is pressed"""
        if event.key == "up":
            if ValidDay(self.app).validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidDay(self.app).validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)


class HourInput(Input):
    """the HourInput with up and down key bindings"""

    def on_key(self, event: events.Key) -> None:
        """called when a key is pressed"""
        if event.key == "up":
            if (
                ValidMinMax(Constants.HOUR_MIN, Constants.HOUR_MAX, "hour")
                .validate(str(int(self.value) + 1))
                .is_valid
            ):
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if (
                ValidMinMax(Constants.HOUR_MIN, Constants.HOUR_MAX, "hour")
                .validate(str(int(self.value) - 1))
                .is_valid
            ):
                self.value = str(int(self.value) - 1).zfill(2)


class MinuteInput(Input):
    """the MinuteInput with up and down key bindings"""

    def on_key(self, event: events.Key) -> None:
        """called when a key is pressed"""
        if event.key == "up":
            if (
                ValidMinMax(Constants.MINUTE_MIN, Constants.MINUTE_MAX, "minute")
                .validate(str(int(self.value) + 1))
                .is_valid
            ):
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if (
                ValidMinMax(Constants.MINUTE_MIN, Constants.MINUTE_MAX, "minute")
                .validate(str(int(self.value) - 1))
                .is_valid
            ):
                self.value = str(int(self.value) - 1).zfill(2)
