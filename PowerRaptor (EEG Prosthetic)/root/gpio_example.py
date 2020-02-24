#!/usr/bin/python
import mraa

x = mraa.Gpio(25)

x.dir(mraa.DIR_OUT)

x.write(1)

x.write(0)
