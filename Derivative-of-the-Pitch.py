from essentia import *
from essentia.standard import *
from numpy import *
import matplotlib.pyplot as plt

# In this example we will extract predominant melody given an audio file by
# running a chain of algorithms.

# First, create our algorithms:
hopSize = 128
frameSize = 2048
sampleRate = 44100
guessUnvoiced = True

run_windowing = Windowing(type='hann', zeroPadding=4 * frameSize)  # Hann window with x4 zero padding
run_spectrum = Spectrum(size=frameSize * 4)
run_spectral_peaks = SpectralPeaks(minFrequency=1,
                                   maxFrequency=20000,
                                   maxPeaks=100,
                                   sampleRate=sampleRate,
                                   magnitudeThreshold=0,
                                   orderBy="frequency")
run_pitch_salience_function = PitchSalienceFunction()
run_pitch_salience_function_peaks = PitchSalienceFunctionPeaks()
run_pitch_contours = PitchContours(hopSize=hopSize)
run_pitch_contours_melody = PitchContoursMelody(guessUnvoiced=guessUnvoiced,
                                                hopSize=hopSize)

# ... and create a Pool
pool = Pool();

# Now we are ready to start processing.
# 1. Load audio and pass it through the equal-loudness filter
no_vibrato = 'Neumman-05 render 001.wav'
std_vibrato = 'Neumman-07 render 019.wav'
slow_vibrato = 'Neumman-10 render 008.wav'
fast_vibrato = 'Neumman-13 render 019.wav'

files = [no_vibrato,std_vibrato,slow_vibrato,fast_vibrato]
derivative_vector = []
for file in files:
    audio = MonoLoader(filename=file)()
    audio = EqualLoudness()(audio)

    # 2. Cut audio into frames and compute for each frame:
    #    spectrum -> spectral peaks -> pitch salience function -> pitch salience function peaks
    for frame in FrameGenerator(audio, frameSize=frameSize, hopSize=hopSize):
        frame = run_windowing(frame)
        spectrum = run_spectrum(frame)
        peak_frequencies, peak_magnitudes = run_spectral_peaks(spectrum)

        salience = run_pitch_salience_function(peak_frequencies, peak_magnitudes)
        salience_peaks_bins, salience_peaks_saliences = run_pitch_salience_function_peaks(salience)

        pool.add('allframes_salience_peaks_bins', salience_peaks_bins)
        pool.add('allframes_salience_peaks_saliences', salience_peaks_saliences)

    # 3. Now, as we have gathered the required per-frame data, we can feed it to the contour
    #    tracking and melody detection algorithms:
    contours_bins, contours_saliences, contours_start_times, duration = run_pitch_contours(
        pool['allframes_salience_peaks_bins'],
        pool['allframes_salience_peaks_saliences'])
    pitch, confidence = run_pitch_contours_melody(contours_bins,
                                                  contours_saliences,
                                                  contours_start_times,
                                                  duration)

    # NOTE that we can avoid the majority of intermediate steps by using a composite algorithm
    #      PredominantMelody (see extractor_predominant_melody.py). This script will be usefull
    #      if you want to get access to pitch salience function and pitch contours.

    n_frames = len(pitch)
    print "number of frames:", n_frames

    # # visualize output pitch
    # fig = plt.figure()
    # plt.plot(range(n_frames), pitch, 'b')
    # n_ticks = 10
    # xtick_locs = [i * (n_frames / 10.0) for i in range(n_ticks)]
    # xtick_lbls = [i * (n_frames / 10.0) * hopSize / sampleRate for i in range(n_ticks)]
    # xtick_lbls = ["%.2f" % round(x,2) for x in xtick_lbls]
    # plt.xticks(xtick_locs, xtick_lbls)
    # ax = fig.add_subplot(111)
    # ax.set_xlabel('Time (s)')
    # ax.set_ylabel('Pitch (Hz)')
    # plt.suptitle("Predominant melody pitch")
    #
    # # visualize output pitch confidence
    # fig = plt.figure()
    # plt.plot(range(n_frames), confidence, 'b')
    # n_ticks = 10
    # xtick_locs = [i * (n_frames / 10.0) for i in range(n_ticks)]
    # xtick_lbls = [i * (n_frames / 10.0) * hopSize / sampleRate for i in range(n_ticks)]
    # xtick_lbls = ["%.2f" % round(x,2) for x in xtick_lbls]
    # plt.xticks(xtick_locs, xtick_lbls)
    # ax = fig.add_subplot(111)
    # ax.set_xlabel('Time (s)')
    # ax.set_ylabel('Confidence')
    # plt.suptitle("Predominant melody pitch confidence")
    # plt.show()

    pass

    time = range(n_frames-1)
    dr1 = derivative(pitch)
    high_derivative_indexes = [index for index, val in enumerate(dr1) if val>100]
    normalized_derivatives = [val for index, val in enumerate(dr1)
                            if index not in high_derivative_indexes]
    low_derivative_indexes = [index for index, val in enumerate(normalized_derivatives) if val<-100]
    normalized_derivatives = [val for index, val in enumerate(normalized_derivatives)
                              if index not in low_derivative_indexes]

    derivative_vector.append(normalized_derivatives)

    # fig = plt.figure()
    # plt.subplot(211)
    # plt.plot(range(n_frames),pitch,'b')
    # plt.xlabel('Time (s)')
    # plt.ylabel('Pitch (Hz)')
    # plt.suptitle("Predominant melody pitch")
    # plt.subplot(212)
    # plt.plot(range(len(normalized_derivatives)),normalized_derivatives,'b')
    # plt.xlabel('Time(s)')
    # plt.ylabel('Derivative')
    # plt.ylim(-10,10)
    # plt.suptitle("1st Derivative of the pitch")
    # plt.show()

peaknumber = 0
percentage_vector = []
peaknumber_vector = []
length_vector = []
# Calculate vibrato rate for each vibrato
for track in derivative_vector:
    peaknumber = float(count_nonzero(track))
    peaknumber_vector.append(peaknumber)
    length = float(len(track))
    length_vector.append(length)
    peak_percentage = peaknumber/length*100.0
    percentage_vector.append(peak_percentage)

pass

# # The fast vibrato rate
# derivative_peak_no = count_nonzero(normalized_derivatives)
# length = len(normalized_derivatives)
# zero_no = length - derivative_peak_no
#
# peak_percentage = derivative_peak_no/length*100
#
# pass
