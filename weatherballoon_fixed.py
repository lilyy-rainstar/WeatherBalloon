# import necessary packages
import mattak.Dataset
import time
import numpy as np
import argparse
import uproot
import matplotlib.pyplot as plt
import gpxpy
import gpxpy.gpx
import gzip
import pandas as pd
import math

# Active stations: 11 - Nanoq, 12 - Terianniaq, 13 - Ukaleq, 14 - Tuttu, 21 - Amaroq, 22 - Avinngaq, 23 - Ukaliatsiaq, 24 - Qappik

# PLOTTING COORDINATES
# Read RNO-G station data
# useful for ID-ing stations, seeing which ones are active, etc.
stations = pd.read_csv('rnogstations.txt')

# get weather balloon coordinates
gpxcoordinates = [] # <-- empty array to store balloon coordinates
times = []          # <--- empty array to store times
# I believe in you
# Unzip gpx.gz file and extract coordinates
gpx_file = gzip.open('SMT_YYYYMMDD_HRMNSC.gpx.gz', 'rb')  # <-- replace 'YYYYMMDD' with date and "HRMNSC' with time
gpx = gpxpy.parse(gpx_file)
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # print(f'({point.latitude}, {point.longitude})')
            latlong = (point.latitude, point.longitude)
            gpxcoordinates.append(latlong)                     # get coordinates and append them to list 'gpxcoordinates'
            times.append(point.time)                           # get times and append them to 'times'
print(times[0], times[-1])                                     # print timespan of weather balloon data

# get RNO-G station coordinates
rnogcoordinates = []
for i in range(35):
    rnoglatlong = (stations['latitude'][i], stations['longitude'][i])
    rnogcoordinates.append(rnoglatlong)

# Uncomment code below to plot weather balloon path over RNO-G to see if balloon crosses any stations
fig, axs = plt.subplots(1, figsize = (45, 40))
for i, j in gpxcoordinates:
    plt.plot(j, i, 'or')
for m, n in rnogcoordinates:
    plt.plot(n, m, 'ok')
axs.set_title('Coordinate Map', fontsize = 45)
plt.xticks(fontsize = 35)
plt.yticks(fontsize = 35)
# plt.ylim([72.5, 72.7])
# plt.xlim([-38.6, -38.42])
#plt.savefig('WeatherBalloon.pdf')

# FINDING RUNS
# Event information from RNO-G
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Test mattak.")
    argparser.add_argument('--station', type=int, default=00)   # change default to station you want to look at
    argparser.add_argument('--run', type=int, default=00)     # change default to run you want to look at
    argparser.add_argument('--data_dir', type=str, default=None)
    argparser.add_argument('--backend', nargs='*', help="Which backend(s) to test", default=['uproot'])
    args = argparser.parse_args()

    for backend in args.backend:
        print(f">----- Testing backend: {backend} -----<")
        d = mattak.Dataset.Dataset(
            args.station, args.run, data_path=args.data_dir,
            backend=backend, verbose=True)
        print(d.N())                                      # number of events in run
        # print(d.eventInfo())
        # print(d.wfs())

        d.setEntries((0,500))                             # number of events computer will compile, make sure d.setEntries() >= d.N() or you will lose events
        # print(d.eventInfo())
        # print(d.wfs())

        mean = 0
        start = time.time()
        for ev in d.iterate():
            mean += np.average(ev[1])

        end = time.time()
        # print(mean / d.N())
        # print("time:", end - start)
        default_t = np.arange(0, 2048/3.2, 1/3.2)          # default time
        all_wfs = d.wfs()                                  # waveforms (call with all_wfs[event][channel])

def voltfreqplot(t, v):                                    # function to perform fft to get frequency (GHz), power (db)
    v = v-np.mean(v)
    fft = np.fft.fft(v)
    N = len(v)
    freqs = np.fft.fftfreq(len(v), d=t[1]-t[0])
    db = 10.0*np.log10(np.abs(fft[:int(N/2)])**2)          # convert to decibels
    return(freqs[:int(N/2)], db)

def exclude_zeroes(array):                                 # function to calculate average excluding zero rows (use for frequencies, do NOT use for power)
    non_zeroes = array[np.any(array != 0, axis = 1)]
    avg = np.mean(non_zeroes, axis=0)
    return avg

