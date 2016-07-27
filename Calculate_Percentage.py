import numpy as np
from numpy import *
import pandas as pd
from derivative_peak_percentage import derivative_peak_percentage

df = pd.read_csv('Violin Recordings Annotation - Sheet1.csv')
df_new = df[df.Type == 'note']
df_new = df_new[28:57]
df_new["Percentage of Derivative Peaks"] = np.nan
for file in df_new.File_Name:
    percentage = derivative_peak_percentage(file)
    index = df_new[df_new.File_Name == file].index
    df_new.set_value(index,"Percentage of Derivative Peaks", percentage)
pass

print df_new