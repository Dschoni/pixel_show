# Released by rdb under the Unlicense (unlicense.org)
# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt
import time
import os, struct, array
import signal as sig
from blinker import signal
from fcntl import ioctl
import threading as t
import subprocess

verbose = True
running = False
p=[]
java=[]
# Iterate over the joystick devices.
if verbose:
    print('Available devices:')

if verbose:
    for fn in os.listdir('/dev/input'):
        if fn.startswith('js'):
            print('  /dev/input/%s' % (fn))
    
# We'll store the states here.
axis_states = {}
button_states = {}
pressed = signal('pressed')
released = signal('released')
changed = signal('changed')
# These constants were borrowed from linux/input.h
axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'z',
    0x03 : 'rx',
    0x04 : 'ry',
    0x05 : 'rz',
    0x06 : 'trottle',
    0x07 : 'rudder',
    0x08 : 'wheel',
    0x09 : 'gas',
    0x0a : 'brake',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
    0x12 : 'hat1x',
    0x13 : 'hat1y',
    0x14 : 'hat2x',
    0x15 : 'hat2y',
    0x16 : 'hat3x',
    0x17 : 'hat3y',
    0x18 : 'pressure',
    0x19 : 'distance',
    0x1a : 'tilt_x',
    0x1b : 'tilt_y',
    0x1c : 'tool_width',
    0x20 : 'volume',
    0x28 : 'misc',
}

button_names = {
    0x120 : 'trigger',
    0x121 : 'thumb',
    0x122 : 'thumb2',
    0x123 : 'top',
    0x124 : 'top2',
    0x125 : 'pinkie',
    0x126 : 'base',
    0x127 : 'base2',
    0x128 : 'base3',
    0x129 : 'base4',
    0x12a : 'base5',
    0x12b : 'base6',
    0x12f : 'dead',
    0x130 : 'a',
    0x131 : 'b',
    0x132 : 'c',
    0x133 : 'x',
    0x134 : 'y',
    0x135 : 'z',
    0x136 : 'tl',
    0x137 : 'tr',
    0x138 : 'tl2',
    0x139 : 'tr2',
    0x13a : 'select',
    0x13b : 'start',
    0x13c : 'mode',
    0x13d : 'thumbl',
    0x13e : 'thumbr',

    0x220 : 'dpad_up',
    0x221 : 'dpad_down',
    0x222 : 'dpad_left',
    0x223 : 'dpad_right',

    # XBox 360 controller uses these codes.
    0x2c0 : 'dpad_left',
    0x2c1 : 'dpad_right',
    0x2c2 : 'dpad_up',
    0x2c3 : 'dpad_down',
}

axis_map = []
button_map = []

# Open the joystick device.
fn = '/dev/input/js0'
if verbose:
    print('Opening %s...' % fn)
jsdev = open(fn, 'rb')

# Get the device name.
#buf = bytearray(63)
buf = array.array('c', ['\0'] * 64)
ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
js_name = buf.tostring()
if verbose:
    print('Device name: %s' % js_name)

# Get number of axes and buttons.
buf = array.array('B', [0])
ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
num_axes = buf[0]

buf = array.array('B', [0])
ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
num_buttons = buf[0]

# Get the axis map.
buf = array.array('B', [0] * 0x40)
ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

for axis in buf[:num_axes]:
    axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
    axis_map.append(axis_name)
    axis_states[axis_name] = 0.0

# Get the button map.
buf = array.array('H', [0] * 200)
ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

for btn in buf[:num_buttons]:
    btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
    button_map.append(btn_name)
    button_states[btn_name] = 0

print '%d axes found: %s' % (num_axes, ', '.join(axis_map))
print '%d buttons found: %s' % (num_buttons, ', '.join(button_map))
def start_invader(sender, **kw):
    global running
    global java
    global p
    if kw['button']=='start':
        if running == False:
            print 'Invader_start'
            java=subprocess.Popen('cd /home/pi/Downloads/pixelcontroller-distribution-2.0.0/;\
                            java -jar PixelController.jar',stdout=subprocess.PIPE, shell=True)
            print 'invader_running'
            p=subprocess.Popen('python /home/pi/Documents/pixel_show/pixelpi.py pixelinvaders --udp-ip 127.0.0.1 --udp-port 6803',stdout=subprocess.PIPE, shell=True,preexec_fn=os.setsid)
            print 'Done calling'
            running = True
pressed.connect(start_invader)

def kill(sender, **kw):
    global running
    if button_states['select']==1 and kw['button']=='start':
        if running == True:
            os.killpg(os.getpgid(p.pid), sig.SIGTERM)
            a = subprocess.check_output('ps -e | grep java',shell=True)
            pid = int(a.strip().split(' ',1)[0])
            os.kill(pid,sig.SIGTERM)
            running = False
            
pressed.connect(kill)
    
# Main event loop
while True:
    evbuf = jsdev.read(8)
    if evbuf:
        e_time, value, type, number = struct.unpack('IhBB', evbuf)

        if type & 0x80:
            if verbose:
                print "(initial)",
        else:
            
            if type & 0x01:
                button = button_map[number]
                if button:
                    button_states[button] = value
                    if value:
                        if verbose:
                            print "%s pressed" % (button)
                        pressed.send('button',button=button)
                    else:
                        if verbose:
                            print "%s released" % (button)
                        released.send('button',button=button)

            if type & 0x02:
                axis = axis_map[number]
                if axis:
                    fvalue = value / 32767.0
                    axis_states[axis] = fvalue
                    if verbose:
                        print "%s: %.3f" % (axis, fvalue)
                    changed.send('axis',axis=axis,value=fvalue)
