# import sdl2
import sdl2
import sdl2.sdlttf
from ctypes import c_int, byref

from kivy_config_helper import config_kivy

# window configuration
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ORIG_DENSISTY = 2.0

# simulation configuration
DO_SIMULATE = False
SIMULATE_DPI = 100
SIMULATE_DENSITY = 1.0

# provided by the course
config_kivy(window_width=WINDOW_WIDTH,
            window_height=WINDOW_HEIGHT,
            curr_device_density=ORIG_DENSISTY,
            simulate_device=DO_SIMULATE,
            simulate_dpi=SIMULATE_DPI,
            simulate_density=SIMULATE_DENSITY)

# disable user resizing
from kivy.config import Config
Config.set('graphics', 'resizable', '0') 

# kivy imports
from kivy.app import App
from kivy.metrics import dp, Metrics
from kivy.lang import Builder
from kivy.uix.spinner import Spinner
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
import kivy.core.text
from kivy.graphics import Color, Rectangle, Line
from kivy.graphics.instructions import Callback


sdl2.sdlttf.TTF_Init()

fonts = {
            'OpenDyslexic': {"regular": "./Fonts/OpenDyslexic-Regular.ttf"},
            'FreeSerif': {"regular": "./Fonts/FreeSerif.otf"},
            'APHont': {"regular": "./Fonts/APHont-Regular_q15c.ttf"},
            'AnonymousPro': {"regular": "./Fonts/Anonymous Pro.ttf"},
            'Times': {"regular": "./Fonts/Times New Roman.ttf"}
        }

for fname in fonts.keys():
    fobj = fonts[fname]
    LabelBase.register(name=fname, fn_regular=(fobj["regular"]))

selected_font_index = 4
font_name = list(fonts.keys())[selected_font_index]
print(f"Font Name: {font_name}")

FONT_SIZE = 30

font_obj = fonts[font_name]
app_sdl2_font = sdl2.sdlttf.TTF_OpenFont(str.encode(font_obj["regular"]), FONT_SIZE)

def font_baseline_pos():
    return abs(sdl2.sdlttf.TTF_FontDescent(app_sdl2_font))

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words = []
        self.word_index = 0
        self.paused = False

    def show_file_chooser(self):
        content = LoadFileDialog(load=self.load_file, cancel=self.dismiss_popup)
        self.popup = Popup(title="Load A File", content=content, size_hint=(1, 1))
        self.popup.open()

    def load_file(self, path, filename):
        self.selected(filename)
        self.popup.dismiss()

    def dismiss_popup(self):
        self.popup.dismiss()

    def selected(self, filename):
        try:
            selected_file = filename[0]
            if selected_file:
                self.ids.play_button.disabled = False
                self.words = []
                with open(selected_file, 'r') as file:
                    self.words = file.read().split()
                self.word_index = 0
                Clock.schedule_interval(self.update_text, 60.0 / self.ids.wpm.wpm)
        except:
            pass
    
    def update_text(self, dt):
        if not self.paused and self.word_index < len(self.words):
            self.ids.wordlabel.word = self.words[self.word_index]
            self.ids.wordlabel.format_word(self.ids.wordlabel.word)
            self.word_index += 1
        elif self.word_index >= len(self.words):
            # loops back to the first word
            self.word_index = 0
    
    def toggle_pause(self):
        self.paused = not self.paused
        
class LoadFileDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class KivyTextMeasurement:
    def __init__(self, **kwargs):
        self.mlabel = kivy.core.text.Label(**kwargs)

    # Find the height of the resulting texture_size for the text if rendered on-screen
    def measure_text_height(self, text) -> int:
        return self.mlabel.get_extents(text)[1]

    # Find the width of the resulting texture_size for the text if rendered on-screen
    def measure_text_width(self, text) -> int:
        return self.mlabel.get_extents(text)[0]

    # Find the offsets from the left side of the font texture for the beginning of each glyph/character
    def find_glyph_offsets(self, text) -> list[int]:
        res = []
        res = [self.mlabel.get_extents(text[0:i])[0] for i in range(0, len(text) + 1)]
        return res

