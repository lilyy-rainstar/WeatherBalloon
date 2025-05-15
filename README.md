# WeatherBalloon
Python files for finding weather balloons on RNO-G
INTRODUCTION:

What is this code looking for?
    This folder contains two Python files: one that holds the code for locating weather balloons on RNO-G by creating time vs. frequency vs.
power plots, and one that demonstrates how to string multiple RNO-G runs together on the same plot as if they were one run. Weather balloon signals
are expected to appear at higher-decibels (80 - 100 db) around 400 MHz (or 0.4 GHz). Occasionally the signal will be fainter (down to 68 db or so)
or stronger (> 100 db).

What does this code do?
    The weatherballoon_fixed.py code uses imported data of waveforms recorded on active RNO-G stations (stations 11, 12, 13, 14, 21, 22, 23, 24). 
Each waveform is recorded per event in the RNO-G run (for example, if there were 100 recorded events in a run, there would be 100 waveforms). The 
times of these waveforms are also recorded in unix time. These events are then sorted into minutes and put through a function that performs an FFT 
on them via an numpy function. The function then uses this FFT to get the frequencies in GHz in the waveform and power in decibels of each frequency
for each event. These are returns as arrays, which are then averaged per minute to get one array of frequencies and their powers per minute. The 
frequency vs. time is then plotted, with power in db on the color axis. If weather balloon signals are present in the data, a high-decibel signal 
will be picked up and shown at around 400 MHz on the plot.
    The multirun.py code demonstrates how to string multiple runs back to back on the same plot, in case it is ever needed.

NECESSARY PACKAGES

    weatherballoon_fixed.py employs many, many packages. The package mattak.Dataset is a module that contains the information stored on RNO-G, and 
the time package gets the default time from the datasest (this is important for performing the FFT). numpy is also included for numerical 
evaluations. argparse is for parsing RNO-G arguments such as the run and station. uproot is for reading ROOT files, and matplotlib.pyplot is needed 
for making plots. gpxpy, gpxpy.gpx, and gzip are for unzipping and reading the .gpx.gz files containing weather balloon coordinates. pandas is for 
reading in the RNO-G station information, and math is for one operation that rounds the number of minutes up to the next integer.

PLOTTING COORDINATES

Where do you start?
    Open weatherballoon_fixed.py.
    Included in this folder is the .txt file "rnogstations.txt" in it, and the code uploads this as a pandas data frame to get the 
coordinates of each station.
    The easiest way to find weather balloon candidates is not to start making spectrograms randomly but to instead check weather balloon paths.
These are available at https://rno-g.uchicago.edu/data/sonde/, accessible with the username "rno-g-alt" and the password "100PeVvsATSummitStation".
Enter the folder "gpx/" and you will see a collection of .gpx.gz files. These contain the paths of weather balloons on different days. The files
are titled "SMT_YYYYMMDD_HRMNSC". The "YYYYMMDD" is the date the balloon was launched and the "HRMNSEC" is the time of launch (ex. a file named
"SMT_20220610_111504" would track a balloon launched on June 10th, 2022, at 11:15:04 AM. The times will be on a 24-hour clock, so 11:00 PM will be 
23:00). Choose a file to download (download by clicking on it) and upload it to whatever directory you are in.
    The next step is to unzip the .gpx.gz file. There is already code written for this. All you have to do is replace the file name in Line 25
