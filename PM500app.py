# -*- coding: utf-8 -*-
"""
Created on Wed Oct 08 16:54:09 2014

@author: afeldman
"""

import sys,os,threading,time
import numpy as np
from PyQt4 import QtCore, QtGui
from parse import *

sys.path.append("H:\\Python\\devices")
sys.path.append("H:\\Python\\tools")

import PM500gui
import PM500




def umtops(pos):
    c=299792458*1E6*1E-12
    pspos=(pos+myapp.settings.maxtrav)/c*2*myapp.settings.nummirrors
    return pspos
    
def pstoum(pspos):
    c=299792458*1E6*1E-12
    pos=pspos*c/(2*myapp.settings.nummirrors)-myapp.settings.maxtrav
    return pos    
    

class PM500dialog(QtGui.QDialog, PM500gui.Ui_Dialog):
    def __init__(self, parent=None):
        super(PM500dialog,self).__init__(parent)
        self.setupUi(self)
        self.running=False
        
        self.ts = FuncThread(self.update)
        
        self.settings=scansettings()        
        
        self.startmeas()
        self.statusedit.setText('Stage Ready')

    def startmeas(self):
        if not self.running:
            self.running  = True 
            self.ts.start()
            
    def update(self):
        curpos=pm500.get_abspos()
        self.updateLCDum(float(curpos))
        self.updateLCDps(float(umtops(curpos)))
    
    def updateLCDum(self,text):
        self.curposLCDum.display(text)
    def updateLCDps(self,text):
        self.curposLCDps.display(text)
        
    def gotox(self,pos):
        curaxis=self.axiscombo.itemText(self.axiscombo.currentIndex())
        if abs(pos)>self.settings.maxtrav:
            self.statusedit.setText('Selected Position beyond range')
        else:
            self.statusedit.setText('Moving to '+str(pos))
            pm500.goabs(pos,str(curaxis))
            self.statusedit.setText('Done')
        

    def goabs(self):
        amt=float(self.goedit.text())
        if self.unitcombo.currentIndex()==0:
            amt=amt
        else:
            amt=pstoum(amt)
            
        tm=FuncThread(self.gotox,amt)
        tm.start()
        tm.join()
        self.update()
        
                

    def gorel(self):
        amt=float(self.goedit.text())
        curaxis=self.axiscombo.itemText(self.axiscombo.currentIndex())
        curpos=self.curposLCDum.value()
        if self.unitcombo.currentIndex()==0:
            amt=curpos+amt
        else:
            c=299792458*1E6*1E-12
            amt=curpos+amt*c/(2*self.settings.nummirrors)
        
        tm=FuncThread(self.gotox,amt)
        tm.start()
        tm.join()
        self.update()
    def gohome(self):
        self.statusedit.setText('Moving Home')
        curaxis=self.axiscombo.itemText(self.axiscombo.currentIndex())
        pm500.findCenter(str(curaxis))
        self.update()
        self.statusedit.setText('Done')
    def chgmirrors(self):
        self.settings.nummirrors=int(self.nomirrors.text())
    def chgmaxtrav(self):
        self.settings.maxtrav=int(self.maxtrav.text())
    def chgaccel(self):
        pm500.setAccel(int(self.accelset.text()))
        pm500.setDecel(int(self.accelset.text()))
    def chgvel(self):
        pm500.setHSV(int(self.veloset.text()))
    def reboot(self):
        self.statusedit.setText('Rebooting, please wait 45 sec')
        tr=FuncThread(pm500.reset)
        tr.setDaemon(True)
        tr.start()
        tr.join(45)
        pm500.findCenter()
        self.statusedit.setText('Stage Ready')
    def chgAxisenabled(self):
        self.axiscombo.clear()
        
        numchecked = 0
        if self.Xcb.checkState(): 
            self.axiscombo.addItem("X")
            numchecked=numchecked+1
        if self.Ycb.checkState():
            self.axiscombo.addItem("Y")
            numchecked=numchecked+1
        if self.Zcb.checkState():
            self.axiscombo.addItem("Z")
            numchecked=numchecked+1
        if self.Acb.checkState():
            self.axiscombo.addItem("A")
            numchecked=numchecked+1
        if self.Bcb.checkState():
            self.axiscombo.addItem("B")
            numchecked=numchecked+1
            
        self.axiscombo.setCurrentIndex(0)
        self.settings.numaxis=numchecked
    def reject(self):
        self.running=False
        pm500.close()
        QtGui.QDialog.accept(self)
        
class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
        self._stop=threading.Event()

    def run(self):
        self._target(*self._args)

    def stop(self):
        if self.isAlive():
            self._Thread__stop()
        
class scansettings:
    def __init__(self):
        self.nummirrors=2
        self.maxtrav=10*10000
        self.numaxis=1        
        
if (__name__ == '__main__'):
    
    add="GPIB0::1"
    pm500=PM500.device(add)
    app= QtGui.QApplication(sys.argv)
    myapp=PM500dialog()
    
    myapp.show()
    app.exec_()