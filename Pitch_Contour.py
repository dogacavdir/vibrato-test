from essentia.standard import *
from pylab import *
from numpy import *
from matplotlib.pylab import *
import numpy as np

loader = MonoLoader(filename = 'Neumman-32 render 001.wav')
audio = loader()

frame_vector = []
pitch_vector = []
loudness_vector = []
pitch_confidence_vector = []
spectrum_vector = []
spectral_peak_vector = []
frequencies = []
magnitudes = []

hopSize = 128
frameSize = 2048
sampleRate = 44100
size = 2048
zeroPadding = 4
binResolution = 10

time = np.linspace(0,len(audio)/sampleRate,num=len(audio))
frame_to_time = []
local_time = 0

equal_loudness = EqualLoudness(sampleRate=sampleRate)
w = Windowing(size=size,zeroPadding=zeroPadding,type='hann')
spectrum = Spectrum(size=size)
spectral_peaks = SpectralPeaks(sampleRate=sampleRate,orderBy='frequency')
salience_function = PitchSalienceFunction(binResolution=binResolution)
salience_function_peaks = PitchSalienceFunctionPeaks(binResolution=binResolution)


filtered_signal = equal_loudness(audio)
for frame in FrameGenerator(filtered_signal,frameSize,hopSize):
    frame_vector.append(frame)
    spec = spectrum(w(frame))
    spectrum_vector.append(spec)

for i in range(len(spectrum_vector)):
    frequencies,magnitudes = spectral_peaks(spectrum_vector[i])

salienceFunction = salience_function(frequencies,magnitudes)
salienceBins,salienceValues = salience_function_peaks(salienceFunction)



fig1 = plt.figure(1)
ax1 = fig1.add_subplot(211)
ax1.plot(salienceBins)
grid()
title('Salience Bins')

fig2 = plt.figure(1)
ax2 = fig2.add_subplot(212)
ax2.plot(salienceValues)
grid()
title('Salience Values')
show()

