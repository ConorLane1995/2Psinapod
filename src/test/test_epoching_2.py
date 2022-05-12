import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.io as scio
import numpy as np
import pickle
import json


# load what we need from the config file
with open('/Users/veronica/2Psinapod/config.json','r') as f:
    config = json.load(f)

BASE_PATH = config['RecordingFolder'] # folder with all of the files generated by Suite2P for this recording (F.npy, iscell.npy, etc)
conditions_path = config['Conditions'] # name of the CSV (assumed to be in folder given two lines above) with the condition types of each trial (freq, intensity, etc)
output_path = config['AnalysisFile'] # name of the file that all of the analysis is getting saved in (tuning, best frequency, etc)
STIMULUS_FRAMERATE = config['TriggerFR']
TRIGGER_DELAY_IN_MS = config['TriggerDelay'] # delay between TDT sending a trigger and the stimulus actually happening
RECORDING_FRAMERATE = config['RecordingFR']
EPOCH_START_IN_MS = config['EpochStart']
EPOCH_END_IN_MS = config['EpochEnd']

def get_first_trial(cell_dictionary):
    # load the conditions file
    conditions_mat = scio.loadmat(BASE_PATH + conditions_path) # conditition type of each trial in chronological order (row 1 = trial 1)
    conditions = conditions_mat["stim_data"]
    f = conditions[0,0]
    i = conditions[0,1]
    cell = list(cell_dictionary.keys())[0]
    
    # get this trial
    return cell_dictionary[cell]['traces'][f][i][1]

def get_original_trial(fluo,onsets):
    # get the first trial for the first cell in this big fluorescence trace
    cell1_f = fluo[1,:]

    onsets = np.round(onsets)

    # find the first frame in this epoch
    first_frame = int(onsets[0] + EPOCH_START_IN_MS/1000*RECORDING_FRAMERATE)
    last_frame = int(onsets[0] + EPOCH_END_IN_MS/1000*RECORDING_FRAMERATE)

    return cell1_f[int(first_frame):int(last_frame)]

def main():
    # get the first trial from the cell dictionary we've created
    # find where this corresponds to the ORIGINAL fluorescence trace

    with open(BASE_PATH + output_path, 'rb') as f:
        cell_dictionary = pickle.load(f)

    onsets = np.load(BASE_PATH+"onsets.npy",allow_pickle=True)
    fluorescence_trace = np.load(BASE_PATH + "F.npy",allow_pickle=True) # uncorrected trace of dF/F
    neuropil_trace = np.load(BASE_PATH + "Fneu.npy",allow_pickle=True) # estimation of background fluorescence
    iscell_logical = np.load(BASE_PATH + "iscell.npy",allow_pickle=True) # Suite2P's estimation of whether each ROI is a cell or not

    corrected_fluo = fluorescence_trace - 0.7*neuropil_trace

    original_trace = get_original_trial(corrected_fluo,onsets)

    trace_from_dict = get_first_trial(cell_dictionary)

    print(original_trace - trace_from_dict)

    plt.plot(original_trace)
    plt.plot(trace_from_dict)

    plt.show()


if __name__=="__main__":
    main()