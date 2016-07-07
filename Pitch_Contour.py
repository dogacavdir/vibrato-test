from essentia.standard import MonoLoader,EqualLoudness,Windowing,Spectrum,SpectralPeaks,PitchSalienceFunction,PitchSalienceFunctionPeaks,PitchContours,FrameGenerator
import pylab as plt
from matplotlib.pylab import *
#plot,subplot,title,xlabel,ylabel,show,grid,figure
import numpy as np

loader = MonoLoader(filename = 'Neumman render 002.wav')
audio = loader()

frame_vector = []
pitch_vector = []
loudness_vector = []
pitch_confidence_vector = []
spectrum_vector = []
spectral_peak_vector = []

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
pitch_contours = PitchContours(binResolution=binResolution,hopSize=hopSize,sampleRate=sampleRate)

filtered_signal = equal_loudness(audio)
for frame in FrameGenerator(filtered_signal,frameSize,hopSize):
    frame_vector.append(frame)
    spec = spectrum(w(frame))
    spectrum_vector.append(spec)

frequencies_vector = []
magnitudes_vector = []
salienceFunction = []
function_vector = []

for i in range(len(spectrum_vector)):
    frequencies,magnitudes = spectral_peaks(spectrum_vector[i])
    frequencies_vector.append(frequencies)
    magnitudes_vector.append(magnitudes)

#salienceFunction=salience_function(frequencies_vector[0],magnitudes_vector[0])
#salienceFunction1=salience_function(frequencies_vector[1],magnitudes_vector[1])
#salienceFunction[3183]=salience_function(frequencies_vector[3183],magnitudes_vector[3183])


for i in range(len(spectrum_vector)):
    salienceFunction = salience_function(frequencies_vector[i],magnitudes_vector[i])
    function_vector.append(salienceFunction)

print len(frame_vector)

fig1 = plt.figure(1)
ax1 = fig1.add_subplot(211)
ax1.plot(salienceFunction)
grid()
title('Salience Function')

fig2 = plt.figure(1)
ax1 = fig2.add_subplot(212)
ax1.plot(frequencies_vector[0],magnitudes_vector[0])
grid()
title('Frequencies of the first frame vs Magnitudes')
show()


peakBins = []
peakSaliences = []
salienceBins = []
salienceValues = []

for i in range(len(frame_vector)):
    salienceBins,salienceValues = salience_function_peaks(function_vector[i])
    peakBins.append(salienceBins)
    peakSaliences.append(salienceValues)

contoursBins = []
contoursSaliences = []
contoursStartTimes = []
duration = 0


contoursBins,contoursSaliences,contoursStartTimes,duration = pitch_contours(peakBins,peakSaliences)

print contoursBins,contoursSaliences,contoursStartTimes,duration

'''fig1 = plt.figure(1)
ax1 = fig1.add_subplot(211)
ax1.plot(salienceBins)
grid()
title('Salience Bins')

fig2 = plt.figure(1)
ax2 = fig2.add_subplot(212)
ax2.plot(salienceValues)
grid()
title('Salience Values')
show()'''

