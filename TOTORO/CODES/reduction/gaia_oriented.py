import pandas as pd
import os
import argparse

# Suppress all warnings
import warnings
warnings.filterwarnings("ignore")

def filter_data(input_file):
    # Load the data
    data = pd.read_csv(input_file, header=None, delim_whitespace=True, \
                    usecols=[2, 3, 4, 5, 6, 15], names=['dx', 'dy', 'x', 'y', 'F814W', 'F225W'])
    data['dx'] = pd.to_numeric(data['dx'], errors='coerce')
    data['dy'] = pd.to_numeric(data['dy'], errors='coerce')

    # Drop rows with NaN values
    data = data.dropna()

    # Add a column with dr to identify the stars that are mismatched
    data['dr'] = (data['dx']**2 + data['dy']**2)**0.5
    # Filter rows where 'dr' is less than 0.5
    valid_data = data[(data['dr'] < 0.5)]

    # Round the values to the desired number of decimals
    decimals = {'x' : 3, 'y' : 3, 'F225W' : 4}
    valid_data = valid_data.round(decimals)

    # Create a new file with x y and F225W for the stars that are matched
    valid_data[['x', 'y', 'F225W']].to_csv('FINAL_MASTER.xym', sep=' ', index=False, header=False)  

    return print('Data filtered and saved as FINAL_MASTER.xym')

def main():
    # Set up parser
    parser = argparse.ArgumentParser(description='Filter the data')
    parser.add_argument('input_file', type=str, help='Input file with the data')
    args = parser.parse_args()

    filter_data(args.input_file)

if __name__ == '__main__':
    main()