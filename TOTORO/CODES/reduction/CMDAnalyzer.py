import matplotlib.pyplot as plt
from matplotlib.widgets import Button, PolygonSelector
from matplotlib.path import Path
import numpy as np
import pandas as pd
import csv

class CMDRegionSelector:
    def __init__(self, data, color, magnitude, color_bound_bin, magnitude_bound_bin, color_bound_prim, magnitude_bound_prim, x_label, y_label, output_file="selected_regions.csv"):
        self.data = data
        self.color = color
        self.magnitude = magnitude
        self.color_bound_bin = color_bound_bin
        self.magnitude_bound_bin = magnitude_bound_bin
        self.color_bound_prim = color_bound_prim
        self.magnitude_bound_prim = magnitude_bound_prim
        self.x_label = x_label
        self.y_label = y_label
        self.output_file = output_file
        self.current_region = None
        self.saved_regions = []
        self.save_button = None  # Ensure button is part of the class instance
        self.selector = None  # This will hold the PolygonSelector
        self.init_plot()

    def save_region(self, event):
        """Save the current region when the button is clicked."""
        print("Save button clicked!")  # Debugging line
        if self.current_region is not None:
            self.saved_regions.append(self.current_region)
            print("Region saved.")
            self.current_region = None
            self.save_to_file()

    def save_to_file(self):
        """Save selected regions to a CSV file."""
        with open(self.output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Region_ID", "X", "Y"])  # Header
            for i, region in enumerate(self.saved_regions):
                for x, y in region:
                    writer.writerow([i, x, y])
        print(f"Regions saved to '{self.output_file}'.")

    def on_select(self, verts):
        """Callback function for PolygonSelector."""
        self.current_region = verts
        print("Polygon completed. Adjust or confirm selection.")

    def init_plot(self):
        """Initialize the CMD plot with interactive selection."""
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.scatter(self.color, self.magnitude, s=0.5, c='black', alpha=0.4, zorder=1)
        self.ax.scatter(self.color_bound_bin, self.magnitude_bound_bin, s=15, c='red', label='boundary', marker='o', zorder=4)
        self.ax.scatter(self.color_bound_prim, self.magnitude_bound_prim, s=15, c='red', marker='o', zorder=4)
        self.ax.invert_yaxis()
        self.ax.set_xlabel(f'{self.x_label}')
        self.ax.set_ylabel(f'{self.y_label}')

        # Create the PolygonSelector
        self.selector = PolygonSelector(self.ax, self.on_select, useblit=True)

        # Create the Save button
        self.create_save_button()

        plt.show(block=True)

    def create_save_button(self):
        """Create a button to save the selected region."""
        button_ax = self.fig.add_axes([0.7, 0.01, 0.1, 0.05])  # Centered button
        self.save_button = Button(button_ax, 'Save')
        self.save_button.on_clicked(self.save_region)
        plt.draw()  # Force redraw to update the button display

    @staticmethod
    def load_regions(file_name):
        """Load saved regions from a CSV file."""
        regions = {}
        try:
            with open(file_name, "r") as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for row in reader:
                    region_id = int(row[0])
                    if region_id not in regions:
                        regions[region_id] = []
                    regions[region_id].append((float(row[1]), float(row[2])))
        except FileNotFoundError:
            print(f"File '{file_name}' not found.")
        return regions
    
    @staticmethod
    def count_stars_in_region(region, colors, mags):
        """Count stars in a region defined by a polygon."""
        path = Path(region)
        points = np.column_stack((colors, mags))
        return np.sum(path.contains_points(points))
    
    def analyze_regions(self, regions_file):
        """Count stars in the loaded regions."""
        regions = self.load_regions(regions_file)
        regions_stars_dict = {'Region_ID': [], 'Stars': []}
        
        for region_id, region in regions.items():
            count = self.count_stars_in_region(region, self.color, self.magnitude)
            regions_stars_dict['Region_ID'].append(region_id)
            regions_stars_dict['Stars'].append(count)
        
        region_count = pd.DataFrame(regions_stars_dict)
        print(region_count)
        return region_count
    


'''
=============================
EXAMPLE USAGE 
=============================

cmd_select_vis = CMDRegionSelector(
    data = data,
    color = data['F606W'] - data['F814W'],
    magnitude = data['F814W'],
    color_bound_bin = bound_bin_vis['F606W'] - bound_bin_vis['F814W'],
    magnitude_bound_bin = bound_bin_vis['F814W'],
    color_bound_prim = bound_ms['F606W'] - bound_ms['F814W'],
    magnitude_bound_prim = bound_ms['F814W'],
    x_label='F606W-F814W',
    y_label='F814W',
    output_file = '/Users/giadaaggio/Desktop/Thesis/TOTORO/FITS/47_Tuc/regions_F606W_F814W.csv'
)

And to count the number of stars in the selected regions:

region_vis_count = cmd_select_vis.analyze_regions('/Users/giadaaggio/Desktop/Thesis/TOTORO/FITS/47_Tuc/regions_F606W_F814W.csv')

'''

class CMDFiducialSelector:
    def __init__(self, data, color, magnitude, x_label='Color', y_label='Magnitude', output_file='fiducial_lines.csv'):
        self.data = data
        self.color = color
        self.magnitude = magnitude
        self.x_label = x_label
        self.y_label = y_label
        self.output_file = output_file
        self.fiducial_points = []
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.cid = None  # Event connection ID
        self.init_plot()

    def init_plot(self):
        """Initialize the CMD plot with interactive selection."""
        self.ax.scatter(self.color, self.magnitude, s=0.5, c='black', alpha=0.4, zorder=1)
        self.ax.invert_yaxis()
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.create_save_button()
        plt.show()

    def on_click(self, event):
        """Capture clicks to select fiducial line points."""
        if event.inaxes == self.ax:
            self.fiducial_points.append((event.xdata, event.ydata))
            self.ax.scatter(event.xdata, event.ydata, c='red', s=20, zorder=2)
            self.fig.canvas.draw()
            print(f'Selected point: ({event.xdata:.3f}, {event.ydata:.3f})')

    def create_save_button(self):
        """Create a button to save the selected fiducial line."""
        button_ax = self.fig.add_axes([0.7, 0.01, 0.1, 0.05])
        save_button = Button(button_ax, 'Save')
        save_button.on_clicked(self.save_fiducial_line)

    def save_fiducial_line(self, event):
        """Save the selected fiducial line points to a CSV file."""
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Color', 'Magnitude'])
            writer.writerows(self.fiducial_points)
        print(f'Fiducial line saved to {self.output_file}')

    @staticmethod
    def load_fiducial_line(file_name):
        """Load fiducial line points from a CSV file."""
        fiducial_points = []
        try:
            with open(file_name, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for row in reader:
                    fiducial_points.append((float(row[0]), float(row[1])))
        except FileNotFoundError:
            print(f'File {file_name} not found.')
        return fiducial_points

