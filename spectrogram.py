#!/usr/bin/python

import matplotlib.pyplot as plt

from rigol import RigolScope

scope = RigolScope("/dev/usbtmc0")
print scope.getName()

scope.setupAndTrigger()

# Docs say that first acq gives 600 samples and second gives all of them.
# But this doesn't appear to be true.
A = scope.getWave('CHAN1')
t = scope.getWaveTime(len(A))
samp_rate = scope.askFloat(":ACQ:SAMP?")

print '%d samples' % len(A)
print 'Sampling rate is %f' % samp_rate

# Put the scope back in local mode
scope.write(":KEY:FORC")

plt.specgram(A, Fs=samp_rate)
plt.show()
