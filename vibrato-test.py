from essentia.standard import *
from pylab import *
from numpy import *
from matplotlib.pylab import *
import numpy as np
from sound_islands_detector import SoundIslandsDetector


loader = MonoLoader(filename = 'Neumman-32 render 001.wav')
audio = loader()

w = Windowing(type = 'hann')
spectrum = Spectrum()
pitch_vector = []


hopSize = 512
frameSize = 2048
sampleRate = 44100.
time = np.linspace(0, len(audio)/sampleRate, num = len(audio))
frame_to_time = []
local_time = 0
loudness_vector = []
pitch_confidence_vector = []

run_pitchContourSegmentation = PitchContourSegmentation (hopSize=hopSize)
pitch_detect = PitchYinFFT(frameSize=frameSize,sampleRate=sampleRate,minFrequency=140,maxFrequency=160)
loudness_detect = Loudness()



for frame in FrameGenerator(audio,frameSize,hopSize):
    spec = spectrum(w(frame))
    pitch, pitchConfidence = pitch_detect(spec)
    loudness = loudness_detect(audio)
    pitch_vector.append(pitch)
    pitch_confidence_vector.append(pitchConfidence)
    frame_to_time.append(local_time)
    local_time += hopSize / sampleRate # Obtaining the time array
    loudness_vector.append(loudness)


'''sid = SoundIslandsDetector(loudness_envelope=loudness_vector,
                           pitches=pitch_vector,
                           pitches_conf=pitch_confidence_vector)
sound_islands = sid.run()
print(sound_islands)
'''
onset,duration,MIDIpitch = run_pitchContourSegmentation(pitch_vector, audio)

'''for i in range(len(pitch_vector)):
    print "pitch", i, ":", pitch_vector [i], "pitch confidence:", pitchConfidence'''

'''for i in range(len(onset)):
    print "onset", i, ":", onset[i], "duration:", duration[i], "MIDIpitch", MIDIpitch[i]'''


vibrato = Vibrato(sampleRate=sampleRate, minFrequency = 1, maxFrequency = 5 )
vibratoFrequency, vibratoExtend = vibrato (pitch_vector)

print "vibrato frequency:", vibratoFrequency

fig1 = plt.figure(1)
ax1 = fig1.add_subplot(211)
ax1.plot(time,audio)
grid()
xlabel('time')
title('Original Audio')

fig2 = plt.figure(1)
ax4 = fig2.add_subplot(212)
ax4.plot(pitch_vector[700:1000])
grid()
xlabel('time')
ylabel('frequency(Hz)')
title('Detected Pitch Values')

show()
