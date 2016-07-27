import numpy as np
from numpy import *
import pandas as pd
from derivative_peak_percentage import derivative_peak_percentage
import json

with open('input_data.json', 'r') as data_file:
    data = json.load(data_file)

# vibrato_rate = 'slow vibrato'
# df = pd.read_csv('Violin_Recordings_Annotation_Sheet1.csv')
# df_new = df[df.Type == 'note']
# df_new["Percentage_of_Derivative_Peaks"] = np.nan
# files = df_new[df_new['Presence_of_Vibrato'] == vibrato_rate]
percentages = []
for i in range(len(data)):
    file = data[i]['File_Name']
    percentage = derivative_peak_percentage(file)
    print(file, percentage)
    percentages.append(percentage)
pass
