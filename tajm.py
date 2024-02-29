import logging
import re
from datetime import datetime
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.validation import Function, Number, ValidationResult, Validator
from textual.widgets import Header, Footer, Label, Input, Static, Tabs, TextArea, Button

class ValidTime(Validator):  
    def validate(self, value: str) -> ValidationResult:
        """Check a string is equal to its reverse."""
        pattern = re.compile("[0-2][0-9]:[0-5][0-9]")
        if pattern.fullmatch(value) != None:
            return self.success()
        else:
            return self.failure("That's not a valid hh:mm")

class Tajm(App):
    """ A Textual app to manage time slots """

    BINDINGS = [("q", "quit", "Quit"), ("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "layout.tcss"
    AUTO_FOCUS = "#end_time"

    def compose(self) -> ComposeResult:
        now = datetime.now()
        logging.debug(f"{now.strftime("%Y-%m-%d %H:%M:%S")}")

        """Create child widgets for the app."""
        yield Header()

        with Container(id="app-grid"):
            with Static("One", classes="box", id="date_row"):
                with Horizontal():
                    yield Input(id="year", value=f"{now.strftime("%Y")}", max_length=4)
                    yield Input(id="month", value=f"{now.strftime("%m")}", max_length=2)
                    yield Input(id="day", value=f"{now.strftime("%d")}", max_length=2)
                    yield Label("Week 9", id="week")

            with Static("Two", classes="box"):
                with Horizontal():
                    yield Input(id="t1h", value=f"{now.strftime("%H")}", max_length=2)
                    yield Input(id="t1m", value=f"{now.strftime("%M")}", max_length=2)
                    yield Input(id="t2h", value=f"{now.strftime("%H")}", max_length=2)
                    yield Input(id="t2m", value=f"{now.strftime("%M")}", max_length=2)
                with Horizontal():    
                    yield Input(id="label", placeholder="Tag...", max_length=25)
                with Horizontal():    
                    yield TextArea(id="notes")
                with Horizontal():    
                    yield Button.success("Register")
                    yield Button.error("Remove")

            with Static("Three", classes="box"):
                yield Tabs("Day", "Week", "Month", "Year")

#                yield Input(id="start_time", value=f"{now.strftime("%H:%M")}", max_length=5, validators=[ValidTime()], validate_on=["submitted"])
#                yield Input(id="end_time", placeholder="00:00", max_length=5, validators=[ValidTime()], validate_on=["submitted"])

        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


    @on(Input.Submitted)
    def show_invalid_reasons(self, event: Input.Submitted) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:
            self.notify(event.validation_result.failure_descriptions[0], severity="error", timeout=10)  

if __name__ == "__main__":
    logging.basicConfig(filename='tajm.log', encoding='utf-8', level=logging.DEBUG)
    logging.debug("Spinning up")
    app = Tajm()
    app.run()