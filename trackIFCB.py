# works with Python 2

import pandas as pd
from scipy import interpolate
from glob import glob
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def trackIFCB():
    """ Will prompt for inputs needed. Interpolates locations of IFCB samples
        from the cruise track data.
        Output: will save a csv file in designated location; 1st header line
        with vessel and approximate survey area, start datetime, end datetimes
        for the cruise effort; 2nd header line describes columns
    """
    # takes inputs from user
    trackfile = input('path for cruise track file (.txt)? ')
    ifcbdir = input('path for IFCB directory? ')
    ship = input('vessel name? ')
    location = input('approximate survey area? ')
    output = input('output file path (.csv)? ')

    # get roi files from the IFCB directory; some conditionals to be able to take more inputs
    if ifcbdir[-1] == '/':
        ifcbglob = sorted(glob(ifcbdir + '*.hdr'))
    else:
        ifcbglob = sorted(glob(ifcbdir + '/*.hdr'))

    # parse IFCB files into a dataframe with a datetime index with the corresponding filenames
    ifcbtimes = []
    ifcbfiles = []
    for string in ifcbglob:
        singlefile = string.split('/')[-1]
        ifcbfiles.append(singlefile)
        timestr = singlefile.split('_')[0]
        a = timestr.split('D')[1]
        b = a.split('T')
        c = b[0] + ' ' + b[1].split('_')[0]
        ifcbtimes.append(c) 
    ifcbfiles_df = pd.DataFrame(ifcbfiles)
    ifcbfiles_df = ifcbfiles_df.set_index(pd.DatetimeIndex(ifcbtimes))
    ifcbfiles_df.columns = ['file']

    # parse ship track coordinates into a dataframe with a datetime index and other relevant info (incl. lat and long)
    # requires interpolating the ship track data for every second to exactly match with IFCB file times
    track = pd.read_table(trackfile)
    tracktimes = []
    for item in track['time']:
        tracktimes.append(datetime.strptime(item, '%Y-%m-%d %H:%M:%S'))
    track_df = track.set_index(pd.DatetimeIndex(tracktimes))
    track_upsamp = track_df.resample('1S').asfreq().interpolate(method='linear')

    # loops through the dataframe of IFCB files, taking the time of the file and matching it to the coordinates found ship track dataframe
    lat = []
    long = []
    for n in range(0, np.shape(ifcbfiles_df)[0]):
        searchtime = ifcbfiles_df.index[n]
        if searchtime in track_upsamp.index:
            found = track_upsamp.loc[searchtime]
            lat.append(found['latitude'])
            long.append(found['longitude'])
        else:
            print(searchtime, 'not in cruise track data')

    matchedloc = pd.concat([pd.DataFrame(ifcbfiles), pd.DataFrame(lat), pd.DataFrame(long)], axis=1) # uses ifcbfiles instead of ifcbfiles_df because there is no attached datetime index that would complicate the concatination. Order should be the same though
    hdr_meta = [ship + ' ' + location, tracktimes[0], tracktimes[-1]]  # metadata about this cruise
    hdr = ['ifcbfile', 'latitude', 'longitude']  # actual column names
    matchedloc.columns = pd.MultiIndex.from_tuples(zip(hdr_meta, hdr))
    matchedloc.to_csv(output) #, header=(ship + ' ' + location, tracktimes[0], tracktimes[-1]))
    
    print('Done') 
    return


def mapsamples(file, latmin=40, latmax=48, lonmin=-73, lonmax=-63):
    """ Required input: path to .csv file with IFCB sample coordinates, header
                        should have latitude and longitude in 2nd line
        Default inputs: latmin=40, latmax=48, lonmin=-73, lonmax=-63
        Output: Plots a map of the IFCB sample locations
    """
    samples = pd.read_csv(file, header=[1])
    lat = np.array(samples['latitude'])
    lon = np.array(samples['longitude'])
    m = Basemap(projection='merc', llcrnrlat=latmin, urcrnrlat=latmax, llcrnrlon=lonmin, urcrnrlon=lonmax,resolution='i')
    m.drawcoastlines()
    m.fillcontinents(color='#FFDDCC',lake_color='#DDEEFF')
    m.drawcoastlines()
    m.drawmapboundary(fill_color='#DDEEFF')
    m.drawstates()
    m.drawcountries()
    m.scatter(lon, lat, latlon=True, c='darkgreen', s=3)
    plt.title(file.split('/')[-1].split('.csv')[0])
    plt.show()
    return
