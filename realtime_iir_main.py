import threading
import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyusbdux as c
import iirclass as iir
import scipy.signal as sig

#set up variables
ringbuffer = []
fs =1345

#normalise
norm = 2/fs

#########################################################################

#Set up Qt Panning Plot class
app = QtGui.QApplication(sys.argv)
running = True


channel_of_window1 = 0
channel_of_window2 = 0

class QtPanningPlot:

    #set up Panning plot
    def __init__(self,title):
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle(title)
        self.plt = self.win.addPlot()
        self.plt.setYRange(0,5)
        self.plt.setXRange(0,500)
        self.curve = self.plt.plot()
        self.data = []
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)
        self.win.show()
        
    def update(self):
        self.data=self.data[-500:]
        if self.data:
            self.curve.setData(np.hstack(self.data))

    def addData(self,d):
        self.data.append(d)

#########################################################################

#create function to get, filter and plot data
def getDataThread(qtPanningPlot1, qtPanningPlot2, ringbuffer, frequency, n):

    ############################################
    #set up variables
    
    #normalise (Wn for butterworth filter is in half-cycles / sample)
    norm = 2/fs
    plotbuffer = []
        
    #calculate coefficients
    wide= np.array([(frequency-11)*norm, (frequency+11)*norm])

    #sos
    sos_wide = sig.butter(10, wide, btype='bandpass', output='sos')
        
    #access master IIR filter with coefficients
    master_wide = iir.IIR_filter(sos_wide)
    
    ############################################
    
    while running:
        # loop as fast as we can to empty the kernel buffer
        while c.hasSampleAvailable():
            sample = c.getSampleFromBuffer()
            v1 = 10**2*sample[channel_of_window1]
            #filter data
            v2 = master_wide.dofilter(v1)
            #detect strength of peak
            detect=((th*m*10*abs(v2)))
            print(detect)
            #if in range
            if detect > n:
                #digital outputs
                #3 = red light
                #2 = blue light
                c.digital_out(3,1)
                c.digital_out(2,0)

            #if it is close
            elif n > detect > 2:
                c.digital_out(3,0)
                c.digital_out(2,1)

            #if no signal is detected
            else:
                c.digital_out(3,0)
                c.digital_out(2,0)
                
            #add filtered data to ringbuffer
            ringbuffer= np.append(ringbuffer,v2)
            #plot incoming signal
            qtPanningPlot1.addData(v1)
            #check if there is data in the ringbuffer
            #if data is found then add it to plotbuffer and reset ringbuffer
            if not ringbuffer == []:
                result = ringbuffer
                ringbuffer = []
                plotbuffer=np.append(plotbuffer,result)

            #only keep the most recent 50 samples of data
            plotbuffer=plotbuffer[-50:]
            #calculate the spectrum
            spectrum = np.fft.rfft(plotbuffer)
            # absolute value
            spectrum2 = m*np.absolute(spectrum)/len(spectrum)
            #plot spectrum
            qtPanningPlot2.addData(spectrum2)

#########################################################################

#main programme
# open comedi
c.open()

#set digital outputs low to start
c.digital_out(2,0)
c.digital_out(3,0)

#print user interaction
print("Violin Tuner")
print("Type note to tune: G, D, A or E")
frequency = input()

#set variables based on user input
if frequency == 'G':
     frequency = 196
     m= 10**107
     th = 1
     n = 12
if frequency == 'D':
     frequency = 293.66
     m= 10**105
     th = 5
     n = 12
if frequency == 'A':
     frequency = 440
     m = 10**116
     th = 7
     n = 12
if frequency == 'E':
     frequency = 659.25
     m= 10**105
     th = 1
     n = 12

print("The frequency of that note is {}Hz" .format(frequency))

############################################

#create two instances of plot windows
qtPanningPlot1 = QtPanningPlot("Input Signal")
qtPanningPlot2 = QtPanningPlot("Output Frequency")

#create a thread which gets the data from the USB-DUX
t = threading.Thread(target=getDataThread,args=(qtPanningPlot1, qtPanningPlot2,ringbuffer,frequency, n))

############################################

# start data acquisition
c.start(8,1345)

# start the thread getting the data
t.start()

# showing all the windows
app.exec_()

# no more data from the USB-DUX
c.stop()

# Signal the Thread to stop
running = False

# Waiting for the thread to stop
t.join()

c.close()

print("finished")
