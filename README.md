# upy-switch-led-panel
MicroPython switch and LED panel

## Description

Uses a Micropython Pyboard to provide a one-touch interface to start and
monitor selected jobs on a GNU/Linux PC.

It works by binding systemd jobs to input pins (for triggering) and
output pins (for indicating via an LED whether that job is running).

It talks via a serial protocol over the USB interface.

## Inputs

Currently I'm using tactile switches, each debounced by a low-pass RC filter.
I find a 2.2 kOhm resistor and a 1uF capacitor works quite well, on the Y pins
starting at Y1.  Powering these tactile switches using the 3V3 and GND pins on
the Pyboard.

```
               --T--       _2k2_ 
    3V3 <------o   o------[_____]----*-----------> Yn
                                     |
				  -------  1uF
				  -------
				     |
    GND <-----------------------------
```

## Outputs

LEDs, each with a 100 Ohm resistor, on the X pins starting at X1.
The X* pins are connected at the LED anodes, and the LED cathodes are
connected via a 100 Ohm resistor to the Pyboard GND pin.

X9 is currently used as an indicator for 'not seen host yet'.
When the pyBoard starts up the X9 pin is brought high, and
when the host writes line 'HELLO' over the serial line it is brought low.

Of course it's all controlled in software on the Pyboard, so can be changed
at will.

```
                    ^^            _100_
    Xn <-----------(>|)----------[_____]-------> GND
```

## Host side

The host runs a small Perl 5 script that communicates over /dev/ttyACM0 with
the PyBoard, monitoring and starting the systemd jobs specified in
/usr/local/etc/upy-switch-systemd/jobtab 

## Copyright and License

Copyright (C) 2015  Nicholas Booker <nmb@nickbooker.uk>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
