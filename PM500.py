# -*- coding: utf-8 -*-
"""
Created on Wed Oct 08 15:03:25 2014

@author: afeldman
"""

import visa,time,threading

class device:
    def __init__(self,add="GPIB0::1"):
        self.rm = visa.ResourceManager()
        self.device=self.rm.open_resource(add+'::INSTR')
        self.device.write('SCUM0')
        #print self.device.ask('ESTAT?')
        self.setHSV(25)
        self.setAccel(25)
        self.setDecel(25)
        
        self.statusset={
        'A':'Acknowledge',
        'B':'Busy',
        'D':'Done',
        'E':'Error',
        'L':'Limit',
        'M':'Motor off'}
        
    def setHSV(self,LSV,axis='X'):
        self.device.write(axis+'V '+str(LSV))
    def setAccel(self,Accel,axis='X'):
        self.device.write(axis+'ACCEL '+str(Accel))
    def setDecel(self,Decel,axis='X'):
        self.device.write(axis+'DECEL '+str(Decel))        
    def reset(self):
        tr=threading.Thread(target=self.resetthread)
        tr.start()
        tr.join()
    def resetthread(self):
        self.device.write('RSTART')
        print 'Wait 45 sec'
    def close(self):
        self.device.close()
        
    def getstatus(self,axis='X'):
        rawstat=self.device.ask(axis+'STAT?')
        return self.readstatus(rawstat)
        
    def goabs(self,abspos,axis='X'):
        self.device.write(axis+'G '+str(abspos))
        self.waitforstage()
        
    def gorel(self,relpos,axis='X'):
        self.device.write(axis+'GR'+str(relpos))
        self.waitforstage()

    def get_abspos(self,axis='X'):
        return self.readpos(self.device.ask(axis+'G?'))
        
    def gohome(self,axis='X'):
        self.device.write(axis+'H')
        self.waitforstage()
        
        
    def waitforstage(self,axis='X'):
        status=self.getstatus(axis)        
        while status != 'D':
            time.sleep(.25)
            status=self.getstatus(axis)
            print 'waiting...'
        print self.statusset[status]
        print self.get_abspos()
        
    def readpos(self,posstring):
        axis=posstring[:1]
        status=posstring[2:2]        
        pos=posstring[-12:]
        return float(pos)
        
    def readerror(self,errorstring):
        axis=statusstring[:1]
        status=statusstring[2:2]      
    
    def readstatus(self,statusstring):
        axis=statusstring[:1]
        status=statusstring[1:2]
        return status
        
    def findCenter(self,axis='X'):
        self.device.write(axis+'F1')
        self.waitforstage()
        
        
if (__name__ == '__main__'):
    add="GPIB0::1"
    pm500=device(add)
    curpos=pm500.get_abspos()
    print curpos
    pm500.findCenter()
#    if curpos == 0:
#        pm500.goabs(10000)
#    else:
#        pm500.gohome()
    
    
    
    
