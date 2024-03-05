import logging, re, calendar
import urllib.parse
from datetime import datetime
from textual import on, events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Header, Footer, Label, Input, Static, Tabs, TextArea, Button, Markdown
from time_slot import *

class ValidYear(Validator):  
    def validate(self, value: str) -> ValidationResult:
        if value.isdigit() and int(value) >= 1 and int(value) <= 9999: 
            return self.success()
        else:
            return self.failure("That's not a valid year")

class ValidMonth(Validator):  
    def validate(self, value: str) -> ValidationResult:
        if value.isdigit() and int(value) >= 1 and int(value) <= 12: 
            return self.success()
        else:
            return self.failure("That's not a valid month")

class ValidDay(Validator):

    def __init__(self, app):
        self.app = app

    def validate(self, value: str) -> ValidationResult:
        max_day = calendar.monthrange(self.app.selected_date.year, self.app.selected_date.month)[1]
        if value.isdigit() and int(value) >= 1 and int(value) <= max_day: 
            return self.success()
        else:
            return self.failure("That's not a valid day within the month")

class ValidHour(Validator):  
    def validate(self, value: str) -> ValidationResult:
        if value.isdigit() and int(value) >= 0 and int(value) <= 23: 
            return self.success()
        else:
            return self.failure("That's not a valid hour")

class ValidMinute(Validator):  
    def validate(self, value: str) -> ValidationResult:
        if value.isdigit() and int(value) >= 0 and int(value) <= 59: 
            return self.success()
        else:
            return self.failure("That's not a valid minute")

class YearInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidYear().validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1)
        elif event.key == "down":
            if ValidYear().validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1)

    def on_blur(self):
        if ValidYear().validate(self.value).is_valid:
            try:
                new_date = self.app.selected_date.replace(year=int(self.value))
                self.app.update_selected_date(new_date)
            except:
                self.app.notify("Invalid date!", severity="error") 

class MonthInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMonth().validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMonth().validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

    def on_blur(self):
        if ValidMonth().validate(self.value).is_valid:
            try:
                new_date = self.app.selected_date.replace(month=int(self.value))
                self.app.update_selected_date(new_date)
            except:
                self.app.notify("Invalid date!", severity="error") 

class DayInput(Input):
    def on_key(self, event: events.Key) -> None:
        max_day = calendar.monthrange(self.app.selected_date.year, self.app.selected_date.month)[1]
        if event.key == "up":
            if ValidDay(self.app).validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidDay(self.app).validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

    def on_blur(self):
        if ValidDay(self.app).validate(self.value).is_valid:
            try:
                new_date = self.app.selected_date.replace(day=int(self.value))
                self.app.update_selected_date(new_date)
            except:
                self.app.notify("Invalid date!", severity="error") 

class HourInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidHour().validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidHour().validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

    def on_blur(self):
        self.app.update_slot_summary()

class MinuteInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinute().validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMinute().validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

    def on_blur(self):
        self.app.update_slot_summary()

