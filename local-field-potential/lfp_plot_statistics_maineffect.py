# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 17:36:40 2025

@author: ssenapat

Read pickle files with mainEffect pvalues (results from lfp_ttest.py) to generate heatmap
{For directionality effect in significant pairwise comparison, 
 check scripts lfp_pairwise_direction_maineffect.py and lfp_plot_pairwise_direction_maineffect.py}
"""

def load_probe():
    
    file = Path('G:/Final_exps_spikes/LFP/Elfie/p1/p1_15/probe-info.csv')
    prb = pd.read_csv(file)
    prb_ylocs = prb['y']    # column representing the depths of channels
    return prb_ylocs


def combine_channels(df, val_list, index):
    
    df.loc[index,:] = val_list
    return df



'''
### FOR HEATMAP plots : Only picking up the minimum p-value without caring about which pairwise comparison it belongs to
'''
def add_depth_info(df, depths):
    
    # add probe info to rest of the data
    df['probeinfo'] = np.array(depths)
    # sort the data based on depth of channels
    df = df.sort_values(by=['probeinfo']).astype(float)
    # drop the probe location column
    df.drop(['probeinfo'], axis=1, inplace=True)
    # change the index for ease during plotting
    df.set_index(np.unique(depths), inplace=True)
    
    return df


def p_each_factor(model):
    
    p_12 = []       # original-globalrev;   66Hz-75Hz
    p_13 = []       # original-localrev;    66Hz-85Hz
    p_23 = []       # localrev-globalrev;   75Hz-85Hz

    for tw in model.keys():
        # print(key)
        window = model[tw][0]
        
        p_12 = np.append(p_12, window[0])        
        p_13 = np.append(p_13, window[1])       
        p_23 = np.append(p_23, window[2])        
        
    return p_12, p_13, p_23



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from collections import Counter
from pathlib import Path
import os


directory =  Path('G:/Final_exps_spikes/LFP/Elfie/p1/p1_15/')
directory_ttest = Path(str(directory) + '/significance_tests/ttest/')
directory_downsizedonsets = Path(str(directory) + '/donwsampled_onset_responses/')
savehere = Path('G:/Final_exps_spikes/LFP/Elfie/p1/p1_15/plots/')

save_loc = str(savehere) + '/maineffect_significance_plots'
if not os.path.exists(save_loc):     # if the required folder does not exist, create one
    os.mkdir(save_loc)
    

timewindows = ['tw1', 'tw2', 'tw3', 'tw4','tw5','tw6','tw7','tw8','tw9','tw10','tw11','tw12']

'''p-VALUE dataframes'''
# order effect
p_o12_df = pd.DataFrame(columns=timewindows)
p_o13_df = pd.DataFrame(columns=timewindows)
p_o23_df = pd.DataFrame(columns=timewindows)

# speed effect
p_s12_df = pd.DataFrame(columns=timewindows)
p_s13_df = pd.DataFrame(columns=timewindows)
p_s23_df = pd.DataFrame(columns=timewindows)



# get probe info
probe_locs = load_probe()

for chan in range(1,385):
    
    channel_num = chan

    # checking one channel to get associated pvalues (output from lfp_ttest.py)
    with open(str(directory_ttest) + '/channel' + str(chan) + '_mainEffect.pkl', 'rb') as file:
        loaded_model_pval = pickle.load(file)
        file.close()
        
    ### HEATMAP with pvalue for each pairwise comparison for each factor
    # obtain the p-value for each factor comparison for this channel
    p_o12, p_o13, p_o23 = p_each_factor(loaded_model_pval['main_order'])
    p_s12, p_s13, p_s23 = p_each_factor(loaded_model_pval['main_speed'])
    
    # order effect
    combine_channels(p_o12_df, p_o12, channel_num)
    combine_channels(p_o13_df, p_o13, channel_num)
    combine_channels(p_o23_df, p_o23, channel_num)

    # speed effect
    combine_channels(p_s12_df, p_s12, channel_num)
    combine_channels(p_s13_df, p_s13, channel_num)
    combine_channels(p_s23_df, p_s23, channel_num)
    

'''Data preparation for heatmap'''
# updating the channel order based on electrode depths
p_o12_df = add_depth_info(p_o12_df, probe_locs)
p_o13_df = add_depth_info(p_o13_df, probe_locs)
p_o23_df = add_depth_info(p_o23_df, probe_locs)

p_s12_df = add_depth_info(p_s12_df, probe_locs)
p_s13_df = add_depth_info(p_s13_df, probe_locs)
p_s23_df = add_depth_info(p_s23_df, probe_locs)


# plotting
%matplotlib qt

fig, axs = plt.subplots(nrows=1, ncols=6, sharex=True, figsize=(20, 10))


### HEATMAP 1 : alpha = 0.05/12 = 0.004
sns.heatmap(p_o12_df, cmap="coolwarm", vmax=0.008, vmin=0.0005, ax=axs[0], cbar=False)
axs[0].set_title('Original - Global rev')
axs[0].set_ylabel('Depth')

sns.heatmap(p_o13_df, cmap="coolwarm", vmax=0.008, vmin=0.0005, ax=axs[1], cbar=False, yticklabels=False)
axs[1].set_title('Original - Local rev')

sns.heatmap(p_o23_df, cmap="coolwarm", vmax=0.008, vmin=0.0005, ax=axs[2], cbar=False, yticklabels=False)
axs[2].set_title('Local rev - Global rev')

sns.heatmap(p_s12_df, cmap="coolwarm", vmax=0.008, vmin=0.0005, ax=axs[3], cbar=False, yticklabels=False)
axs[3].set_title('66 - 75Hz')

sns.heatmap(p_s13_df, cmap="coolwarm", vmax=0.008, vmin=0.0005, ax=axs[4], cbar=False, yticklabels=False)
axs[4].set_title('66 - 85Hz')

sns.heatmap(p_s23_df, cmap="coolwarm", vmax=0.008, vmin=0.0005, ax=axs[5], yticklabels=False)
axs[5].set_title('75 - 85Hz')
    
for col in range(6):
    axs[col].invert_yaxis()
    axs[col].axvline(x = 6, color = 'w', linestyle = '--', linewidth = 1)
    axs[col].set_xticks(np.arange(0,15,3), ['-300','-150','0','150','300'], rotation=0)
    axs[col].set_xlabel('Time(in ms)')
    
fig.suptitle('Main effect - Pairwise comparison', fontsize=16)


plt.savefig(str(save_loc) + '/pairwise_significance_maineff_hm.png')
plt.close()
