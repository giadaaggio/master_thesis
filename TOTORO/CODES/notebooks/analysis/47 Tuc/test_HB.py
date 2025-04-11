hb_stars = pd.read_csv('/Users/giadaaggio/Desktop/Thesis/TOTORO/FITS/47_Tuc/HB_435_814.csv')
test_stars_HB = pd.read_csv('/Users/giadaaggio/Desktop/Thesis/TOTORO/FITS/47_Tuc/test_stars_HB.csv')

mags_hb = [13.16, 13.14, 13.12]
x_val = hb_stars['x']
y_val = hb_stars['y']

# interpolate
interp_func = interp1d(y_val, x_val, kind='linear', fill_value='extrapolate')
colors_hb = interp_func(mags_hb)

mags_hb_2 = colors_hb + mags_hb

test_stars_HB['F435W'] = mags_hb_2

test_stars_HB.to_csv('/Users/giadaaggio/Desktop/Thesis/TOTORO/FITS/47_Tuc/test_stars_HB.csv', index=False, float_format='%.4f')