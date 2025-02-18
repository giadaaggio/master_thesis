
'''
================================================================================
                    Binary Star System Utilities
================================================================================

This module contains utility functions for working with binary star systems.
The main functions are:
    - binary_system_HB: Generate a DataFrame with magnitudes of binary systems in which one of the members of the binary is a 
     HB star for multiple primary stars and two selected filters.
    - binary_system_general: Generate a DataFrame with magnitudes of binary systems for multiple primary stars and two selected filters.
    - color_index_noncalibrated: Generate color indices for a DataFrame based on the secondary star indices, ensuring HB stars have lighter colors.
    Suited for non-calibrated magnitudes.
    - color_index: Generate color indices for a DataFrame based on the secondary star indices. Suited for calibrated magnitudes.

================================================================================
'''


class BinaryStarUtils:
    @staticmethod
    def binary_system_HB(df, primary_indices, filter1, filter2, source_column='source', hb_label='HB_test_stars'):
        """
        Generate a DataFrame with magnitudes of binary systems for multiple primary stars and two selected filters.

        Parameters:
            df (pd.DataFrame): DataFrame containing stars with magnitudes in different filters.
            primary_indices (list[int]): List of indices for the chosen primary stars in the DataFrame.
            filter1 (str): The name of the first filter column.
            filter2 (str): The name of the second filter column.
            source_column (str): Column name identifying the source of the stars. Default is 'source'.
            hb_label (str): Label identifying horizontal branch stars in the source column. Default is 'HB_test_stars'.

        Returns:
            pd.DataFrame: A new DataFrame containing binary system magnitudes, primary and secondary star indices.
        """
        
        # Check if the primary stars are labeled as HB stars
        for star_index in primary_indices:
            if df.loc[star_index, source_column] != hb_label:
                raise ValueError(f"Star at index {star_index} is not labeled as an HB star.")

        # List to store results
        results = []

        for star_index in primary_indices:
            # Extract primary magnitudes
            mag1_p = df.loc[star_index, filter1]
            mag2_p = df.loc[star_index, filter2]

            # Compute binary magnitudes using vectorized operations
            mag1_bin = -2.5 * np.log10(10 ** (-mag1_p / 2.5) + 10 ** (-df[filter1] / 2.5))
            mag2_bin = -2.5 * np.log10(10 ** (-mag2_p / 2.5) + 10 ** (-df[filter2] / 2.5))

            # Create a temporary DataFrame for this primary
            temp_df = pd.DataFrame({
                "primary": star_index,  # Add primary star index
                "secondary": df.index,  # Add secondary star indices
                filter1: mag1_bin,
                filter2: mag2_bin
            })

            # Append to results
            results.append(temp_df)

        # Concatenate all results into a single DataFrame
        result_df = pd.concat(results, ignore_index=True)

        return result_df


    @staticmethod
    def binary_system_general(df, primary_indices, filter1, filter2):
        """
        Generate a DataFrame with magnitudes of binary systems for multiple primary stars and two selected filters.

        Parameters:
            df (pd.DataFrame): DataFrame containing stars with magnitudes in different filters.
            primary_indices (list[int]): List of indices for the chosen primary stars in the DataFrame.
            filter1 (str): The name of the first filter column.
            filter2 (str): The name of the second filter column.
            source_column (str): Column name identifying the source of the stars. Default is 'source'.
            hb_label (str): Label identifying horizontal branch stars in the source column. Default is 'HB_test_stars'.

        Returns:
            pd.DataFrame: A new DataFrame containing binary system magnitudes, primary and secondary star indices.
        """
        # Validate primary indices
        if not all(0 <= idx < len(df) for idx in primary_indices):
            raise ValueError("One or more primary indices are out of bounds for the DataFrame.")

        # List to store results
        results = []

        for star_index in primary_indices:
            # Extract primary magnitudes
            mag1_p = df.loc[star_index, filter1]
            mag2_p = df.loc[star_index, filter2]

            # Compute binary magnitudes using vectorized operations
            mag1_bin = -2.5 * np.log10(10 ** (-mag1_p / 2.5) + 10 ** (-df[filter1] / 2.5))
            mag2_bin = -2.5 * np.log10(10 ** (-mag2_p / 2.5) + 10 ** (-df[filter2] / 2.5))

            # Create a temporary DataFrame for this primary
            temp_df = pd.DataFrame({
                "primary": star_index,  # Add primary star index
                "secondary": df.index,  # Add secondary star indices
                filter1: mag1_bin,
                filter2: mag2_bin
            })

            # Append to results
            results.append(temp_df)

        # Concatenate all results into a single DataFrame
        result_df = pd.concat(results, ignore_index=True)

        return result_df
    
    # if working with instrumental magnitudes use this function
    @staticmethod
    def color_index_noncalibrated(df, column, colormap=plt.cm.viridis, dark_fraction=0.9, non_calibrated=False):
        """
        Generate color indices for a DataFrame based on the secondary star indices, ensuring HB stars have lighter colors.

        Parameters:
            df (pd.DataFrame): DataFrame containing a column with values to map to colors.
            column (str): The name of the column to compute the color index.
            colormap (matplotlib colormap): The colormap to use for mapping values.
            dark_fraction (float): Fraction of the colormap to use, starting from the darker end (default 0.9).
            calibration (bool): If True, applies different color mapping for HB test stars.

        Returns:
            list: A list of colors mapped from a subset of the colormap.
        """
        norm = pd.Series(dtype=float, index=df.index)  # Initialize empty series for normalized values

        if non_calibrated==True:
             # Identify HB stars
            hb_mask = df["source"].str.contains("HB_test_stars", na=False)  # True for HB stars, False otherwise
            other_mask = ~hb_mask  # Non-HB stars

            # Standard normalization for HB stars (light colors)
            norm[hb_mask] = (df.loc[hb_mask, column] - df[column].min()) / (df[column].max() - df[column].min())

            # Inverted normalization for non-HB stars (darker colors)
            norm[other_mask] = (df[column].max() - df.loc[other_mask, column]) / (df[column].max() - df[column].min())
        else:
            # Standard normalization for all stars
            norm = 1 - (df[column] - df[column].min()) / (df[column].max() - df[column].min())

        # Scale norm to use only the lower fraction of the colormap
        norm = norm * dark_fraction  

        # Apply colormap
        colors = norm.map(colormap)

        return colors
    
    # if working with calibrated magnitudes use this function
    @staticmethod
    def color_index(df, column, colormap = plt.cm.viridis, dark_fraction=0.9, calibration=True):
        """
        Generate color indices for a DataFrame based on the secondary star indices, using only darker colors.

        Parameters:
            df (pd.DataFrame): DataFrame containing a column with values to map to colors.
            column (str): The name of the column to compute the color index.
            dark_fraction (float): Fraction of the colormap to use, starting from the darker end (default 0.5).

        Returns:
            list: A list of colors mapped from a subset of the colormap.
        """
        if calibration == False:
            if "HB_test_stars" in df["source"].values:
                norm = 1 - (df[column] - df[column].min()) / (df[column].max() - df[column].min())
            else:
                norm = 1 - (df[column].max() - df[column]) / (df[column].max() - df[column].min())
        else:
            norm = (df[column] - df[column].min()) / (df[column].max() - df[column].min())

            

        # Scale norm to use only the lower fraction of the colormap
        norm = norm * dark_fraction  # Compress the values to the first `dark_fraction` of the colormap

        colors = norm.map(colormap)

        return colors
