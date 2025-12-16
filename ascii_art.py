import time

_SCALE_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

MIDI_NOTES = (
    # take the MIDI note, subtract 24, and index into here
    [f"{n}0" for n in _SCALE_NOTES] +
    [f"{n}1" for n in _SCALE_NOTES] +
    [f"{n}2" for n in _SCALE_NOTES] +
    [f"{n}3" for n in _SCALE_NOTES] +
    [f"{n}4" for n in _SCALE_NOTES]
)

GREEN = chr(27) + "[32m"
INVERT_CYAN = chr(27) + "[97;46m"
INVERT_YELLOW = chr(27) + "[30;43m"
RESET = chr(27) + "[0m"

KNOB_ART = [
    # 0 - 0-12%
    [
        r" ~~~~~ ",
        r":     :",
        r":---- :",
        r":     :",
        r" ~~~~~ ",

    ],

    # 1 - 13-37%
    [
        r" ~~~~~ ",
        r": \   :",
        r":  \  :",
        r":   ` :",
        r" ~~~~~ ",
    ], 

    # 2 - 38-62%
    [
        r" ~~~~~ ",
        r":  |  :",
        r":  |  :",
        r":  `  :",
        r" ~~~~~ ",
    ], 

    # 3 - 63-87%
    [
        r" ~~~~~ ",
        r":   / :",
        r":  /  :",
        r": '   :",
        r" ~~~~~ ",
    ], 

    # 4 - 88-100%
    [
        r" ~~~~~ ",
        r":     :",
        r": ----:",
        r":     :",
        r" ~~~~~ ",
    ], 
]

BUTTON_ART = {
    True: [
        "+---+  ",
        "|:::|: ",
        "+---+: ",
        " `---` ",
    ],
    False: [
        "...... ",
        ":`+---+",
        ": |   |",
        " `+---+",
    ],
}


