# Code illustrates how to string multiple runs on RNO-G together and plot
# import necessary packages
import mattak.Dataset
import time
import numpy as np
import argparse
import uproot
import matplotlib.pyplot as plt

# get RNO-G data of first run
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Test mattak.")
    argparser.add_argument('--station', type=int, default=22)       # insert station you want to look at
    argparser.add_argument('--run', type=str, default=1054)         # insert first run you want to look at
    argparser.add_argument('--data_dir', type=str, default=None)
    argparser.add_argument('--backend', nargs='*', help="Which backend(s) to test", default=['uproot'])
    args = argparser.parse_args()

    for backend in args.backend:
        print(f">----- Testing backend: {backend} -----<")
        d = mattak.Dataset.Dataset(
            args.station, args.run, data_path=args.data_dir,
            backend=backend, verbose=True)
        print(d.N())                                                # number of events in run
        # print(d.eventInfo())
        # print(d.wfs())

        d.setEntries((0,500))                                       # number of events the computer will compile, make sure d.setEntries >= d.N()
        # print(d.eventInfo())
        # print(d.wfs())

        mean = 0
        start = time.time()
        for ev in d.iterate():
            mean += np.average(ev[1])

        end = time.time()
        print(mean / d.N())
        print("time:", end - start)
        default_t = np.arange(0, 2048/3.2, 1/3.2)                   # default time
        all_wfs = d.wfs()                                           # waveforms (call with all_wfs[event][channel])

# function to perform FFT, get frequency (GHz), power (db)
def voltfreqplot(t, v):
    v = v-np.mean(v)
    fft = np.fft.fft(v)
    N = len(v)
    freqs = np.fft.fftfreq(len(v), d=t[1]-t[0])
    db = 10.0*np.log10(np.abs(fft[:int(N/2)])**2)                   # convert to decibels (optional, but much more convenient)
    return(freqs[:int(N/2)], db)

# function to calculate average excluding zero rows, use for frequency, not power
def exclude_zeroes(array):
    non_zeroes = array[np.any(array != 0, axis = 1)]
    avg = np.mean(non_zeroes, axis=0)
    return avg

# average the events in the first run by minute
# designate each array (unixtime, secs, mins, M) specifically, i.e. by using '_0' or the run number, etc.
unixtime_1054 = []
secs_1054 = []
for l in d.eventInfo():
    unixtime_1054.append(l.readoutTime)
    secs_1054.append(l.readoutTime - unixtime_1054[0])

mins_1054 = []
M_1054 = []
for j in range(120):
    mins_1054.append([])
    M_1054.append([])
    for i in secs_1054:
        if j*60 <= i < (j+1)*60:
            mins_1054[j].append(i)
    M_1054[j] = [k for k, v in enumerate(secs_1054) if v in mins_1054[j]]

for j in range(120):
    xvals = np.zeros([len(M_1054[j]), 1024])
    yvals = np.zeros([len(M_1054[j]), 1024])
    for i in M_1054[j]:
        xvals[i-M_1054[j][0]], yvals[i-M_1054[j][0]] = voltfreqplot(default_t, all_wfs[i][16])
    xavg = exclude_zeroes(xvals)
    yavg = np.sum(yvals, axis=0) / len(M_1054[j])
    all_xvals_1054 = np.zeros([120, len(xavg)])
    all_yvals_1054 = np.zeros([120, len(yavg)])
# xvals, yvals, xavg, yavg do not need to be separately designated since they are inside a for loop
# all_xvals, all_yvals must be run-specific
for j in range(120):
    xvals = np.zeros([len(M_1054[j]), 1024])
    yvals = np.zeros([len(M_1054[j]), 1024])
    for i in M_1054[j]:
        xvals[i-M_1054[j][0]], yvals[i-M_1054[j][0]] = voltfreqplot(default_t, all_wfs[i][16])
    xavg = exclude_zeroes(xvals)
    yavg = np.sum(yvals, axis=0) / len(M_1054[j])
    if len(M_1054[j]) == 0:
        yavg = 0
    all_xvals_1054[j,:] = [x*1000 for x in xavg]
    all_yvals_1054[j,:] = yavg

