import logging, calendar
import urllib.parse
from datetime import datetime, timedelta
from textual import on, events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.validation import ValidationResult, Validator
from textual.widgets import Header, Footer, Label, Input, Static, Tabs, Tab, TextArea, Button, Markdown, DataTable
from textual.suggester import Suggester
from rich.text import Text
from time_slot import *

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

class YearInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinMax(1, 9999, "year").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1)
        elif event.key == "down":
            if ValidMinMax(1, 9999, "year").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1)

    def on_blur(self):
        if ValidMinMax(1, 9999, "year").validate(self.value).is_valid:
            try:
                new_date = self.app.selected_date.replace(year=int(self.value))
                self.app.update_selected_date(new_date)
            except:
                self.app.notify("Invalid date!", severity="error") 

class MonthInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinMax(1, 12, "month").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMinMax(1, 12, "month").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

    def on_blur(self):
        if ValidMinMax(1, 12, "month").validate(self.value).is_valid:
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
            if ValidMinMax(0, 23, "hour").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMinMax(0, 23, "hour").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

    def on_blur(self):
        self.app.update_slot_summary()

class MinuteInput(Input):
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            if ValidMinMax(0, 59, "minute").validate(str(int(self.value) + 1)).is_valid:
                self.value = str(int(self.value) + 1).zfill(2)
        elif event.key == "down":
            if ValidMinMax(0, 59, "minute").validate(str(int(self.value) - 1)).is_valid:
                self.value = str(int(self.value) - 1).zfill(2)

    def on_blur(self):
        self.app.update_slot_summary()

class TagSuggester(Suggester):
    async def get_suggestion(self, value):
        if len(value) > 0:
            query = Tag.select().where(Tag.tag.startswith(value))
            if len(query) > 0:
                return query[0].tag
        return None

