import essentia
from essentia.standard import *
import numpy as np
import matplotlib.pyplot as plt

loader = MonoLoader(filename = 'Neumman-05 render 001.wav')
audio = loader()

frame_vector = []
pitch_vector = []
loudness_vector = []
pitch_confidence_vector = []
spectrum_vector = []
spectral_peak_vector = []

hopSize = 128
frameSize = 2048
sampleRate = 32000
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
fft = FFT(size=4*frameSize)

filtered_signal = equal_loudness(audio)
for frame in FrameGenerator(filtered_signal,frameSize,hopSize):
    frame_vector.append(frame)
    spec = spectrum(w(frame))
    spectrum_vector.append(spec)

frequencies_vector = []
magnitudes_vector = []
function_vector = []
filtered_frequencies = []
filtered_magnitudes = []

for frame_spectrum in spectrum_vector:
    frequencies, magnitudes = spectral_peaks(frame_spectrum)
    # list comprehension: create new list with values from frequencies that are not zero
    invalid_frequencies_indexes = [index for index, val in enumerate(frequencies) if not val]
    filtered_frequencies = [val for index, val in enumerate(frequencies)
                            if index not in invalid_frequencies_indexes]
    filtered_magnitudes = [val for index, val in enumerate(magnitudes)
                           if index not in invalid_frequencies_indexes]
    filtered_frequencies = essentia.array(filtered_frequencies).astype(type('float', (float, ), {}))
    filtered_magnitudes = essentia.array(filtered_magnitudes).astype(type('float', (float, ), {}))
    frequencies_vector.append(filtered_frequencies)
    magnitudes_vector.append(filtered_magnitudes)

for i in range(len(frequencies_vector)):
    freq = essentia.array(frequencies_vector[i])
    mag = essentia.array(magnitudes_vector[i])
    salienceFunction = salience_function(freq,mag)
    function_vector.append(salienceFunction)

# fig1 = plt.figure(1)
# ax1 = fig1.add_subplot(311)
# ax1.plot(function_vector[0])
# plt.grid()
# plt.title('Salience Function')
#
# fig2 = plt.figure(1)
# ax2 = fig2.add_subplot(312)
# ax2.plot(frequencies_vector[0])
# plt.grid()
# plt.title('Frequencies of the first frame vs Magnitudes')
#
# fig3 = plt.figure(1)
# ax3 = fig3.add_subplot(313)
# ax3.plot(magnitudes_vector[0])
# plt.grid()
# plt.title('Frequencies of the first frame vs Magnitudes')
# plt.show()


pool = essentia.Pool()
salienceBins = []
salienceValues = []
salienceBins_vector = []
salienceValues_vector = []

for i in range(len(frame_vector)):
    function = essentia.array(function_vector[i])
    salienceBins,salienceValues = salience_function_peaks(function)
    salienceBins_vector.append(salienceBins)
    salienceValues_vector.append(salienceValues)
    pool.add('allframes_salience_peaks_bins', salienceBins)
    pool.add('allframes_salience_peaks_saliences', salienceValues)


contoursBins,contoursSaliences,contoursStartTimes,duration = pitch_contours(
        pool['allframes_salience_peaks_bins'],
        pool['allframes_salience_peaks_saliences'])


# Spectral Analysis of frames of each pith trajectory

pitch_spec_vector = []
for pitch in contoursBins:
    for pitch_frame in FrameGenerator(pitch,frameSize,hopSize):
        pitch_spec = spectrum(w(pitch_frame))
        pitch_spec_vector.append(pitch_spec)


# fig = plt.figure(1)
# plt.plot(pitch_spec_vector[20])
# plt.xlim(0,100)
# plt.ylim(-100,200)
# plt.show()



# Pitch Salience
pitch_salience = PitchSalience(sampleRate=sampleRate)
pitchSalience = []
for frame_spectrum in spectrum_vector:
    pitchSalience.append(pitch_salience(frame_spectrum))



filtered_salience = pitchSalience[700:3180]
salience_spectrum = []
for salience_frames in FrameGenerator(filtered_salience):
    salience_spectrum.append(spectrum(w(salience_frames)))

# Plots the result of the spectrum for each pitch salience frames
for i in range(len(salience_spectrum)):
    fig = plt.figure(i)
    plt.plot(salience_spectrum[i])
    plt.ylim(0,0.1)
plt.show()




pass
# n_frames = len(pitch)
# print "number of frames:", n_frames
#
# # visualize output pitch
# fig = plt.figure()
# plot(range(n_frames), pitch, 'b')
# n_ticks = 10
# xtick_locs = [i * (n_frames / 10.0) for i in range(n_ticks)]
# xtick_lbls = [i * (n_frames / 10.0) * hopSize / sampleRate for i in range(n_ticks)]
# xtick_lbls = ["%.2f" % round(x,2) for x in xtick_lbls]
# plt.xticks(xtick_locs, xtick_lbls)
# ax = fig.add_subplot(111)
# ax.set_xlabel('Time (s)')
# ax.set_ylabel('Pitch (Hz)')
# suptitle("Predominant melody pitch")
#
# # visualize output pitch confidence
# fig = plt.figure()
# plot(range(n_frames), confidence, 'b')
# n_ticks = 10
# xtick_locs = [i * (n_frames / 10.0) for i in range(n_ticks)]
# xtick_lbls = [i * (n_frames / 10.0) * hopSize / sampleRate for i in range(n_ticks)]
# xtick_lbls = ["%.2f" % round(x,2) for x in xtick_lbls]
# plt.xticks(xtick_locs, xtick_lbls)
# ax = fig.add_subplot(111)
# ax.set_xlabel('Time (s)')
# ax.set_ylabel('Confidence')
# suptitle("Predominant melody pitch confidence")
#
# show()