class Tajm(App):
    """ A Textual app to manage time slots """

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "layout.tcss"
    AUTO_FOCUS = "#end_time"

    selected_date = datetime.now()

    time_slot = None

    def compose(self) -> ComposeResult:
        logging.debug(f"{self.selected_date.strftime("%Y-%m-%d %H:%M:%S")}")

        """Create child widgets for the app."""
        yield Header()

        with Container(id="app-grid"):
            with Static("One", classes="box", id="date_row"):
                with Horizontal():
                    yield YearInput(id="year", value=f"{self.selected_date.strftime("%Y")}", max_length=4, validators=[ValidYear()], validate_on=["changed"])
                    yield MonthInput(id="month", value=f"{self.selected_date.strftime("%m")}", max_length=2, validators=[ValidMonth()], validate_on=["changed"])
                    yield DayInput(id="day", value=f"{self.selected_date.strftime("%d")}", max_length=2, validators=[ValidDay(self)], validate_on=["changed"])
                    yield Label(id="week")

            with Static("Two", classes="box"):
                with Horizontal():
                    yield HourInput(id="t1h", value=f"{self.selected_date.strftime("%H")}", max_length=2, validators=[ValidHour()], validate_on=["changed"])
                    yield MinuteInput(id="t1m", value=f"{self.selected_date.strftime("%M")}", max_length=2, validators=[ValidMinute()], validate_on=["changed"])
                    yield Label("to")
                    yield HourInput(id="t2h", value=f"{self.selected_date.strftime("%H")}", max_length=2, validators=[ValidHour()], validate_on=["changed"])
                    yield MinuteInput(id="t2m", value=f"{self.selected_date.strftime("%M")}", max_length=2, validators=[ValidMinute()], validate_on=["changed"])
                    yield Label(id="slot_summary")
                with Vertical():    
                    yield Input(id="new_tag", placeholder="Tag...[ENTER]", max_length=25)
                    yield Markdown(id="tags")
                with Vertical():    
                    yield TextArea(id="notes")
                with Horizontal():    
                    yield Button.success(":floppy_disk:", id="save")
                    yield Button.error(":wastebasket:", disabled=True)
            with Static("Three", classes="box"):
                yield Tabs("Day", "Week", "Month", "Year")
                yield Label(id="sselected")

        yield Footer()

    def update_selected_date(self, new_date):
        self.selected_date = new_date
        week_label = self.query_one("#week")
        week_label.update(f"{self.selected_date.strftime('%Y-%m-%d')} Week# {self.selected_date.isocalendar().week}")

    def update_slot_summary(self):
        """ start time """
        t1 = self.selected_date.replace(hour=int(self.app.query_one("#t1h").value), minute=int(self.app.query_one("#t1m").value))
        """ end time """
        t2 = self.selected_date.replace(hour=int(self.app.query_one("#t2h").value), minute=int(self.app.query_one("#t2m").value))
        self.time_slot = TimeSlot()
        self.time_slot.start_at = t1
        self.time_slot.end_at = t2
        slot_summary_label = self.query_one("#slot_summary")
        slot_summary_label.update(f"{str(self.time_slot.get_difference()[0]).zfill(1)}h {str(self.time_slot.get_difference()[1]).zfill(2)}m")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_mount(self):
        self.update_selected_date(datetime.now())
        self.update_slot_summary()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs."""
        label = self.query_one("#sselected")
        if event.tab is None:
            # When the tabs are cleared, event.tab will be None
            label.visible = False
        else:
            label.visible = True
            label.update(self.selected_date.strftime("%Y-%m-%d"))

    def action_clear(self) -> None:
        """Clear the tabs."""
        self.query_one("#sselected").clear()

    def update_tags(self):
            tags = self.query_one("#tags")
            tags_content = ""
            for tag in self.time_slot.tags:
                href_tag = f"remove_{tag}"
                href_tag = urllib.parse.quote(href_tag)
                tags_content += tag + f" [❌]({href_tag}) "
            tags.update(tags_content)

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        if event.validation_result != None and not event.validation_result.is_valid:
            self.notify(event.validation_result.failure_descriptions[0], severity="error")  

    @on(Input.Submitted)
    def show_invalid_reasons(self, event: Input.Submitted) -> None:
        if event.input.id == "new_tag":
            self.time_slot.add_tag(event.value)
            self.update_tags() 
            """ then clear the event.input """
            event.input.clear()

    @on(Markdown.LinkClicked)
    def check_link(self, markdown) -> None:
        if markdown.href.startswith("remove_"): 
            tag = urllib.parse.unquote(markdown.href[7:])
            self.time_slot.remove_tag(tag)
            self.update_tags()

    @on(Button.Pressed)
    def button_clicked(self, pressed) -> None:
        if pressed.button.id == "save":
            """ here the user's intent is to save the time slot """
            notes = self.query_one("#notes")
            self.time_slot.note = notes.text
            self.time_slot.save()

if __name__ == "__main__":
    logging.basicConfig(filename='tajm.log', encoding='utf-8', level=logging.DEBUG)
    logging.debug("Spinning up")
    init_db()
    app = Tajm()
    app.run()
    close_db()