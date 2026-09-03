from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Input, TextArea, Button, Select
from textual.containers import HorizontalGroup, VerticalGroup
from textual.binding import Binding
from textual.reactive import reactive


class CCEditor(VerticalGroup):
    unciphed = ""
    key = ""

    # This generator function defines the shape of the widget
    def compose(self) -> ComposeResult:
        yield Input(placeholder = "Raw or encoded text", id = "input")
        yield HorizontalGroup(Input(placeholder = "Shift", id = "shift", type = "integer", max_length=3, tooltip="An intiger, 1 - 25 to shift the input text"),
                              Button("Encrypt",id = "encrypt",flat=True,), 
                              Button("Decrypt",id = "decrypt",flat=True,), 
                              Button("Clear", id = "clear",flat=True,),
                              Select([
                                      ("Caeser Cipher", "caeser"),
                                      ("Vigenère Cipher", "vig")],
                                      prompt="Choose method (default = Caeser Cipher)",
                                      id = "method-select"),
                              id = "control_bar")
        yield TextArea(id = "output" , read_only=True, show_cursor=False, highlight_cursor_line=False)

    # These two methods can be avoided if TextArea was used instead of Input, but that broke the css formatting
    def on_input_blurred(self, event:Input.Blurred) -> None:
        if event.input.id == "shift":
            self.key = event.value
        else:
            self.unciphed = event.value

    def on_input_submitted(self, event:Input.Blurred) -> None:
        if event.input.id == "shift":
            self.key = event.value
        else:
            self.unciphed = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # It may be wise to just make these instance attirbutes.
        input_widget = self.query_one("#input", Input)
        shift_widget = self.query_one("#shift", Input)
        text_widget = self.query_one("#output", TextArea)
        if event.button.id == "clear":
            shift_widget.clear()
            shift_widget.refresh()
            input_widget.clear()
            input_widget.refresh()
            text_widget.clear()
            text_widget.refresh()
        else:
            text_widget.text = self._method(self.unciphed,self.key,event.button.id)
            text_widget.refresh()

    # AI stuff
    def caesar_cipher(self, text: str, shift: int | str, mode: str = "encrypt") -> str:
        if not isinstance(shift,int):
            shift = int(shift)
        if mode == "decrypt":
            shift = -shift

        result = []
        for char in text:
            if char.isupper():
                # Shift within uppercase ASCII range (A-Z)
                shifted = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
                result.append(shifted)
            elif char.islower():
                # Shift within lowercase ASCII range (a-z)
                shifted = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
                result.append(shifted)
            else:
                # Non-alphabetic characters remain unchanged
                result.append(char)

        return "".join(result)

    def vigenere_cipher(self, text: str, key: str, mode: str = "encrypt") -> str:
        if not key.isalpha():
            raise ValueError("Key must contain only alphabetic characters.")

        result = []
        key = key.lower()
        key_length = len(key)
        key_index = 0

        for char in text:
            if char.isalpha():
                # Determine shift magnitude from the current key character
                shift = ord(key[key_index % key_length]) - ord('a')
                if mode == "decrypt":
                    shift = -shift

                if char.isupper():
                    base = ord('A')
                    shifted_char = chr((ord(char) - base + shift) % 26 + base)
                    result.append(shifted_char)
                else:
                    base = ord('a')
                    shifted_char = chr((ord(char) - base + shift) % 26 + base)
                    result.append(shifted_char)

                # Only advance the key index when an alphabetic character is shifted
                key_index += 1
            else:
                # Leave spaces, punctuation, and digits untouched
                result.append(char)

        return "".join(result)
    # End AI stuff

    _method = caesar_cipher

    def on_select_changed(self, event: Select.Changed) -> None:
        self.method = event.value
        shift_widget = self.query_one("#shift", Input)
        match self.method:
            case "vig":
                shift_widget.placeholder = "Key"
                shift_widget.max_length = 0
                shift_widget.type = "text"
                shift_widget.tooltip = "Alphabetic keyword to transform the input text"
                self._method = self.vigenere_cipher
            case "caeser":
                shift_widget.placeholder = "Shift"
                shift_widget.max_length = 2
                shift_widget.type = "int"
                shift_widget.tooltip = "An intiger, 1 - 25 to shift the input text"
                self._method = self.caesar_cipher
        shift_widget.clear()

# Canabalized from the stopwatch tutorial 
class CypherApp(App):
    """A Textual app to manage stopwatches."""
    CSS_PATH = "cc.tcss"

    BINDINGS = [
                Binding("ctrl+d", "quit", "Quit", priority=True),
                Binding("escape", "unfocus", "Unfocus", priority=True),]


    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield CCEditor(id = "main_group")
        yield Footer()

    def action_unfocus(self) -> None:
        self.set_focus(None)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = CypherApp()
    app.run()