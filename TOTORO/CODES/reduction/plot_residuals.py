import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse

def plot_residuals(input_file):
    # Load the data
    data = pd.read_csv(input_file, comment='#', delim_whitespace=True, header=None, \
                        names=['0', '1', '2', '3', '4', '5', 'res1', 'res2', 'res3', 'res4', '10', '11', '12', '13', '14'])
    
    # Create the plot
    plt.figure(figsize=(10, 10))
    plt.scatter(data['res1'], data['res2'], s=1, c='black', label='columns 7-8')
    plt.scatter(data['res3'], data['res4'], s=1, c='red', label='columns 9-10')
    plt.axvline(0.0, color='black', linestyle='--', alpha=0.5, linewidth=0.5)
    plt.axhline(0.0, color='black', linestyle='--', alpha=0.5, linewidth=0.5)
    plt.xlabel('Residual 1')
    plt.ylabel('Residual 2')
    plt.legend()
    plt.title('Residuals')

    # Construct output file name
    base_name = os.path.basename(input_file)
    file_parts = base_name.split('.')
    output_file = f"MAT_{file_parts[1]}_res_plot.png"
        
    # Save the plot without showing it
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate residuals plots from MAT files.")
    parser.add_argument("input_files", nargs='+', help="Input file to process")  # Accept multiple files

    # Parse command-line arguments
    args = parser.parse_args()

    # Loop through each input file and generate the plot
    for input_file in args.input_files:
        print(f"Processing file: {input_file}")
        plot_residuals(input_file)

if __name__ == "__main__":
    main()