("gpx_file = gzip.open('SMT_YYYYMMDD_HRMNSC.gpx.gz', 'rb')) with the .gpx.gz file you want to look at. The rest of the code until Line 33 unzips
the file, appends the coordinates of the weather balloon path into the list "gpxcoordinates" and the time each coordinate was recorded into the list
"times". It then prints the first and last element of "times" to get the time interval that the weather balloon was tracked.
    The file appends the latitude and longitude coordinates in rnogstations.txt and appends them to a list called "rnogcoordinates". These
coordinates are then plotted on the same graph to create a map of the weather balloon path over the RNO-G array. Using 
this map: https://rno-g.github.io/station-map/ to determine which station is which, you can decide if the weather balloon in the .gpx.gz file
tracks a balloon that could possibly be seen on any RNO-G stations. The station ID's are also stored in rnogstations.txt, and you can use those to
determine which station ID number corresponds to which name (ex. 11 = Nanoq, 23 = Ukaliatsiaq). Uncomment Line 54 to save and view the map.
    Run the file by starting a Pitzer Desktop, opening a terminal, and typing the following commands:

    source .bashrc
    python weatherballoon_fixed.py

FINDING RUNS

How do you find the run with a weather balloon?
    Simple answer: brute force.
    The code in Line 56 to Line 86 extracts RNO-G data from a specified station and run. To choose which station you are looking at, change the
number after "default=" in Line 58 (ex. if you want to look at station 11, you would change Line 58 to:
"argparser.add_argument('--station', type=int, default=11))"). The same is true for choosing the run in Line 59, change the number after "default=".
*NOTE: Lines 88 and 96 define two functions: voltfreqplot() and exclude_zeroes(). I will elaborate on those later, when they are useful.
*NOTE: There is a command called d.setEntries in Line 75. This determines how many events in the run are processed. Make sure the number you input
for d.setEntries is greater than d.N, the number of events in the run.
    The dataset contains a category of data called "readoutTime". This contains the time in unix time (seconds since January 1st, 1970, GMT) of each
event recorded in the chosen run. The code in Lines 104 - 110 creates two lists: "unixtime" and "secs", and pulls the readoutTime information from
the dataset. It then appends the readoutTime (unix time values) to "unixtime", and the recorded time of each event in seconds from the first event to
"secs". It then prints the first and last element of "unixtime" to get the time span of the run in unix time, and the first and last element of
"secs" to get the length of the run in seconds.
    Once the printed unix times overlap with the times from the .gpx.gz file, you can move on.

SORTING BY MINUTE

    The code then sorts the times in "secs" into minutes, then uses these to sort the corresponding event numbers into minutes. This outputs the list
"M", which contains lists for each minute in the run. Each list in "M" contains the events that occur in that minute. Some minutes will be empty,
and there is a check applied later to account for minutes with len(M[j]) == 0.

AVERAGING FREQUENCY AND POWER PER MINUTE

How does this work? (Can skip this section if no questions)
    This is the main objective of the code. The following is an explanation of how it works, but it is not necessary to understand this to know how
to use it. The first command in Line 136 creates a for-loop that loops over the number of minutes in the run. Inside the loop, it creates two arrays
of zeros, one to store frequencies and one to store powers. The dimensions of these arrays are len(M[j]) (length of each minute in the run) and
1024 (half the length of the waveforms). A second for-loop is open, that loops over each event in the current minute. Inside this second loop, the 
code uses the function defined in Line 88 to perform an FFT and get the frequency and power of each event in the minute, and assigns it to the
corresponding row in xvals or yvals.
    The code then averages the frequencies of each event per minute to get one frequency array for the entire minute. Each frequency array per minute
should be the same. The code uses the fuction defined in Line 96 to filter out any empty rows. The code averages the powers for each event by summing
them and dividing by the number of events in the minute. Then two additional arrays are created, one to store the average frequencies of each minute
(all_xvals) and one to store the average powers of each minute (all_yvals).
*NOTE: Lines 136 - 142 must be copied to be able to assign values to all_xvals and all_yvals. That is why it appears twice.
    The average frequencies per minute are converted to MHz (from GHz) and assigned to their corresponding row in all_xvals. The average powers per
minute are assigned to their corresponding row in all_yvals. These can now be used to create a spectrogram.

How do I use this code?
    To use it, all you have to do is change the channel you are viewing in Lines 140 and 149. Inside the FFT function (voltfreqplot()), there is the
input "all_wfs[event][channel]". all_wfs[event][channel] is used to call the waveforms of each event, extracted from the dataset. The first square
bracket contains the event number you want to look at, and the second square bracket contains the channel you want to look at.
    There are 24 channels per station, of varying depths. To find weather balloons, you'll want to stick to surface channels, which are channels
12 - 20. I have had the best luck with channel 16. This should be the only thing you need to change from run-to-run, everything else should be
already set. 
*NOTE: In Lines 113 - 121, there is commented out code to plot and save a frequency vs. power line plot without averaging the events per minute.
This is meant to be an extra check before the spectrogram, to confirm that weather balloon signals exist in the run. This code plots frequency on
the x-axis in GHz and power on the y-axis in db. If weather balloon signals are present, there will be a spike in power at around 0.4 GHz on the
plot. Uncomment the code to save and view this plot. An example called "WeatherBalloon.pdf" is provided in the repository.

CREATING THE SPECTROGRAM 
    The next section of the code assigns the values contained in all_yvals to the color axis. It does this by using the axs.imshow() function from
matplotlib. The important thing about this section is to always make sure the "extent=[]" is set to have the x-axis range as the total minutes in 
the run and the y-axis range as the minimum and maximum frequencies recorded. Otherwise, the power spikes will not show up at the corresponding
frequency. The other important detail is "axs.set_aspect('auto')", omitting this will give you a long, narrow plot that is hard to view and interpret.

    The final bit of code sets the plot parameters (size, fontsize, tick parameters, etc.). Change these as you see fit. The final line saves the 
spectrogram as a PDF with time in minutes on the x-axis, frequency in MHz on the y-axis, and power in decibels on the color axis.

BONUS: multirun.py
    The file multirun.py contains an example of code that strings two runs together and plots them on the same spectrogram, as if they were one run.
The main points to note when doing this are that you have to copy the code that sets the station and run and extracts the data (Lines 11 - 41 in
multirun.py) for each run you want to plot. Also be sure to specifically designate all_xvals and all_yvals array to the run they correspond to. They 
are strung together right before plotting using np.concatenate(). An example called "MultiRun.pdf" is provided in the repository.
