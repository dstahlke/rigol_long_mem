#!/usr/bin/python

import scipy.io.wavfile as wavfile

from rigol import RigolScope

scope = RigolScope("/dev/usbtmc0")
print scope.getName()

scope.setupAndTrigger()

# Docs say that first acq gives 600 samples and second gives all of them.
# But this doesn't appear to be true.
A = scope.getWaveRaw('CHAN1')

scope.localMode()

print '%d samples' % len(A)

wavfile.write('capture.wav', 44100, A)