# get times of events
unixtime = []                                               # empty list to store universal time
secs = []                                                   # empty list to store time starting at 0.0 secs
for l in d.eventInfo():
    unixtime.append(l.readoutTime)                          # append universal time to unixtime
    secs.append(l.readoutTime - unixtime[0])                # subtract first universal time from all times, append to secs
print(unixtime[0], unixtime[-1])                          # for finding the time of the run
print(secs[0], secs[-1])                                  # for determining how many minutes are in the run (secs[-1] / 60 = total mins)

# OPTIONAL: plot freq vs. power to verify spike at 0.403 GHz
events = d.N()
print(events)
# fig, axs = plt.subplots(1, figsize = (45, 40))
# for i in range(events):                                   
    # xvals, yvals = voltfreqplot(default_t, all_wfs[i][16])
    # plt.plot(xvals, yvals, linewidth = 4)
# plt.xticks(fontsize = 35)
# plt.yticks(fontsize = 35)
# plt.savfig('WeatherBalloon.pdf')

# SORTING BY MINUTE
mins = []                                                   # empty list to store times of each event per minute
M = []                                                      # empty list to store index of each event per minute
mins_total = math.ceil(secs[-1] / 60)
for j in range(mins_total):                                        # j in range(total minutes)
    mins.append([])                                         # append empty list to mins for each minute
    M.append([])                                            # append empty list to M for each minute
    for i in secs:
        if j*60 <= i < (j+1)*60:                            # sort by minute
            mins[j].append(i)                               # append times to corresponding list in 'mins 
    M[j] = [k for k, v in enumerate(secs) if v in mins[j]]  # append index to corresponding list in 'M'

# AVERAGING FREQUENCY AND POWER PER MINUTE
for j in range(mins_total):
    xvals = np.zeros([len(M[j]), 1024])                     # create empty arrays for frequency (xvals) and power (yvals)
    yvals = np.zeros([len(M[j]), 1024])
    for i in M[j]:
        xvals[i-M[j][0]], yvals[i-M[j][0]] = voltfreqplot(default_t, all_wfs[i][16])    # get frequency, power, for each event per minute
    xavg = exclude_zeroes(xvals)                            # average frequency excluding empty minutes
    yavg = np.sum(yvals, axis=0) / len(M[j])                # average power
    all_xvals = np.zeros([mins_total, len(xavg)])                  # empty array to store frequencies per minute in run
    all_yvals = np.zeros([mins_total, len(yavg)])                  # empty array to store powers per minute in run
for j in range(mins_total):
    xvals = np.zeros([len(M[j]), 1024])
    yvals = np.zeros([len(M[j]), 1024])
    for i in M[j]:
        xvals[i-M[j][0]], yvals[i-M[j][0]] = voltfreqplot(default_t, all_wfs[i][16])
    xavg = exclude_zeroes(xvals)
    yavg = np.sum(yvals, axis=0) / len(M[j])
    if len(M[j]) == 0:                                      # account for empty minutes
        yavg = 0
    all_xvals[j,:] = [x*1000 for x in xavg]                 # append average frequencies (converted to MHz) of each minute to all_xvals
    all_yvals[j,:] = yavg                                   # append average power of each minute to all_yvals

# CREATING THE SPECTROGRAM
fig, axs = plt.subplots(1, figsize = (45, 40))
pos = axs.imshow(np.swapaxes(all_yvals, 0, 1),
    extent=[0, 120, all_xvals[0][-1], all_xvals[0][0], all_yvals.shape[0]], 
    cmap='viridis')                                         # assign color axis to power array, x-axis = time, y = freq, color = power
cbar = fig.colorbar(pos, ax=axs)                            # display color bar
axs.set_aspect('auto')                                      # makes plot viewable

# plot characteristics
plt.title('Jul 20 2022 - Station 21 Ch16 Run 1365', fontsize = 50)
plt.xlabel('Time (Minutes)', fontsize = 45)
plt.ylabel('Frequency (MHz)', fontsize = 45)
plt.xticks(fontsize = 35)
plt.yticks(fontsize = 35)
cbar.ax.tick_params(labelsize = 35)
plt.ylim([0, np.max(all_xvals[0])])

# save figure
plt.savefig('WeatherBalloon.pdf')                            # save figure as pdf