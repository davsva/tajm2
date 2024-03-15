""" The tajm module holds the main function of the app as well as the App textual class """

import logging
import calendar
import urllib.parse
from datetime import datetime, timedelta
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header,
    Footer,
    Label,
    Input,
    Static,
    Tabs,
    Tab,
    TextArea,
    Button,
    Markdown,
    DataTable,
)
from textual.suggester import Suggester
from rich.text import Text
from time_slot import TimeSlot, Tag, TimeSlotTag, init_db, close_db
from custom_validators import ValidMinMax, ValidDay
from custom_inputs import YearInput, MonthInput, DayInput, HourInput, MinuteInput
from constants import Constants


class TagSuggester(Suggester):
    """TagSuggester is a Suggester that suggests the first matching tag found in the database"""

    async def get_suggestion(self, value):
        if len(value) > 0:
            query = Tag.select().where(Tag.tag.startswith(value))
            if len(query) > 0:
                return query[0].tag
        return None


class Tajm2(App):
    """A Textual app to manage time slots"""

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "layout.tcss"
    AUTO_FOCUS = "#year"

    selected_date = datetime.now()

    time_slot = None

    tags = []

    def compose(self) -> ComposeResult:
        day = self.selected_date.strftime("%Y-%m-%d %H:%M:%S")
        logging.debug(day)

        # Create child widgets for the app.
        yield Header()

        with Container(id="app-grid"):
            with Static("One", classes="box", id="date_row"):
                with Horizontal():
                    yield YearInput(
                        id="year",
                        max_length=4,
                        validators=[ValidMinMax(1, 9999, "year")],
                        validate_on=["changed"],
                    )
                    yield MonthInput(
                        id="month",
                        max_length=2,
                        validators=[ValidMinMax(1, 12, "month")],
                        validate_on=["changed"],
                    )
                    yield DayInput(
                        id="day",
                        max_length=2,
                        validators=[ValidDay(self)],
                        validate_on=["changed"],
                    )
                    yield Label(id="slot_status")
                    yield Label(id="week")

            with Static("Two", classes="box"):
                with Horizontal():
                    yield HourInput(
                        id="t1h",
                        max_length=2,
                        validators=[ValidMinMax(0, 23, "hour")],
                        validate_on=["changed"],
                    )
                    yield MinuteInput(
                        id="t1m",
                        max_length=2,
                        validators=[ValidMinMax(0, 59, "minute")],
                        validate_on=["changed"],
                    )
                    yield Label("to")
                    yield HourInput(
                        id="t2h",
                        max_length=2,
                        validators=[ValidMinMax(0, 23, "hour")],
                        validate_on=["changed"],
                    )
                    yield MinuteInput(
                        id="t2m",
                        max_length=2,
                        validators=[ValidMinMax(0, 59, "minute")],
                        validate_on=["changed"],
                    )
                    yield Label(id="slot_summary")
                with Vertical():
                    yield Input(
                        id="new_tag",
                        placeholder="Tag...→...↩",
                        max_length=25,
                        suggester=TagSuggester(),
                    )
                    yield Markdown(id="tags")
                with Vertical():
                    yield TextArea(id="notes")
                with Horizontal():
                    yield Button.success(":floppy_disk:", id="save")
                    yield Button.success(":new:", id="new")
                    yield Button.error(":wastebasket:", id="remove", disabled=True)
            with Static("Three", classes="box"):
                yield Tabs(
                    Tab("Day", id="day_tab"),
                    Tab("Day stats", id="day_stats_tab"),
                    Tab("Week stats", id="week_stats_tab"),
                    Tab("Month stats", id="month_stats_tab"),
                    Tab("Year stats", id="year_stats_tab"),
                )
                with VerticalScroll():
                    yield DataTable(id="datatable", cursor_type="row")

        yield Footer()

    def update_selected_date(self, new_date):
        """updates the selected date"""
        self.selected_date = new_date
        week_label = self.query_one("#week")
        day = self.selected_date.strftime("%Y-%m-%d")
        week_label.update(f"{day} Week# {self.selected_date.isocalendar().week}")

        # update the active tab by forcing reload
        tabs = self.app.query_one(Tabs)
        active_tab = tabs.active
        tabs.watch_active(active_tab, active_tab)

    def reset_for_new_time_slot(self):
        """resets the field making the inputs ready for a new time slot"""
        self.time_slot = TimeSlot()
        self.query_one("#year").value = self.selected_date.strftime("%Y")
        self.query_one("#month").value = self.selected_date.strftime("%m")
        self.query_one("#day").value = self.selected_date.strftime("%d")
        self.query_one("#t1h").value = self.selected_date.strftime("%H")
        self.query_one("#t1m").value = self.selected_date.strftime("%M")
        self.query_one("#t2h").value = self.selected_date.strftime("%H")
        self.query_one("#t2m").value = self.selected_date.strftime("%M")
        self.tags = []
        self.update_tags()
        self.app.query_one("#tags").update("")
        self.app.query_one("#notes").text = ""

        self.app.query_one("#slot_status").update("New")
        self.app.query_one("#slot_status").remove_class("white_text_on_red_background")
        self.app.query_one("#slot_status").add_class(
            "black_text_on_yellowgreen_background"
        )

        self.update_slot_summary()

        # disable remove button
        self.app.query_one("#remove").disabled = True

        # update the active tab by forcing reload
        tabs = self.app.query_one(Tabs)
        active_tab = tabs.active
        tabs.watch_active(active_tab, active_tab)

        # Set focus on the t1h input field
        self.query_one("#t1h").focus()

    def update_slot_summary(self):
        """start time"""
        t1 = self.selected_date.replace(
            hour=int(self.app.query_one("#t1h").value),
            minute=int(self.app.query_one("#t1m").value),
        )
        # end time
        t2 = self.selected_date.replace(
            hour=int(self.app.query_one("#t2h").value),
            minute=int(self.app.query_one("#t2m").value),
        )
        self.time_slot.start_at = t1
        self.time_slot.end_at = t2
        slot_summary_label = self.query_one("#slot_summary")
        slot_summary_label.update(
            (str(self.time_slot.get_difference()[0])).zfill(2)
            + "h "
            + str((self.time_slot.get_difference()[1])).zfill(2)
            + "m"
        )

    def action_toggle_dark(self) -> None:
        """an action to toggle dark mode"""
        self.dark = not self.dark

    def on_mount(self):
        """called when the app is mounted"""
        self.update_selected_date(datetime.now().replace(second=0, microsecond=0))
        self.reset_for_new_time_slot()

    def get_summary(self, start_date, end_date):
        """returns a tag summary as a list for the given period"""
        tags_dict = {}

        # process all the time slots within the dates
        query_all_ts = TimeSlot.select().where(
            (TimeSlot.start_at >= start_date) & (TimeSlot.end_at < end_date)
        )

        # for each time slot - sum the duration for each tag
        for ts in query_all_ts:  # pylint: disable=E1133
            duration_in_minutes = (ts.end_at - ts.start_at).seconds // 60
            query_all_tags = TimeSlotTag.select().where(TimeSlotTag.timeslot == ts)
            if query_all_tags:
                for tag in query_all_tags:  # pylint: disable=E1133
                    tags_dict[str(tag.tag)] = (
                        tags_dict.get(str(tag.tag), 0) + duration_in_minutes
                    )

        # order by duration desc
        sorted_list = sorted(tags_dict.items(), key=lambda x: x[1], reverse=True)

        # process the sorted_dict and replace the duration in minutes to
        # hour:minute format before returning
        output = [("tag", "duration")]
        for tag in sorted_list:
            output.append((tag[0], f"{tag[1] // 60}:{str(tag[1] % 60).zfill(2)}"))
        return output

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle TabActivated message sent by Tabs."""
        datatable = self.query_one("#datatable")
        datatable.clear(columns=True)
        if event.tab.id == "day_tab":
            first_second = self.selected_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            last_second = first_second + timedelta(days=1)

            data = [
                ("start", "end", "duration", "tags"),
            ]
            data_keys = []
            query_ts = (
                TimeSlot.select()
                .where(TimeSlot.start_at >= first_second)
                .where(TimeSlot.start_at < last_second)
                .order_by(TimeSlot.start_at.asc())
            )
            total_duration = 0
            for timeslot in query_ts:
                start_str = (
                    (str(timeslot.start_at.hour)).zfill(2)
                    + ":"
                    + str((timeslot.start_at.minute)).zfill(2)
                )
                end_str = (
                    (str(timeslot.end_at.hour)).zfill(2)
                    + ":"
                    + str((timeslot.end_at.minute)).zfill(2)
                )

                duration = timeslot.end_at - timeslot.start_at
                total_duration += duration.seconds
                duration_str = (
                    str((duration.seconds // 3600)).zfill(2)
                    + ":"
                    + str((duration.seconds // 60) % 60).zfill(2)
                )

                tags_str = ""
                query_t = TimeSlotTag.select().where(TimeSlotTag.timeslot == timeslot)
                for tag in query_t:  # pylint: disable=E1133
                    tags_str += f"*{tag.tag} "

                data.append((start_str, end_str, duration_str, tags_str))
                data_keys.append(timeslot.id)
                logging.debug(timeslot)

            # add the duration total
            total_duration_str = (
                str((total_duration // 3600)).zfill(2)
                + ":"
                + str((total_duration // 60) % 60).zfill(2)
            )
            data.append(("", "", Text(total_duration_str, style="italic #03AC13"), ""))
            datatable.add_columns(*data[0])
            data_keys.append("total")
            i = 0
            for data_row in data[1:]:
                datatable.add_row(
                    data_row[0], data_row[1], data_row[2], data_row[3], key=data_keys[i]
                )
                i += 1
        if event.tab.id == "day_stats_tab":
            start_date = self.selected_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_date = start_date + timedelta(days=1)
            logging.debug("Show stats for day %s to %s", start_date, end_date)
            data = self.get_summary(start_date, end_date)
            datatable.add_columns(*data[0])
            i = 0
            for data_row in data[1:]:
                datatable.add_row(data_row[0], data_row[1], key=f"skip_{i}")
                i += 1
        if event.tab.id == "week_stats_tab":
            day_of_week = self.selected_date.isoweekday() - 1
            start_date = self.selected_date.replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=day_of_week)
            end_date = start_date + timedelta(days=7)
            logging.debug("Show stats for week %s to %s", start_date, end_date)
            data = self.get_summary(start_date, end_date)
            datatable.add_columns(*data[0])
            i = 0
            for data_row in data[1:]:
                datatable.add_row(data_row[0], data_row[1], key=f"skip_{i}")
                i += 1
        if event.tab.id == "month_stats_tab":
            max_day = calendar.monthrange(
                self.selected_date.year, self.selected_date.month
            )[1]
            start_date = self.selected_date.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = start_date + timedelta(days=max_day)
            logging.debug("Show stats for month %s to %s", start_date, end_date)
            data = self.get_summary(start_date, end_date)
            datatable.add_columns(*data[0])
            i = 0
            for data_row in data[1:]:
                datatable.add_row(data_row[0], data_row[1], key=f"skip_{i}")
                i += 1
        if event.tab.id == "year_stats_tab":
            start_date = self.selected_date.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            end_date = self.selected_date.replace(
                month=12, day=31, hour=0, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)
            logging.debug("Show stats for year %s to %s", start_date, end_date)
            data = self.get_summary(start_date, end_date)
            datatable.add_columns(*data[0])
            i = 0
            for data_row in data[1:]:
                datatable.add_row(data_row[0], data_row[1], key=f"skip_{i}")
                i += 1

    def load_time_slot(self, db_id):
        """loads the specified time slot"""
        logging.debug("load_time_slot(%s)", db_id)
        time_slot = TimeSlot.select().where(
            TimeSlot.id == db_id  # pylint: disable=E1101
        )
        self.time_slot = time_slot[0]  # pylint: disable=E1136

        self.app.query_one("#slot_status").update("Editing")
        self.app.query_one("#slot_status").remove_class(
            "black_text_on_yellowgreen_background"
        )
        self.app.query_one("#slot_status").add_class("white_text_on_red_background")

        # update start time
        self.app.query_one("#t1h").value = str(self.time_slot.start_at.hour).zfill(2)
        self.app.query_one("#t1m").value = str(self.time_slot.start_at.minute).zfill(2)

        # update end time
        self.app.query_one("#t2h").value = str(self.time_slot.end_at.hour).zfill(2)
        self.app.query_one("#t2m").value = str(self.time_slot.end_at.minute).zfill(2)

        slot_summary_label = self.query_one("#slot_summary")
        slot_summary_label.update(
            str(self.time_slot.get_difference()[0]).zfill(2)
            + "h "
            + str(self.time_slot.get_difference()[1]).zfill(2)
            + "m"
        )

        # update tags
        self.tags = []
        query = TimeSlotTag.select().where(TimeSlotTag.timeslot == self.time_slot)
        for timeslottag in query:  # pylint: disable=E1133
            self.tags.append(timeslottag.tag.tag)
        self.update_tags()

        # update notes
        self.app.query_one("#notes").load_text(self.time_slot.note)

        # enable remove button
        self.app.query_one("#remove").disabled = False

    def update_tags(self):
        """updates the tags field"""
        tags = self.query_one("#tags")
        tags_content = ""
        for tag in self.tags:
            href_tag = f"remove_{tag}"
            href_tag = urllib.parse.quote(href_tag)
            tags_content += tag + f" [❌]({href_tag}) "
        tags.update(tags_content)

    @on(Input.Changed)
    def input_changed(self, event: Input.Changed) -> None:
        """called when an Input is changed"""
        if event.validation_result is not None and not event.validation_result.is_valid:
            self.notify(
                event.validation_result.failure_descriptions[0], severity="error"
            )
            return
        if event.input.id == "year":
            if (
                ValidMinMax(Constants.YEAR_MIN, Constants.YEAR_MAX, "year")
                .validate(event.input.value)
                .is_valid
            ):
                new_date = self.app.selected_date.replace(year=int(event.input.value))
                self.app.update_selected_date(new_date)

        if event.input.id == "month":
            if (
                ValidMinMax(Constants.MONTH_MIN, Constants.MONTH_MAX, "month")
                .validate(event.input.value)
                .is_valid
            ):
                new_date = self.app.selected_date.replace(month=int(event.input.value))
                self.app.update_selected_date(new_date)

        if event.input.id == "day":
            if ValidDay(self.app).validate(event.input.value).is_valid:
                new_date = self.app.selected_date.replace(day=int(event.input.value))
                self.app.update_selected_date(new_date)

        if isinstance(event.input, HourInput) or isinstance(event.input, MinuteInput):
            self.app.update_slot_summary()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        """called when an Input is submitted"""
        if event.input.id == "new_tag":
            Tag.get_or_create(tag=event.value)
            self.tags.append(event.value)
            self.update_tags()
            # then clear the event.input
            event.input.clear()

    @on(Markdown.LinkClicked)
    def check_link(self, markdown) -> None:
        """called when a Markdown link is clicked, used to remove tags"""
        if markdown.href.startswith("remove_"):
            tag = urllib.parse.unquote(markdown.href[7:])
            self.tags.remove(tag)
            self.update_tags()

    @on(Button.Pressed)
    def button_clicked(self, pressed) -> None:
        """called when a Button is pressed. Handled the save, new, and delete buttons"""
        if pressed.button.id == "save":
            # here the user's intent is to save the time slot
            self.time_slot.start_at = self.selected_date.replace(
                hour=int(self.app.query_one("#t1h").value),
                minute=int(self.app.query_one("#t1m").value),
            )
            self.time_slot.end_at = self.selected_date.replace(
                hour=int(self.app.query_one("#t2h").value),
                minute=int(self.app.query_one("#t2m").value),
            )

            # do some validations according to the tajm2 approved laws
            difference = self.time_slot.end_at - self.time_slot.start_at

            # §1 The timeslot must have a duration that is 1 minute or more
            if difference < timedelta(minutes=1):
                self.app.notify(
                    "No save due to violation of §1 - 'The timeslot must have a \
                    duration that is 1 minute or more'",
                    severity="error",
                )
                return

            # §2 The timeslot must not interfere with already stored time slots
            query = (
                TimeSlot.select()
                .where(TimeSlot.id != self.time_slot.id)  # pylint: disable=E1101
                .where(
                    (
                        (TimeSlot.start_at < self.time_slot.start_at)
                        & (TimeSlot.end_at > self.time_slot.start_at)
                        & (TimeSlot.end_at < self.time_slot.end_at)
                    )
                    | (
                        (TimeSlot.start_at > self.time_slot.start_at)
                        & (TimeSlot.start_at < self.time_slot.end_at)
                        & (TimeSlot.end_at > self.time_slot.end_at)
                    )
                    | (
                        (TimeSlot.start_at > self.time_slot.start_at)
                        & (TimeSlot.end_at < self.time_slot.end_at)
                    )
                    | (
                        (TimeSlot.start_at < self.time_slot.start_at)
                        & (TimeSlot.end_at > self.time_slot.end_at)
                    )
                )
            )
            if len(query) > 0:
                for ts in query:
                    logging.debug("Violation of time slot id %s", ts.id)
                self.app.notify(
                    "No save due to violation of §2 - 'The timeslot must not interfere \
                        with already stored time slots'",
                    severity="error",
                )
                return

            notes = self.query_one("#notes")
            self.time_slot.note = notes.text
            self.time_slot.save()

            # remember to associate all the tags
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
        """this function is called whenever the DataTable's row is selected"""
        # we have the time slot id in message.row_key.value - now load
        if (message.row_key != "total") and (
            str(message.row_key.value).startswith("skip_") is False
        ):
            self.load_time_slot(message.row_key.value)


def run_app():
    """single point to run the app"""
    logging.basicConfig(filename="tajm.log", encoding="utf-8", level=logging.DEBUG)
    logging.debug("Spinning up")
    init_db()
    app = Tajm2()
    app.run()
    close_db()


if __name__ == "__main__":
    run_app()
