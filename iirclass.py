import numpy as np

#2nd order IIR filter
class IIR2_filter:
    def __init__(self, sos):
        self.b0= sos[0]
        self.b1= sos[1]
        self.b2= sos[2]
        self.a1= sos[4]
        self.a2= sos[5]
        self.buffer1 = 0
        self.buffer2 = 0
        
    def dofilter(self,x):
        #accumulator for the IIR part
        input_acc = x
        input_acc = input_acc - (self.a1*self.buffer1)
        input_acc = input_acc - (self.a2*self.buffer2)
    
        #accumulator for the FIR part
        output_acc = input_acc*self.b0
        output_acc = output_acc + (self.b1*self.buffer1)
        output_acc = output_acc + (self.b2*self.buffer2)
        
        self.buffer2 = self.buffer1
        self.buffer1 = input_acc
        
        return output_acc
    
        
class IIR_filter:
    def __init__(self, SOS):
        self.sos = SOS
        self.slaves = []
        self.data = np.zeros(500)
        #access IIR2 filter with coefficients sos
        self.order = len(SOS)
        for i in range(self.order):
            self.slaves.append(IIR2_filter(SOS[0,:]))
            
    def dofilter(self, x):
        y = x
        #create n instances of slave class
        for i in range(self.order):
            y = self.slaves[i].dofilter(y)
        z = y
        return z