class Tajm(App):
    """ A Textual app to manage time slots """

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "layout.tcss"
    AUTO_FOCUS = "#year"

    selected_date = datetime.now()

    time_slot = None

    tags = []

    def compose(self) -> ComposeResult:
        logging.debug(f"{self.selected_date.strftime("%Y-%m-%d %H:%M:%S")}")

        """Create child widgets for the app."""
        yield Header()

        with Container(id="app-grid"):
            with Static("One", classes="box", id="date_row"):
                with Horizontal():
                    yield YearInput(id="year", max_length=4, validators=[ValidMinMax(1, 9999, "year")], validate_on=["changed"])
                    yield MonthInput(id="month", max_length=2, validators=[ValidMinMax(1, 12, "month")], validate_on=["changed"])
                    yield DayInput(id="day", max_length=2, validators=[ValidDay(self)], validate_on=["changed"])
                    yield Label(id="week")
        
            with Static("Two", classes="box"):
                with Vertical():    
                    yield Label(id="slot_status")
                with Horizontal():
                    yield HourInput(id="t1h", max_length=2, validators=[ValidMinMax(0, 23, "hour")], validate_on=["changed"])
                    yield MinuteInput(id="t1m", max_length=2, validators=[ValidMinMax(0, 59, "minute")], validate_on=["changed"])
                    yield Label("to")
                    yield HourInput(id="t2h", max_length=2, validators=[ValidMinMax(0, 23, "hour")], validate_on=["changed"])
                    yield MinuteInput(id="t2m", max_length=2, validators=[ValidMinMax(0, 59, "minute")], validate_on=["changed"])
                    yield Label(id="slot_summary")
                with Vertical():    
                    yield Input(id="new_tag", placeholder="Tag...→...↩", max_length=25, suggester=TagSuggester())
                    yield Markdown(id="tags")
                with Vertical():    
                    yield TextArea(id="notes")
                with Horizontal():    
                    yield Button.success(":floppy_disk:", id="save")
                    yield Button.success(":new:", id="new")
                    yield Button.error(":wastebasket:", id="remove", disabled=True)
            with Static("Three", classes="box"):
                yield Tabs(Tab("Day", id="day_tab"), Tab("Day stats", id="day_stats_tab"), Tab("Week stats", id="week_stats_tab"), Tab("Month stats", id="month_stats_tab"), Tab("Year stats", id="year_stats_tab"))
                yield DataTable(id="datatable", cursor_type="row")

        yield Footer()

    def update_selected_date(self, new_date):
        self.selected_date = new_date
        week_label = self.query_one("#week")
        week_label.update(f"{self.selected_date.strftime('%Y-%m-%d')} Week# {self.selected_date.isocalendar().week}")

        """ update the active tab by forcing reload """
        tabs = self.app.query_one(Tabs)
        active_tab = tabs.active
        tabs.watch_active(active_tab, active_tab)

    def reset_for_new_time_slot(self):
        self.update_selected_date(datetime.now())
        self.time_slot = None
        self.query_one("#year").value = f"{self.selected_date.strftime("%Y")}"
        self.query_one("#month").value = f"{self.selected_date.strftime("%m")}"
        self.query_one("#day").value = f"{self.selected_date.strftime("%d")}"
        self.query_one("#t1h").value = f"{self.selected_date.strftime("%H")}"
        self.query_one("#t1m").value = f"{self.selected_date.strftime("%M")}"
        self.query_one("#t2h").value = f"{self.selected_date.strftime("%H")}"
        self.query_one("#t2m").value = f"{self.selected_date.strftime("%M")}"
        self.tags = []
        self.update_tags()
        self.app.query_one("#tags").update("")
        self.app.query_one("#notes").text = ""
        self.update_slot_summary()

        """ update the active tab by forcing reload """
        tabs = self.app.query_one(Tabs)
        active_tab = tabs.active
        tabs.watch_active(active_tab, active_tab)

    def update_slot_summary(self):
        self.app.query_one("#slot_status").update("New!")

        """ start time """
        t1 = self.selected_date.replace(hour=int(self.app.query_one("#t1h").value), minute=int(self.app.query_one("#t1m").value))
        """ end time """
        t2 = self.selected_date.replace(hour=int(self.app.query_one("#t2h").value), minute=int(self.app.query_one("#t2m").value))
        self.time_slot = TimeSlot()
        self.time_slot.start_at = t1
        self.time_slot.end_at = t2
        slot_summary_label = self.query_one("#slot_summary")
        slot_summary_label.update(f"{str(self.time_slot.get_difference()[0]).zfill(2)}h {str(self.time_slot.get_difference()[1]).zfill(2)}m")

        """ disable remove button """
        self.app.query_one("#remove").disabled = True

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def on_mount(self):
        self.reset_for_new_time_slot()

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs."""
        datatable = self.query_one("#datatable")
        if event.tab.id == "day_tab":
            first_second = self.selected_date.replace(hour=0, minute=0, second=0, microsecond=0)
            last_second = first_second + timedelta(days=1)

            data = [
                ("start", "end", "duration", "tags"),
            ]
            data_keys = []
            query_ts = TimeSlot.select().where(TimeSlot.start_at >= first_second).where(TimeSlot.start_at < last_second).order_by(TimeSlot.start_at.asc())
            total_duration = 0
            for timeslot in query_ts:
                start_str = f"{str(timeslot.start_at.hour).zfill(2)}:{str(timeslot.start_at.minute).zfill(2)}"
                end_str = f"{str(timeslot.end_at.hour).zfill(2)}:{str(timeslot.end_at.minute).zfill(2)}"

                duration = timeslot.end_at - timeslot.start_at
                total_duration += duration.seconds
                duration_str = f"{str(duration.seconds//3600).zfill(2)}:{str((duration.seconds//60)%60).zfill(2)}"

                tags_str = ""
                query_t = TimeSlotTag.select().where(TimeSlotTag.timeslot == timeslot)
                for tag in query_t:
                    tags_str += f"*{tag.tag} "

                data.append((start_str, end_str, duration_str, tags_str))
                data_keys.append(timeslot.id)
                logging.debug(timeslot)

            """" add the duration total """
            total_duration_str = f"{str(total_duration//3600).zfill(2)}:{str((total_duration//60)%60).zfill(2)}"
            data.append(("", "", Text(total_duration_str, style="italic #03AC13"), ""))
            datatable.clear(columns=True)
            datatable.add_columns(*data[0])
            data_keys.append("total")
            i = 0
            for data_row in data[1:]:
                datatable.add_row(data_row[0], data_row[1], data_row[2], data_row[3], key=data_keys[i])
                i += 1    
                
    def load_time_slot(self, id):
        time_slot = TimeSlot.select().where(TimeSlot.id == id)
        self.time_slot = time_slot[0]

        self.app.query_one("#slot_status").update("Editing old")

        """ update start time """
        self.app.query_one("#t1h").value = str(self.time_slot.start_at.hour).zfill(2)
        self.app.query_one("#t1m").value = str(self.time_slot.start_at.minute).zfill(2)

        """ update end time """
        self.app.query_one("#t2h").value = str(self.time_slot.end_at.hour).zfill(2)
        self.app.query_one("#t2m").value = str(self.time_slot.end_at.minute).zfill(2)

        slot_summary_label = self.query_one("#slot_summary")
        slot_summary_label.update(f"{str(self.time_slot.get_difference()[0]).zfill(2)}h {str(self.time_slot.get_difference()[1]).zfill(2)}m")

        """ update tags """
        self.tags = []
        query = TimeSlotTag.select().where(TimeSlotTag.timeslot == self.time_slot)
        for timeslottag in query:
            self.tags.append(timeslottag.tag.tag)
        self.update_tags() 

        """ update notes """
        self.app.query_one("#notes").load_text(self.time_slot.note)

        """ enable remove button """
        self.app.query_one("#remove").disabled = False

    def update_tags(self):
            tags = self.query_one("#tags")
            tags_content = ""
            for tag in self.tags:
                href_tag = f"remove_{tag}"
                href_tag = urllib.parse.quote(href_tag)
                tags_content += tag + f" [❌]({href_tag}) "
            tags.update(tags_content)

    @on(Input.Changed)
    def input_changed(self, event: Input.Changed) -> None:
        if event.validation_result != None and not event.validation_result.is_valid:
            self.notify(event.validation_result.failure_descriptions[0], severity="error")  
        if event.input.id == "new_tag":
            if len(event.value) > 0:
                query = Tag.select().where(Tag.tag.startswith(event.value))
                for tag in query:
                    logging.debug(f"mAtching item={tag}")

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "new_tag":
            tag = Tag.get_or_create(tag=event.value)
            self.tags.append(event.value)
            self.update_tags() 
            """ then clear the event.input """
            event.input.clear()

    @on(Markdown.LinkClicked)
    def check_link(self, markdown) -> None:
        if markdown.href.startswith("remove_"): 
            tag = urllib.parse.unquote(markdown.href[7:])
            self.tags.remove(tag)
            self.update_tags()

    @on(Button.Pressed)
    def button_clicked(self, pressed) -> None:
        if pressed.button.id == "save":
            """ here the user's intent is to save the time slot """
            notes = self.query_one("#notes")
            self.time_slot.note = notes.text
            self.time_slot.save()

            """ remember to associate all the tags """
            TimeSlotTag.delete().where(TimeSlotTag.timeslot == self.time_slot).execute()
            for tag in self.tags:
                tag_in_db = Tag.get(tag=tag)
                TimeSlotTag.create(timeslot=self.time_slot, tag=tag_in_db)

            self.reset_for_new_time_slot()

        if pressed.button.id == "remove":
            self.time_slot.delete_instance(recursive=True)
            self.reset_for_new_time_slot()

        if pressed.button.id == "new":
            self.reset_for_new_time_slot()

    @on(DataTable.RowSelected)
    def row_selected(self, message):
        """ we have the time slot id in message.row_key.value - now load"""
        if message.row_key != "total":
            self.load_time_slot(message.row_key.value)
        logging.debug("this is awesome")

if __name__ == "__main__":
    logging.basicConfig(filename='tajm.log', encoding='utf-8', level=logging.DEBUG)
    logging.debug("Spinning up")
    init_db()
    app = Tajm()
    app.run()
    close_db()