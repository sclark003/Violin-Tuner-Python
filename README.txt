DSP Assignment 3- IIR filters

For this assignment, it was decided to make a violin tuner. 
Using infinite impulse response, IIR, filters, the audio signal of each string of a violin was measured in realtime in order to determine the predominant frequency. 
To use our tuner, the user types the note of the string they'd like to tune into the terminal. 
Using saved frequency values, the tuner then identifies the frequency of the note required and filters the input audio signal through a bandpass IIR filter 
to only pass when the frequency of the signal is close to the note they are trying to find. 
The output signal of the bandpass, is then loaded into a buffer. 
The fast fourier transform (FFT) is taken of the buffer at regular intervals and this spectrum is then plotted on the screen continuously. 
As a result, the output plot shows continuous frequency peaks which increase in amplitude as the input signal moves closer to the required frequency. 
