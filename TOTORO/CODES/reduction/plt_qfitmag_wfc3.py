import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

def plot_qfit_vs_magnitude(input_file, plot_title):
    # Load the data
    data = pd.read_csv(input_file, comment='#', delim_whitespace=True, header=None, names=['x', 'y', 'magnitude', 'qfit', 'nan'])

    # Check if the necessary columns are present
    if 'magnitude' not in data.columns or 'qfit' not in data.columns:
        print(f"The input data in {input_file} must contain 'magnitude' and 'qfit' columns.")
        return

    # Convert 'qfit' column to string to handle non-numeric values like "*********"
    data['qfit'] = data['qfit'].astype(str)

    # Filter out rows where 'qfit' is "*********"
    filtered_data = data[data['qfit'] != "*********"]

    # Convert 'qfit' back to numeric values (invalid parsing will be set to NaN)
    filtered_data['qfit'] = pd.to_numeric(filtered_data['qfit'], errors='coerce')

    # Keep only rows where 'qfit' is between 0 and 1 (inclusive)
    qfit_range_data = filtered_data[(filtered_data['qfit'] >= 0)]

    # Create the plot using the filtered subset
    plt.figure(figsize=(10, 6))
    plt.scatter(qfit_range_data['magnitude'], qfit_range_data['qfit'], color='black', alpha=0.5, s=0.5)
    plt.xlabel('Magnitude')
    plt.ylabel('qfit')
    plt.xlim(-20, -5)
    plt.ylim(-0.1, 1)
    plt.title(f'qfit vs Magnitude - {plot_title}')  # Include the title and filename

# Construct output file name
    output_file = os.path.splitext(input_file)[0] + '_qfit_plot.png'
        
    # Save the plot without showing it
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate qfit vs Magnitude plots from multiple input files.")
    parser.add_argument("input_files", nargs='+', help="List of input files to process")  # Accept multiple files
    parser.add_argument("-t", "--title", type=str, default="Custom Plot", help="Title for the plots")

    # Parse command-line arguments
    args = parser.parse_args()

    # Loop through each input file and generate the plot
    for input_file in args.input_files:
        print(f"Processing file: {input_file}")
        plot_qfit_vs_magnitude(input_file, args.title)

if __name__ == "__main__":
    main()
