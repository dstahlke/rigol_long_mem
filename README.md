Capture full memory (1M samples) from a Rigol DS1052E.

Based upon
http://www.cibomahto.com/2010/04/controlling-a-rigol-oscilloscope-using-linux-and-python/
and modified to support deep memory (a million samples).

Deep memory is s bit finicky, and this was a bit difficult to get working even making use of
the instructions on Rigol's site.  In the end I found a sequence of commands that appear to
work.
There are two sample scripts.  One saves the waveform as a WAV (audio) file and the other plots
a spectrogram.  When you run the scripts, the scope is put into single sweep trigger mode.
One it is triggered, the waveform data is downloaded.
Other trigger modes (e.g. `normal` or `auto`) do not appear to work properly, even when
acquisition is stopped before waveform download.
