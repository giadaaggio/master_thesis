'''''
To select the data that are good for our analysis we need to get rid of the 
cloud of points in the critical region between the saturation limit and the 
limit for the faint stars. 
To do so the main idea is to divide the critical region in bin, plot the median and the
std for each bin and then select only the values that fall in the region of the median +- the std. 
'''''

import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse

# Suppress all warnings
import warnings
warnings.filterwarnings("ignore")

def filter_data(input_file):
    # Load the data
    data = pd.read_csv(input_file, comment='#', delim_whitespace=True, header=None, names=['x', 'y', 'magnitude', 'qfit'])
    data['qfit'] = data['qfit'].astype(str)
    valid_data = data[data['qfit'] != "*********"]
    valid_data['qfit'] = pd.to_numeric(valid_data['qfit'], errors='coerce')
    # Filter rows where 'qfit' is positive
    qfit_range_data = valid_data[(valid_data['qfit'] >= 0)]

    saturation_limit  = - 13.7
    faint_limit = - 6.5

    # Define the range we are working with 
    qfit_range_data_crit = qfit_range_data[(qfit_range_data['magnitude'] >= saturation_limit)  \
                                       & (qfit_range_data['magnitude'] <= faint_limit)]

    # Define magnitude range and number of zones
    magnitude_min = saturation_limit  # start of the range
    magnitude_max = faint_limit   # end of the range (faint star limit)
    n_zones = 15  # number of zones

    # Define qfit upper limit range
    qfit_min = 0.1  # starting upper limit for qfit
    qfit_max = 0.9  # ending upper limit for qfit

    # Calculate magnitude boundaries and qfit upper limits for each zone
    magnitude_limits = np.geomspace(magnitude_min, magnitude_max, n_zones + 1)
    qfit_limits = np.geomspace(qfit_min, qfit_max, n_zones)

    # Initialize list to store data for each zone
    zone_data = []

    # Iterate over the zones and filter the data
    for i in range(n_zones):
        lower_mag_limit = magnitude_limits[i]
        upper_mag_limit = magnitude_limits[i + 1]
        qfit_limit = qfit_limits[i]

        # Select data for the current zone
        zone = qfit_range_data_crit[(qfit_range_data_crit['magnitude'] > lower_mag_limit) & 
                             (qfit_range_data_crit['magnitude'] <= upper_mag_limit) & 
                             (qfit_range_data_crit['qfit'] <= qfit_limit)]

        # Append the filtered zone data to the list
        zone_data.append(zone)

    # Concatenate the data for all zones
    filtered_data = pd.concat(zone_data)

    # Define the number of bins
    n_bins = 100

    # Create the bins
    bins = np.linspace(saturation_limit, faint_limit, n_bins)

    # Calculate the median and standard deviation of the qfit values for each bin
    medians = []
    stds = []
    for i in range(len(bins) - 1):
        bin_data = filtered_data[(filtered_data['magnitude'] >= bins[i]) & (filtered_data['magnitude'] < bins[i + 1])]
        median = bin_data['qfit'].median()
        std = bin_data['qfit'].std()
        if median >= 0.5:
            bin_data_outlier = bin_data[bin_data['qfit'] < 0.5]
            median = bin_data_outlier['qfit'].median()
            std = bin_data_outlier['qfit'].std()
        medians.append(median)
        stds.append(std)  

    # Remove the points that are outside the range median +- 3*std
    good_data = pd.DataFrame()
    for i in range(len(bins) - 1):
        bin_data = filtered_data[(filtered_data['magnitude'] >= bins[i]) \
                                 & (filtered_data['magnitude'] < bins[i + 1])]
        good_data = pd.concat([good_data, bin_data[(bin_data['qfit'] >= medians[i] - 2 * stds[i]) \
                                                   & (bin_data['qfit'] <= medians[i] + 2 *stds[i])]])

    # Concatenate the selected data with the ones outside the range
    final_data = pd.concat([good_data, qfit_range_data[(qfit_range_data['magnitude'] < saturation_limit)\
                                                        | (qfit_range_data['magnitude'] > faint_limit)]])
    
    # Round the values to the desired number of decimals
    decimals = {'x' : 3, 'y' : 3, 'magnitude' : 4, 'qfit' : 5}
    final_data = final_data.round(decimals)

    # Save the filtered data to a new file
    original_file_path = input_file

    # Extract the base name without extension
    base_name = os.path.splitext(os.path.basename(original_file_path))[0]

    # Create the new file name with 's' before '.xym'
    new_file_name = f"{base_name}_s.xym"

    # Save the DataFrame with the new name
    final_data.to_csv(new_file_name, sep=' ', index=False, header=False)

    return print(f"File saved as: {new_file_name}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Filter data based on qfit and magnitude values.")
    parser.add_argument("input_files", nargs='+', help="List of input files to process")  # Accept multiple files

    # Parse command-line arguments
    args = parser.parse_args()

    # Loop through each input file and generate the plot
    for input_file in args.input_files:
        print(f"Processing file: {input_file}")
        filter_data(input_file)

if __name__ == "__main__":
    main()