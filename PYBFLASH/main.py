# main.py -- put your code here!

import sys
import pyb
import micropython
import time
micropython.alloc_emergency_exception_buf(200)

SWITCH_PINS = ['Y1', 'Y2']
NOT_YET_CONNECTED_LED_PIN = 'X8'
LED_PINS = ['X1', 'X2']

class PINLED(object):
    @classmethod
    def forpin(cls, pin_name):
        pin = pyb.Pin(pin_name, pyb.Pin.OUT_PP, pyb.Pin.PULL_DOWN)
        return cls(pin)

    def __init__(self, pin):
        self.pin = pin

    def on(self):
        self.pin.high()

    def off(self):
        self.pin.low()

    def toggle(self):
        self.pin.value(not self.pin.value())


serial = pyb.USB_VCP()
sw = pyb.Switch()

def tell_pressed(ser : object, name : bytes):
    def _tell_pressed_cb():
        ser.write(b'PRESSED ')
        ser.write(name)
        ser.write(b'\r\n')
    return _tell_pressed_cb

def evt(inttable, handler):
    def _evt_handler(x):
        extint = inttable[x]
        extint.disable()
        handler()
        extint.enable()
    return _evt_handler

#sw.callback(tell_pressed(serial, 'USR'))
nametable = {}
inttable = {}
def register_pin(pin_name):
    origirq = pyb.disable_irq()
    try:
        extint = pyb.ExtInt(pin_name, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_DOWN,
                            evt(inttable, tell_pressed(serial, pin_name)))
        nametable[pin_name] = extint
        inttable[extint.line()] = extint
        extint.enable()
    finally:
        pyb.enable_irq(origirq)

for p in SWITCH_PINS:
    register_pin(p)

# TODO Yuck I don't like this polling malarkey
# Is there a better way?  Perhaps I should look at select()
def waitchar(ser, echo=False):
    """Return character from ser.  Polls until there is one"""
    c = None
    while c is None:
        c = ser.read(1)
    if echo:
        print(c.decode(), end="")
    return c

def waitline(ser, echo=False):
    buf = b''
    c = b''
    while c != b'\r':
        c = waitchar(ser, echo=echo)
        buf += c
    return buf

def led_controller(ser):
    not_yet_connected = PINLED.forpin(NOT_YET_CONNECTED_LED_PIN)
    not_yet_connected.on()
    pins = {}
    # for num in [1,2,3,4]:
    #     pins[str(num)] = pyb.LED(num)
    for pin_name in LED_PINS:
        pins[pin_name] = PINLED.forpin(pin_name)
    while True:
        ser.write(b"*READY\r\n")
        line = waitline(ser).rstrip()
        if not line:
            continue
        cmd = line.decode().split()
        if len(cmd) == 1 and cmd[0].lower() == 'hello':
            not_yet_connected.off()
            ser.write(b"*OK\r\n")
            continue
        if len(cmd) != 3:
            ser.write(b"*ERR Wrong number of words\r\n")
            continue
        (_led, ledname, on_or_off) = line.decode().split()
        try:
            led = pins[ledname.upper()]
        except KeyError:
            ser.write(b"*ERR Invalid LED name\r\n")
            continue

        on_or_off = on_or_off.lower()
        if on_or_off == 'on':
            led.on()
        elif on_or_off == 'toggle':
            led.toggle()
        else:
            led.off()
        ser.write(b"*OK\r\n")
            
led_controller(serial)


# pin = pyb.Pin(pyb.Pin.board.X1, pyb.Pin.OUT_PP)
# timer = pyb.Timer(4)
# timer.init(freq=2)

# def toggle(pin):
#     if pin.value():
#         pin.value(0)
#     else:
#         pin.value(1)
        
# timer.callback(lambda t: toggle(pin))
