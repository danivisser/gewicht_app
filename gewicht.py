import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

class GewichtTracker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.label = Label(text="Voer je gewicht in (kg):")
        self.add_widget(self.label)

        self.input_field = TextInput(hint_text="Gewicht", multiline=False)
        self.add_widget(self.input_field)

        self.submit_button = Button(text="Opslaan", on_press=self.gewicht_invoeren)
        self.add_widget(self.submit_button)

        self.view_button = Button(text="Bekijk gewichten", on_press=self.toon_gewichten)
        self.add_widget(self.view_button)

        self.result_label = Label(text="")
        self.add_widget(self.result_label)

    def gewicht_invoeren(self, instance):
        gewicht = self.input_field.text

        try:
            gewicht = float(gewicht)
            datum = datetime.now().strftime("%Y-%m-%d")

            conn, c = get_db_connection()
            c.execute("INSERT INTO gewicht (datum, gewicht) VALUES (?, ?)", (datum, gewicht))
            conn.commit()
            conn.close()

            self.result_label.text = "Gewicht opgeslagen!"
            self.input_field.text = ""

        except ValueError:
            self.result_label.text = "Onjuist gewicht jost"

    def toon_gewichten(self, instance):
        resultaat_scherm = self.parent.manager.get_screen("resultaat")
        resultaat_scherm.toon_gewichten()
        self.parent.manager.current = "resultaat" 



class GewichtScherm(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GewichtTracker()
        self.add_widget(self.layout)

class ResultaatScherm(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.label = Label(text="Opgeslagen gewichten:")
        layout.add_widget(self.label)

        self.resultaat_label = Label(text="")
        layout.add_widget(self.resultaat_label)

        self.terug_button = Button(text="Terug naar invoer", on_press=self.ga_terug)
        layout.add_widget(self.terug_button)

        self.add_widget(layout)

    def toon_gewichten(self):
        conn, c = get_db_connection()
        c.execute("SELECT datum, gewicht FROM gewicht ORDER BY datum DESC")
        rows = c.fetchall()
        conn.close()

        if rows:
            gewicht_lijst = "\n".join([f"{datum} - {gewicht} kg" for datum, gewicht in rows])
            self.resultaat_label.text = gewicht_lijst
        else:
            self.resultaat_label.text = "Nog geen gewichten opgeslagen."

    def ga_terug(self, instance):
        self.manager.current = "hoofd"


# Database setup
def setup_database():
    conn = sqlite3.connect("gewicht_tracker.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS gewicht(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              datum TEXT,
              gewicht REAL)''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect("gewicht_tracker.db")
    return conn, conn.cursor()


class GewichtApp(App):
    def build(self):
        setup_database()  # Database aanmaken bij opstarten
        sm = ScreenManager()

        sm.add_widget(GewichtScherm(name="hoofd"))
        sm.add_widget(ResultaatScherm(name="resultaat"))

        return sm
    
if __name__ == "__main__":
    GewichtApp().run()