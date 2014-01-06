#!/usr/bin/python

# Capture full memory (1M samples) from a Rigol DS1052E.
# Based upon
# http://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
# and modified to support deep memory.

import os
import time
import numpy as np

class usbtmc(object):
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""

    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)

    def write(self, command):
        os.write(self.FILE, command)
        # The Rigol docs say to wait a bit after each command.
        time.sleep(0.1)

    def read(self, length=4000):
        return os.read(self.FILE, length)

    def ask(self, command, length=4000):
        self.write(command)
        return self.read(length)

    def askFloat(self, command):
        return float(self.ask(command))

    def getName(self):
        return self.ask("*IDN?")

    def sendReset(self):
        self.write("*RST")


class RigolScope(usbtmc):
    """Class to control a Rigol DS1000 series oscilloscope"""
    def __init__(self, device):
        super(RigolScope, self).__init__(device)

    def setupAndTrigger(self):
        # Long memory mode seems to be very finicky.  For example, I have seen a situation in
        # which the waveform updates on the scope screen, but the download always returns the
        # same (old, never updating) waveform.  The following particular sequence of commands
        # seems to work well.  See "DS1000E-D Remote Data TX Commands.pdf".

        self.write(":STOP")
        self.write(":WAV:POIN:MODE RAW")
        self.write(":ACQ:MEMD LONG")
        trig_mode = self.ask(':TRIG:MODE?')
        self.write(":TRIG:"+trig_mode+":SWE SING")

        self.write(":RUN")
        print "Waiting for trigger"
        self.waitForStop()
        print "Acquiring"
        self.write(":STOP")

    def waitForStop(self):
        while self.ask(":TRIG:STAT?") != 'STOP':
            time.sleep(0.5)
        # A little extra delay, just in case.
        time.sleep(0.5)

    def getWaveRaw(self, chan="CHAN1"):
        self.write(":WAV:DATA? "+chan)
        max_len = 2000000
        # First 10 bytes are header.
        x = self.read(max_len)[10:]
        return np.frombuffer(x, 'B')

    def getWave(self, chan="CHAN1"):
        raw_byte = self.getWaveRaw(chan)
        volts_div = self.askFloat(":"+chan+":SCAL?")
        vert_offset = self.askFloat(":"+chan+":OFFS?")
        # This equation is from "DS1000E-D Data Format.pdf"
        A = (240-raw_byte)*(volts_div/25.0) - (vert_offset + volts_div*4.6)
        return A

    def getWaveTime(self, nsamps):
        # This equation is from "DS1000E-D Data Format.pdf".  It only works for 600 samples.
        #time_div = self.askFloat(":TIM:SCAL?")
        #time_offset = self.askFloat(":TIM:OFFS?")
        #pt_num = np.arange(nsamps)
        #return pt_num*(time_div/50.0) - (time_div*6 - time_offset)

        time_offset = self.askFloat(":TIM:OFFS?")
        samp_rate = self.askFloat(":ACQ:SAMP?")
        pt_num = np.arange(nsamps)
        return (pt_num - nsamps/2.0) / samp_rate + time_offset

    def localMode(self):
        self.write(":KEY:FORC")

if __name__ == "__main__":
    scope = RigolScope("/dev/usbtmc0")
    print scope.getName()
