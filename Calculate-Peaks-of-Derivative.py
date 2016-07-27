from essentia import *
from essentia.standard import *
from numpy import *
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

# CSV File - Data Extraction

df = pd.read_csv('Violin Recordings Annotation - Sheet1.csv',index_col = 'Note')
df_new = df[df.Type == 'note']
df_no_vibrato = df_new[0:28]
df_std = df_new[28:57]
df_slow = df_new[57:86]
df_fast = df_new[86:115]
dataf = df_slow
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
pool = Pool()

# Now we are ready to start processing.
# 1. Load audio and pass it through the equal-loudness filter
#Files vector will be the first column of the CSV File, File_Name
files = dataf.File_Name
derivative_vector = []
pitch_vector = []
n_frames_vector = []
percentage_vector = []
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
    pitch_vector.append(pitch)
    # NOTE that we can avoid the majority of intermediate steps by using a composite algorithm
    #      PredominantMelody (see extractor_predominant_melody.py). This script will be usefull
    #      if you want to get access to pitch salience function and pitch contours.

    n_frames = len(pitch)
    # n_frames_vector.append(n_frames)
    # print "number of frames:", n_frames


    time=range(n_frames-1)
    dr1 = derivative(pitch)
    high_derivative_indexes = [index for index, val in enumerate(dr1) if val>100]
    normalized_derivatives = [val for index, val in enumerate(dr1)
                            if index not in high_derivative_indexes]
    low_derivative_indexes = [index for index, val in enumerate(normalized_derivatives) if val<-100]
    normalized_derivatives = [val for index, val in enumerate(normalized_derivatives)
                              if index not in low_derivative_indexes]

    derivative_vector.append(normalized_derivatives)
    # dr2 = derivative(dr1)
    # high_second_derivative_indexes = [index for index, val in enumerate(dr2) if val > 100]
    # normalized_second_derivatives = [val for index, val in enumerate(dr2)
    #                           if index not in high_second_derivative_indexes]
    # low_second_derivative_indexes = [index for index, val in enumerate(normalized_second_derivatives) if val < -100]
    # normalized_second_derivatives = [val for index, val in enumerate(normalized_second_derivatives)
    #                           if index not in low_second_derivative_indexes]
    # second_derivative_vector.append(normalized_second_derivatives)

    # Calculate the percentage of peaks od the pitch countor's derivative
    peaknumber = 0
    peaknumber = float(count_nonzero(normalized_derivatives))
    length = float(len(normalized_derivatives))
    peak_percentage = peaknumber/length*100.0
    percentage_vector.append(peak_percentage)


# Need to save the value into the new percentage column of the CSV File
dataf['Percentage_of_Derivative_Peaks'] = percentage_vector
# df_new.to_csv('Violin_Vibrato.csv', sep=',')

max_value = max(df_new.Percentage_of_Derivative_Peaks)
mean_value = mean(df_new.Percentage_of_Derivative_Peaks)
min_value = min(df_new.Percentage_of_Derivative_Peaks)
