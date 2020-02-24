__author__ = 'powerraptor'
import mraa
import serial
import struct
import time
import datetime
from datetime import datetime
from itertools import islice
import ctypes
import os
import os, re, sys, time, socket
from settings import camaddr
from settings import camport
from decimal import *
# Data variables from mindflex
length      = 0
delta       = 0
theta       = 0
low_alpha   = 0
high_alpha  = 0
low_beta    = 0
high_beta   = 0
low_gamma   = 0
high_gamma  = 0
attention   = 0
meditation  = 0
poor_signal = 0
my_big_blob = ""
total_waves = 0
total_waves_total = 0
d_frac = 0
d_total = 0
t_frac = 0
t_total = 0
la_frac = 0
la_total = 0
ha_frac = 0
ha_total = 0
lb_frac = 0
lb_total = 0
hb_frac = 0
hb_total = 0
lg_frac = 0
lg_total = 0
hg_frac = 0
hg_total = 0
record_on = False
record_val = 0
new_value = 0
old_value = 0
gpio_pin = mraa.Gpio(25)
gpio_pin.dir(mraa.DIR_OUT)

def leave_program():
    if control_mode == 1:
	sys.exit()
    else:
	return

print("Select mode: Exit_Program (1) or Hand_Control(2)")
control_mode = int(raw_input("> "))
leave_program()
print("Select control: Meditation (1), Attention (2), or Alpha Wave Levels (3)")
control_desired = int(raw_input("> "))
print("Input threshold value. (80 recommended for Med or Att, 0.4 for Alpha)")
threshold = float(raw_input("> "))
if control_desired == 1:
    control_choice = "Meditation"
elif control_desired == 2:
    control_choice = "Attention"
elif control_desired == 3:
    control_choice = "Alpha"
print("Hand controlled by %s.") % control_choice
mindflex_serial = serial.Serial('/dev/rfcomm0', 57600) #timeout=.1
mindflex_serial.flushInput()

is_synced = False

def sync():
    global is_synced
    sync_bytes = 0
    while sync_bytes != 2:
        if unpack_a_byte() == 170:
            sync_bytes += 1
    is_synced = True

def parse():
    global is_synced
    global delta
    global theta
    global low_alpha
    global high_alpha
    global low_beta
    global high_beta
    global low_gamma
    global high_gamma
    global d_total
    global t_total
    global la_total
    global ha_total
    global lb_total
    global hb_total
    global lg_total
    global hg_total
    global total_waves_total
    global meditation
    global attention
    global la_frac
    global ha_frac
    global record_val
    global record_on
    global control_desired
    global threshold
    global control_mode
    global new_value
    global old_value
    if not is_synced:
        print("No Sync")
        return
    if is_synced:
        plength = unpack_a_byte()
        if plength == 170:
            is_synced = False
        elif plength == 32:
            i = 0
            while i <= plength:
                minddump = unpack_a_byte()
                if minddump == 131:
                    i += 1
                elif minddump == 24:
                    delta = unpack_three_bytes()
                    d_total += delta
                    theta = unpack_three_bytes()
                    t_total += theta
                    low_alpha = unpack_three_bytes()
                    la_total += low_alpha
                    high_alpha = unpack_three_bytes()
                    ha_total += high_alpha
                    low_beta = unpack_three_bytes()
                    lb_total += low_beta
                    high_beta = unpack_three_bytes()
                    hb_total += high_beta
                    low_gamma = unpack_three_bytes()
                    lg_total += low_gamma
                    high_gamma = unpack_three_bytes()
                    hg_total += high_gamma
                    att_code = unpack_a_byte()
                    attention = unpack_a_byte()
                    med_code = unpack_a_byte()
                    meditation = unpack_a_byte()
                    check_sum = unpack_a_byte()
                    total_waves = delta + theta + low_alpha + high_alpha + low_beta + high_beta + low_gamma + high_gamma
                    total_waves_total += total_waves
                    getcontext().prec = 5
                    la_frac = Decimal(low_alpha) / Decimal(total_waves)
                    ha_frac = Decimal(high_alpha) / Decimal(total_waves)
                    alpha_total = la_frac + ha_frac

                    if control_mode == 2:
                        if control_desired == 1:
                            print "Meditation: %d" % (meditation)
			    new_value = meditation
                            if meditation >= threshold and old_value < threshold:
                            	record_start()
				print "hand closed"
				time.sleep(1.0)
				record_stop()
				sys.exit()
                            else:
                            	record_stop()
				print "hand opened"
			    old_value = new_value

                        elif control_desired == 2:
                            print "Attention: %d" % (attention)
                            if attention >= threshold and old_value < threshold:
                            	record_start()
				print "hand closed"
				time.sleep(1.0)
				record_stop()
				sys.exit()
                            else:
                            	record_stop()
				print "hand opened"
			    old_value = new_value

                        elif control_desired == 3:
                            print "alpha_total: " + str(alpha_total)
                            if alpha_total >= threshold and old_value < threshold:
                            	record_start()
				print "hand closed"
				time.sleep(1.0)
				record_stop()
				sys.exit()
                            else:
                            	record_stop()
				print "hand opened"
			    old_value = new_value
                           
                    i += 29
                else:
                    i += 1
            is_synced = False
        else:
            i = 0
            while i <= plength:
                minddump = unpack_a_byte()
                i += 1
            is_synced = False
    return

def unpack_a_byte():
    byte = mindflex_serial.read(1)
    return struct.unpack('>B', byte)[0]

def unpack_three_bytes():
    my_three_bytes = mindflex_serial.read(3)
    three_bytes = ''.join([b for b in islice(my_three_bytes,0,3)])
    four_bytes = b'\x00' + three_bytes
    return struct.unpack('>I', four_bytes)[0]

def record_start():
    gpio_pin.write(1)

def record_stop():
    gpio_pin.write(0)

print("Waiting for Data")

while True:

    try:
        if not is_synced:
            sync()
        if is_synced:
            parse()
            #record()
        is_synced = False

    except KeyboardInterrupt:
        mindflex_serial.close()
        print("Closed mindflex COM port")
        break

