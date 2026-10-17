
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import json
import os

Window.clearcolor = (0.04, 0.04, 0.05, 1)


class CircleButton(Button):
    def __init__(self, bg_color=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)

        with self.canvas.before:
            Color(*bg_color)
            self.circle = Ellipse(pos=self.pos, size=self.size)

        self.bind(pos=self.update_circle, size=self.update_circle)

    def update_circle(self, *args):
        d = min(self.width, self.height)
        self.circle.size = (d, d)
        self.circle.pos = (
            self.x + (self.width - d) / 2,
            self.y + (self.height - d) / 2
        )


class CalculatorApp(App):
    def build(self):
        self.first = 0
        self.operator = ""
        self.new_number = True
        self.expression = ""

        self.history_file = os.path.join(
            self.user_data_dir, "history.json"
        )
        self.history = self.load_history()

        root = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=8
        )

        root.add_widget(Label(
            text="ASSALAFY CALCULATOR",
            font_size=20,
            color=(0.3, 0.65, 1, 1),
            size_hint_y=0.08
        ))

        self.expression_label = Label(
            text="",
            font_size=22,
            color=(0.65, 0.75, 0.85, 1),
            size_hint_y=0.12,
            halign="right",
            valign="middle"
        )
        self.expression_label.bind(
            size=lambda obj, val: setattr(obj, "text_size", val)
        )
        root.add_widget(self.expression_label)

        self.display = Label(
            text="0",
            font_size=48,
            color=(1, 1, 1, 1),
            size_hint_y=0.22,
            halign="right",
            valign="middle"
        )
        self.display.bind(
            size=lambda obj, val: setattr(obj, "text_size", val)
        )
        root.add_widget(self.display)

        history_button = Button(
            text="ASSALAFY HISTORY Calculations",
            size_hint_y=None,
            height=42,
            background_normal="",
            background_color=(0.12, 0.30, 0.58, 1)
        )
        history_button.bind(on_press=self.show_history)
        root.add_widget(history_button)

        grid = GridLayout(
            cols=4,
            spacing=5,
            padding=3
        )

        buttons = [
            "C", "⌫", "%", "/",
            "7", "8", "9", "*",
            "4", "5", "6", "-",
            "1", "2", "3", "+",
            "±", "0", ".", "="
        ]

        gray = (0.18, 0.19, 0.21, 1)
        gray2 = (0.30, 0.31, 0.34, 1)
        orange = (1.0, 0.55, 0.10, 1)
        blue = (0.10, 0.40, 0.95, 1)
        red = (0.80, 0.12, 0.15, 1)

        for symbol in buttons:
            color = gray
            if symbol in ["+", "-", "*", "/", "%"]:
                color = orange
            elif symbol == "=":
                color = blue
            elif symbol == "C":
                color = red
            elif symbol in ["⌫", "±"]:
                color = gray2

            button = CircleButton(
                text=symbol,
                bg_color=color,
                font_size=23
            )
            button.bind(on_press=self.press)
            grid.add_widget(button)

        root.add_widget(grid)
        return root

    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def show_history(self, instance):
        text = "\n".join(self.history[-30:][::-1])
        if not text:
            text = "Babu tarihin lissafi tukuna."

        label = Label(
            text=text,
            size_hint_y=None,
            halign="left",
            valign="top"
        )
        label.bind(
            texture_size=lambda obj, size: setattr(obj, "size", size)
        )
        scroll = ScrollView()
        scroll.add_widget(label)

        Popup(
            title="ASSALAFY HISTORY Calculations",
            content=scroll,
            size_hint=(0.9, 0.75)
        ).open()

    def press(self, button):
        value = button.text

        if value == "C":
            self.display.text = "0"
            self.expression_label.text = ""
            self.first = 0
            self.operator = ""
            self.expression = ""
            self.new_number = True

        elif value == "⌫":
            if not self.new_number:
                current = self.display.text[:-1]
                self.display.text = current if current else "0"

        elif value == "±":
            if self.display.text not in ["0", "Error"]:
                if self.display.text.startswith("-"):
                    self.display.text = self.display.text[1:]
                else:
                    self.display.text = "-" + self.display.text

        elif value == "%":
            try:
                current = float(self.display.text)
                self.expression_label.text = self.display.text + "%"
                self.display.text = str(current / 100)
                self.new_number = True
            except ValueError:
                self.display.text = "Error"

        elif value == ".":
            if self.new_number:
                self.display.text = "0."
                self.new_number = False
            elif "." not in self.display.text:
                self.display.text += "."

        elif value in ["+", "-", "*", "/"]:
            try:
                self.first = float(self.display.text)
            except ValueError:
                self.first = 0

            self.operator = value
            symbols = {
                "+": "+", "-": "−",
                "*": "×", "/": "÷"
            }
            self.expression = (
                f"{self.display.text} {symbols[value]}"
            )
            self.expression_label.text = self.expression
            self.new_number = True

        elif value == "=":
            if not self.operator:
                return

            try:
                second = float(self.display.text)
                symbols = {
                    "+": "+", "-": "−",
                    "*": "×", "/": "÷"
                }

                expression = (
                    f"{self.first:g} {symbols[self.operator]} {second:g}"
                )

                if self.operator == "+":
                    result = self.first + second
                elif self.operator == "-":
                    result = self.first - second
                elif self.operator == "*":
                    result = self.first * second
                else:
                    if second == 0:
                        self.expression_label.text = (
                            "Ba a raba da sifili"
                        )
                        self.display.text = "Error"
                        self.operator = ""
                        self.new_number = True
                        return
                    result = self.first / second

                if result == int(result):
                    result_text = str(int(result))
                else:
                    result_text = str(round(result, 8))

                self.expression_label.text = expression + " ="
                self.display.text = result_text

                self.history.append(
                    expression + " = " + result_text
                )
                self.save_history()
                self.operator = ""
                self.new_number = True

            except (ValueError, OverflowError):
                self.display.text = "Error"
                self.operator = ""
                self.new_number = True

        else:
            if self.new_number or self.display.text in ["0", "Error"]:
                self.display.text = value
                self.new_number = False
            else:
                self.display.text += value


CalculatorApp().run()
      
