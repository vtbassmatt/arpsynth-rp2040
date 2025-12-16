# adapted from https://github.com/todbot/circuitpython-synthio-tricks/tree/main/examples/eighties_arp

import board
import audiobusio, audiomixer, synthio
import keypad, analogio
import ulab.numpy as np
import neopixel, rainbowio
from arpy import Arpy
from ascii_art import AsciiArtDisplay

NEOPIXEL_COUNT = 20
DEFAULT_PIXEL_COLOR = (1,1,1)

knobA = analogio.AnalogIn(board.GP27)
knobB = analogio.AnalogIn(board.GP26)
keys = keypad.Keys( (board.GP7, board.GP8), value_when_pressed=False )
led = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)
pixels = neopixel.NeoPixel(board.GP0, NEOPIXEL_COUNT, auto_write=False)
aa_display = AsciiArtDisplay()

num_voices = 3       # how many voices for each note
lpf_basef = 2500     # filter lowest frequency
lpf_resonance = 1.5  # filter q

i2s_bck_pin = board.GP3
i2s_lck_pin = board.GP4
i2s_dat_pin = board.GP2
audio = audiobusio.I2SOut(bit_clock=i2s_bck_pin, 
                          word_select=i2s_lck_pin, 
                          data=i2s_dat_pin)

mixer = audiomixer.Mixer(channel_count=1, sample_rate=28000, buffer_size=2048)
synth = synthio.Synthesizer(channel_count=1, sample_rate=28000)
audio.play(mixer)
mixer.voice[0].play(synth)
mixer.voice[0].level = 0.8

# our oscillator waveform, a 512 sample downward saw wave going from +/-30k
wave_saw = np.linspace(30000, -30000, num=512, dtype=np.int16)  # max is +/-32k but gives us headroom
amp_env = synthio.Envelope(attack_level=1, sustain_level=1, release_time=0.5)

voices=[]  # holds our currently sounding voices ('Notes' in synthio speak)

chase_lights = [DEFAULT_PIXEL_COLOR] * NEOPIXEL_COUNT

# called by arpy to turn on a note
def note_on(n):
    # aa_display.log(f"note on {n}")
    led_color = rainbowio.colorwheel( n % 12 * 20  )
    led.fill(led_color)
    for j in range(NEOPIXEL_COUNT - 1, 0, -1):
        chase_lights[j] = chase_lights[j-1]
    chase_lights[0] = led_color
    for i in range(0, NEOPIXEL_COUNT):
        pixels[i] = chase_lights[i]
    pixels.show()
    fo = synthio.midi_to_hz(n)
    voices.clear()  # delete any old voices
    for i in range(num_voices):
        f = fo * (1 + i*0.007)
        lpf_f = fo * 8  # a kind of key tracking

        # in CircuitPython 9: lpf = synth.low_pass_filter( lpf_f, lpf_resonance )
        # in CircuitPython 10:
        lpf = synthio.Biquad( mode=synthio.FilterMode.LOW_PASS, frequency=lpf_f, Q=lpf_resonance)
        voices.append( synthio.Note( frequency=f, filter=lpf, envelope=amp_env, waveform=wave_saw) )
    synth.press(voices)

# called by arpy to turn off a note
def note_off(n):
    # aa_display.log(f"note off {n}")
    led.fill(0)
    synth.release(voices)

# simple range mapper, like Arduino map()
def map_range(s, a1, a2, b1, b2): return  b1 + ((s - a1) * (b2 - b1) / (a2 - a1))

arpy = Arpy()
arpy.note_on_handler = note_on
arpy.note_off_handler = note_off
arpy.on()

arpy.root_note = 37
arpy.set_arp('suspended4th')
aa_display.log("arp:" + arpy.arp_name())
aa_display.set_note(37)
aa_display.set_arpeggio(arpy.arp_name())

arpy.set_bpm( bpm=110, steps_per_beat=4 ) # 110 bpm 16th notes
arpy.set_transpose(distance=12, steps=0)
aa_display.set_tempo(110)
aa_display.set_transpose(0)

knobfilter = 0.75
knobAval = knobA.value
knobBval = knobB.value

while True:
    key = keys.events.get()
    if key:
        if key.key_number == 0:
            aa_display.button1_change(key.pressed)
        elif key.key_number == 1:
            aa_display.button2_change(key.pressed)

    if key and key.pressed:
        if key.key_number == 0:  # left button changes arp played
            arpy.next_arp()
            aa_display.log("arp:" + arpy.arp_name())
            aa_display.set_arpeggio(arpy.arp_name())

        elif key.key_number == 1:  # right button changes arp up iterations
            steps = (arpy.trans_steps + 1) % 3;
            arpy.set_transpose(steps=steps)
            aa_display.log(f"steps {steps}")
            aa_display.set_transpose(steps)

    # filter noisy adc
    knobAval = knobAval * knobfilter + (1-knobfilter) * knobA.value
    knobBval = knobBval * knobfilter + (1-knobfilter) * knobB.value

    # map knobA to root note
    note = int(map_range( knobAval, 0,65535, 24, 72) )
    arpy.root_note = note
    aa_display.knob1_change(knobAval)
    aa_display.set_note(note)
    
    # map knobB to bpm
    bpm = map_range(knobBval, 0,65535, 40, 180 )
    arpy.set_bpm(bpm)
    aa_display.knob2_change(knobBval)
    aa_display.set_tempo(int(bpm))

    arpy.update()
    aa_display.refresh()