class AsciiArtDisplay:
    MAX_LOG_LINES = 20

    def __init__(self):
        self._dirty = True
        self._log = ["ARPsynth 6.7", "init"]
        self._knob1_value = 0
        self._knob2_value = 0
        self._button1_on = False
        self._button2_on = False

        self._note = 0
        self._tempo = 0
        self._arpeggio = ""
        self._transpose = 0

        self._refresh = 0.0

        self.clear_screen()

    def log(self, log_line):
        self._log.append(log_line)
        if len(self._log) > AsciiArtDisplay.MAX_LOG_LINES:
            self._log = self._log[-AsciiArtDisplay.MAX_LOG_LINES:]
        self._dirty = True

    def button1_change(self, value):
        if value != self._button1_on:
            self._dirty = True
        self._button1_on = value
    
    def button2_change(self, value):
        if value != self._button2_on:
            self._dirty = True
        self._button2_on = value

    def knob1_change(self, value):
        if value != self._knob1_value:
            self._dirty = True
        self._knob1_value = value
    
    def knob2_change(self, value):
        if value != self._knob2_value:
            self._dirty = True
        self._knob2_value = value
    
    def set_note(self, value):
        if value != self._note:
            self._dirty = True
        self._note = value
    
    def set_tempo(self, value):
        if value != self._tempo:
            self._dirty = True
        self._tempo = value
    
    def set_arpeggio(self, value):
        if value != self._arpeggio:
            self._dirty = True
        self._arpeggio = value
    
    def set_transpose(self, value):
        if value != self._transpose:
            self._dirty = True
        self._transpose = value
    
    def clear_screen(self):
        print("\033[H\033[J")

    def goto_0_0(self):
        print("\x1B[0;0H")

    def refresh(self):
        if not self._dirty:
            return
        
        now = time.monotonic()
        if now - self._refresh < 0.25:
            return
        
        # short variable name to fit in the ASCII art slot
        k1 = [
            self._draw_knob(self._knob1_value, 0),
            self._draw_knob(self._knob1_value, 1),
            self._draw_knob(self._knob1_value, 2),
            self._draw_knob(self._knob1_value, 3),
            self._draw_knob(self._knob1_value, 4),
        ]

        k2 = [
            self._draw_knob(self._knob2_value, 0),
            self._draw_knob(self._knob2_value, 1),
            self._draw_knob(self._knob2_value, 2),
            self._draw_knob(self._knob2_value, 3),
            self._draw_knob(self._knob2_value, 4),
        ]

        b1 = [
            self._draw_button(self._button1_on, 0),
            self._draw_button(self._button1_on, 1),
            self._draw_button(self._button1_on, 2),
            self._draw_button(self._button1_on, 3),
        ]
        b2 = [
            self._draw_button(self._button2_on, 0),
            self._draw_button(self._button2_on, 1),
            self._draw_button(self._button2_on, 2),
            self._draw_button(self._button2_on, 3),
        ]

        nte = GREEN + f"{MIDI_NOTES[self._note-24]:^5s}" + RESET
        tmp = GREEN + f"{self._tempo:^5d}" + RESET
        arpeggio__ = INVERT_CYAN + f"{self._arpeggio:^12s}" + RESET
        t_string = f"up {self._transpose}" if self._transpose else "----"
        transpose_ = INVERT_CYAN + f"{t_string:^12s}" + RESET
        log____________ = [
            INVERT_YELLOW + f"{self._log[ll] if abs(ll) <= len(self._log) else "":20s}" + RESET
            for ll in range(-9, 0, 1)
        ]

        # self.clear_screen()
        self.goto_0_0()
        print(fr"""+------------------------------------------------------------------+.
|`.                                                                  `.
|  `+------------------------------------------------------------------+
|   |  █████  ██████  ██████   ____ _   _ _  _ ___ _  _ ██████████████ |
|   | ██   ██ ██   ██ ██   ██  [__   \_/  |\ |  |  |__| ████████████   |
|   | ███████ ██████  ██████   ___|   |   | \|  |  |  | ██████████     |
|   | ██   ██ ██   ██ ██                        ____________________   |
|   | ██   ██ ██   ██ ██       ███████████████ [{log____________[0]}]  |
|   |   _____    _____     ____________        [{log____________[1]}]  |
|   |  ({nte})  ({tmp})   [{arpeggio__}]       [{log____________[2]}]  |
|   |   ‾‾‾‾‾    ‾‾‾‾‾    [{transpose_}]       [{log____________[3]}]  |
|   |   ♪NOTE    TEMPO     ‾‾‾‾‾‾‾‾‾‾‾‾        [{log____________[4]}]  |
|   |  {k1[0]}  {k2[0]}   ARPG     TRNS        [{log____________[5]}]  |
|   |  {k1[1]}  {k2[1]}  {b1[0]}  {b2[0]}      [{log____________[6]}]  |
|   |  {k1[2]}  {k2[2]}  {b1[1]}  {b2[1]}      [{log____________[7]}]  |
+   |  {k1[3]}  {k2[3]}  {b1[2]}  {b2[2]}      [{log____________[8]}]  |
 `. |  {k1[4]}  {k2[4]}  {b1[3]}  {b2[3]}       ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾   |
   `+------------------------------------------------------------------+""")
        self._dirty = False

# ____ ____ ___  ____ _   _ _  _ ___ _  _ 
# |__| |__/ |__] [__   \_/  |\ |  |  |__| 
# |  | |  \ |    ___]   |   | \|  |  |  | 

#  █████  ██████  ██████  ███████ ██    ██ ███    ██ ████████ ██   ██ 
# ██   ██ ██   ██ ██   ██ ██       ██  ██  ████   ██    ██    ██   ██ 
# ███████ ██████  ██████  ███████   ████   ██ ██  ██    ██    ███████ 
# ██   ██ ██   ██ ██           ██    ██    ██  ██ ██    ██    ██   ██ 
# ██   ██ ██   ██ ██      ███████    ██    ██   ████    ██    ██   ██ 
                                                                    

    def _draw_knob(self, amount, line):
        "amount can be 0-65535; line can be 0-4"
        bucket = int(amount / 655.35 / 25.0 + 0.5)
        return KNOB_ART[bucket][line]
        
    def _draw_button(self, pushed, line):
        "amount can be True/False; line can be 0-3"
        return BUTTON_ART[pushed][line]

if __name__ == '__main__':
    display = AsciiArtDisplay()
    display.refresh()