# Now the second run
# must copy the code for getting RNO-G data from each run
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Test mattak.")
    argparser.add_argument('--station', type=int, default=22)
    argparser.add_argument('--run', type=str, default=1055)     # changed to next run
    argparser.add_argument('--data_dir', type=str, default=None)
    argparser.add_argument('--backend', nargs='*', help="Which backend(s) to test", default=['uproot'])
    args = argparser.parse_args()

    for backend in args.backend:
        print(f">----- Testing backend: {backend} -----<")
        d = mattak.Dataset.Dataset(
            args.station, args.run, data_path=args.data_dir,
            backend=backend, verbose=True)
        print(d.N())
        # print(d.eventInfo())
        # print(d.wfs())

        d.setEntries((0,500))
        # print(d.eventInfo())
        # print(d.wfs())

        mean = 0
        start = time.time()
        for ev in d.iterate():
            mean += np.average(ev[1])

        end = time.time()
        print(mean / d.N())
        print("time:", end - start)
        default_t = np.arange(0, 2048/3.2, 1/3.2)
        all_wfs = d.wfs()

# define values for second run
unixtime_1055 = []
secs_1055 = []
for l in d.eventInfo():
    unixtime_1055.append(l.readoutTime)
    secs_1055.append(l.readoutTime - unixtime_1055[0])

mins_1055 = []
M_1055 = []
for j in range(120):
    mins_1055.append([])
    M_1055.append([])
    for i in secs_1055:
        if j*60 <= i < (j+1)*60:
            mins_1055[j].append(i)
    M_1055[j] = [k for k, v in enumerate(secs_1055) if v in mins_1055[j]]

for j in range(120):
    xvals = np.zeros([len(M_1055[j]), 1024])
    yvals = np.zeros([len(M_1055[j]), 1024])
    for i in M_1055[j]:
        xvals[i-M_1055[j][0]], yvals[i-M_1055[j][0]] = voltfreqplot(default_t, all_wfs[i][16])
    xavg = exclude_zeroes(xvals)
    yavg = np.sum(yvals, axis=0) / len(M_1055[j])
    all_xvals_1055 = np.zeros([120, len(xavg)])
    all_yvals_1055 = np.zeros([120, len(yavg)])
for j in range(120):
    xvals = np.zeros([len(M_1055[j]), 1024])
    yvals = np.zeros([len(M_1055[j]), 1024])
    for i in M_1055[j]:
        xvals[i-M_1055[j][0]], yvals[i-M_1055[j][0]] = voltfreqplot(default_t, all_wfs[i][16])
    xavg = exclude_zeroes(xvals)
    yavg = np.sum(yvals, axis=0) / len(M_1055[j])
    if len(M_1055[j]) == 0:
        yavg = 0
    all_xvals_1055[j,:] = [x*1000 for x in xavg]
    all_yvals_1055[j,:] = yavg

# use np.concatenate() to combine frequency, power arrays into one array
all_xvals = np.concatenate((all_xvals_1054, all_xvals_1055), axis=0)            # axis = 0 will append them to each other on the time axis (which is what we want)
all_yvals = np.concatenate((all_yvals_1054, all_yvals_1055), axis=0)

# plot
fig, axs = plt.subplots(1, figsize = (45, 40))
pos = axs.imshow(np.swapaxes(all_yvals, 0, 1), extent=[0, 240, all_xvals[0][-1], all_xvals[0][0], all_yvals.shape[0]],
cmap='viridis')
cbar = fig.colorbar(pos, ax=axs)
axs.set_aspect('auto')
plt.title('Multiple Runs - Station 22 Ch16 Runs 1054-1055', fontsize = 50)
plt.xlabel('Time (Minutes)', fontsize = 40)
plt.ylabel('Frequency (MHz)', fontsize = 40)
plt.xticks(fontsize = 35)
plt.yticks(fontsize = 35)
cbar.ax.tick_params(labelsize = 35)
plt.ylim([0, np.max(all_xvals[0])])
plt.savefig('MultiRun.pdf')