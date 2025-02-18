'''
======================================================
                    CMD ANALYZER
======================================================

This module contains classes to interactively select regions and fiducial lines in a Color-Magnitude Diagram (CMD) plot.
The main classes and functions are:
    - CMDRegionSelector: Class to select regions in a CMD plot.
    - CMDFiducialSelector: Class to select fiducial lines in a CMD plot.

The CMDRegionSelector class allows the user to interactively select regions in a CMD plot using a PolygonSelector tool.
The selected regions can be saved to a CSV file, and the number of stars in each region can be counted.

The CMDFiducialSelector class allows the user to interactively select fiducial lines in a CMD plot by clicking on the plot.
The selected fiducial line points can be saved to a CSV file for further analysis.

'''

class CMDRegionSelector:
    def __init__(self, data, color, magnitude, color_bound_bin_high=None, magnitude_bound_bin_high=None, color_bound_bin_low=None, magnitude_bound_bin_low=None, x_label=None, y_label=None, output_file="selected_regions.csv"):
        self.data = data
        self.color = color
        self.magnitude = magnitude
        self.color_bound_bin = color_bound_bin_high
        self.magnitude_bound_bin = magnitude_bound_bin_high
        self.color_bound_bin_low = color_bound_bin_low
        self.magnitude_bound_bin_low = magnitude_bound_bin_low
        self.x_label = x_label
        self.y_label = y_label
        self.output_file = output_file
        self.current_region = None
        self.saved_regions = []
        self.save_button = None
        self.selector = None
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
        self.ax.scatter(self.color_bound_bin_low, self.magnitude_bound_bin_low, s=15, c='red', marker='o', zorder=4)
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

    @staticmethod
    def get_stars_inside_region(region_id, data, color, magnitude, regions_file):
        """
        Extracts stars that fall inside a given region in the CMD.
        
        Parameters:
        - region_id (int): The ID of the region to extract stars from.
        - data (pd.DataFrame): DataFrame containing star catalog with color and magnitude.
        - color_col (str): Column name for the color index (e.g., 'F606W-F814W').
        - mag_col (str): Column name for the magnitude (e.g., 'F814W').
        - regions_file (str): Path to the CSV file with saved regions.
        
        Returns:
        - pd.DataFrame: DataFrame containing only the stars inside the selected region.
        """
        # Load saved regions
        regions = pd.read_csv(regions_file)

        # Extract the selected region
        selected_region = regions[regions["Region_ID"] == region_id]

        if selected_region.empty:
            print(f"Region {region_id} not found.")
            return None

        # Convert region coordinates into a polygon
        polygon_vertices = np.column_stack((selected_region["X"], selected_region["Y"]))
        region_path = Path(polygon_vertices)

        # Get star positions
        star_positions = np.column_stack((color, magnitude))

        # Create a mask for stars inside the region
        inside_mask = region_path.contains_points(star_positions)

        # Return a DataFrame of stars inside the region
        return data[inside_mask]

    


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
    color_bound_bin_low = bound_ms['F606W'] - bound_ms['F814W'],
    magnitude_bound_bin_low = bound_ms['F814W'],
    x_label='F606W-F814W',
    y_label='F814W',
    output_file = '/Users/giadaaggio/Desktop/Thesis/TOTORO/FITS/47_Tuc/regions_F606W_F814W.csv'
)

And to count the number of stars in the selected regions:

region_vis_count = cmd_select_vis.analyze_regions('/Users/giadaaggio/Desktop/Thesis/TOTORO/FITS/47_Tuc/regions_F606W_F814W.csv')

'''

class CMDFiducialSelector:
    def __init__(self, data, color, magnitude, x_label=None, y_label=None, output_file='fiducial_lines.csv', xlim=None, ylim=None, invert_yaxis=True):
        self.data = data
        self.color = color
        self.magnitude = magnitude
        self.x_label = x_label
        self.y_label = y_label
        self.output_file = output_file
        self.xlim = xlim
        self.ylim = ylim
        self.invert_yaxis = invert_yaxis
        self.fiducial_points = []
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.cid = None  # Event connection ID
        self.init_plot()

    def init_plot(self):
        """Initialize the CMD plot with interactive selection."""
        self.ax.scatter(self.color, self.magnitude, s=1, c='black', alpha=0.4, zorder=1)
        
        if self.xlim:
            self.ax.set_xlim(self.xlim)
        if self.ylim:
            self.ax.set_ylim(self.ylim)
        
        if self.invert_yaxis:
            self.ax.invert_yaxis()
        
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.create_save_button()
        plt.show(block=True)

    def on_click(self, event):
        """Capture clicks to select fiducial line points."""
        if event.inaxes == self.ax:
            self.fiducial_points.append((event.xdata, event.ydata))
            self.ax.scatter(event.xdata, event.ydata, c='red', s=20, zorder=2)
            if len(self.fiducial_points) > 1:
                x_vals, y_vals = zip(*self.fiducial_points)
                self.ax.plot(x_vals, y_vals, c='red', linestyle='-', linewidth=1, zorder=2)
            self.fig.canvas.draw()
            print(f'Selected point: ({event.xdata:.3f}, {event.ydata:.3f})')

    def create_save_button(self):
        """Create a button to save the selected fiducial line."""
        button_ax = self.fig.add_axes([0.7, 0.01, 0.1, 0.05])
        self.save_button = Button(button_ax, 'Save')
        self.save_button.on_clicked(self.save_fiducial_line)

    def save_fiducial_line(self, event):
        """Save the selected fiducial line points to a CSV file."""
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['X', 'Y'])
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