class WordLabelParent(FloatLayout):
    pass

class WordLabel(Label):
    _FONT_SIZE = FONT_SIZE
    _FONT_NAME = font_name
    font_size = NumericProperty(_FONT_SIZE * Metrics.dp)
    font_name = StringProperty(_FONT_NAME)
    text = StringProperty("")
    dp = NumericProperty(Metrics.dp)
    word = StringProperty("")
    focused = NumericProperty(0)

    def __init__(self, **kwargs):
        super(WordLabel, self).__init__(**kwargs)
        with self.canvas.before:
            Callback(self.before_canvas_callback)

    def on_dp(self, obj, v):
        print(f"on_dp({obj}, {v})")
        self.font_size = self._FONT_SIZE * v  # kivy.metrics.Metrics.dp

    def on_size(self, obj, sz):
        self.before_canvas_callback(None)
    
    def update_font(self, selected_font_index):
        self.font_name = list(fonts.keys())[selected_font_index]
    
    def update_size(self, size):
        self.font_size = size * Metrics.dp
    
    def before_canvas_callback(self, instr):
        baseline = font_baseline_pos()
        baseline_pos = dp(baseline)

        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(size=self.size, pos_hint=self.pos_hint, pos=self.pos)

            Color(0, 0, 0, 0.5)

            # horizontal lines
            Line(width=dp(1), rectangle=(
                self.x + dp(5), 
                self.y + dp(5), 
                self.width - dp(10),
                0
            ))

            Line(width=dp(1), rectangle=(
                self.x + dp(5), 
                self.y + self.height - dp(5), 
                self.width - dp(10),
                0
            ))

            # small vertical lines in the middle of label
            Line(width=dp(1), rectangle=(
                self.x + self.width/2, 
                self.y + dp(5), 
                0,
                dp(5)
            ))
            Line(width=dp(1), rectangle=(
                self.x + self.width/2, 
                self.y + self.height - dp(5), 
                0,
                -dp(5)
            ))
            
    
    def format_word(self, word):
        red = "[color=FF0000]"
        end = "[/color]"
        
        if len(word) > 7:
            self.focused = 5
        elif len(word) > 5:
            self.focused = 3
        elif len(word) > 3:
            self.focused = 1
        else:
            self.focused = 0
        
        self.text = word[:self.focused] + red + word[self.focused] + end + word[self.focused+1:]

        ktm = KivyTextMeasurement(font_size=self.font_size, font_name=self.font_name)
        offsets = ktm.find_glyph_offsets(self.word)

        align = offsets[self.focused] + (offsets[self.focused+1] - offsets[self.focused])/2
        right_align = ktm.measure_text_width(self.word)/2 - align
        left_align = self.width * 0.1

        self.pos[0] = self.pos[0] + right_align - left_align

class PlayButton(Button):
    def update_state(self):
        self.parent.toggle_pause()
        if self.text == 'Play':
            self.text = 'Pause'
        elif self.text == 'Pause':
            self.text = 'Play'

class SelectFont(Spinner):
    def on_select(self, text):
        selected_font = text
        if selected_font == 'OpenDyslexic':
            selected_font_index = 0
        elif selected_font == 'FreeSerif':
            selected_font_index = 1
        elif selected_font == 'APHont':
            selected_font_index = 2
        elif selected_font == 'AnonymousPro':
            selected_font_index = 3
        elif selected_font == 'Times':
            selected_font_index = 4
        
        self.parent.parent.ids.wordlabel.update_font(selected_font_index)

class SelectFontSize(Spinner):
    def on_select(self, text):
        size = int(text)
        self.parent.parent.ids.wordlabel.update_size(size)

class SelectWPM(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wpm = 60
    
    def on_change(self):
        self.wpm = int(self.text)
        Clock.unschedule(self.parent.parent.update_text) 
        Clock.schedule_interval(self.parent.parent.update_text, 60.0 / self.wpm)

class RSVPApp(App):
    pass

if __name__ == "__main__":
    RSVPApp().run()

