import pandas as pd
from scipy import interpolate
from glob import glob

def trackIFCB():
    """ Will prompt for inputs needed. Interpolates locations of IFCB samples
        from the cruise track data. Output: will save a csv file in designated
        location; header line with vessel and approximate survey area, start
        datetime, end datetimes for the cruise effort; lines are [IFCB filename],
        lat,lon
    """
    # takes inputs from user
    trackfile = input('path for cruise track file (.txt)? ')
    ifcbdir = input('path for IFCB directory? ')
    ship = input('vessel name? ')
    location = input('approximate survey area? ')
    output = input('output file path (.csv)? ')

    # get roi files from the IFCB directory; some conditionals to be able to take more inputs
    if ifcbdir[-1] == '/':
        ifcbglob = sorted(glob(ifcbdir + '*.roi'))
    else:
        ifcbglob = sorted(glob(ifcbdir + '/*.roi'))

    #parse IFCB files into a list of times and a list of filenames
    times = []
    ifcbfiles = []
    for string in ifcbglob:
        singlefile = string.split('/')[-1]
        ifcbfiles.append(singlefile)
        timestr = singlefile.split('_')[0]
        a = timestr.split('D')[1]
        b = a.split('T')
        c = b[0] + ' ' + b[1].split('_')[0]
        times.append(c)
        #will need to make time into actual datetime objects
        #something along mcv_index = mcv_index.set_index(pd.DatetimeIndex(mctimes))

    # interpolate ship track coordinate for the time of a specific IFCB sample
    track = pd.read_table(trackfile)
    track = track.set_index(track['time'])
    #interpolate.interp1d() # match IFCB with track data #idk how this works but x would be IFCBtimes, y would be track data

    tracktimes = list(track['time'])
    #somedf.to_csv(output, header=(ship + ' ' + location, tracktimes[0], tracktimes[-1]) #rename somedf