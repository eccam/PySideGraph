'''
Created on Oct 19, 2011

@author: htruskova
'''
from PySide.QtCore import *
from PySide.QtGui import *
from Node import Node

class ImageNode(Node):
    """ \brief Class for image content """
    def __init__(self, lineCalc, lineDecorator, parent, name, img, x = 0, y = 0, w = 100, h = 100):
        Node.__init__(self, lineCalc, lineDecorator, parent, name, x, y, w, h)    

        self.img = img    
        if img is not None and (img.width() != self.w or img.height() != self.h):
            self.img = img.scaled(self.w, self.h)
        
        self.bitmap_lock = threading.Lock()
               
    def paint(self, painter, option, widget):
        #Local coords !!
        self.drawRect(painter, self.contentRect())  
        
        if self.img is not None:
            with self.bitmap_lock:
                painter.drawImage(self.contentRect(), self.img) 
            
        if self.parent is not None:
            self.drawLine(painter, self.contentSceneRect(), self.parent.contentSceneRect())     
       
            
    def changeImg(self, img):        
        if img.width() != self.w or img.height() != self.h:
            img = img.scaled(self.w, self.h)
        
        with self.bitmap_lock:
            self.img = img            
        #self.update(self.contentSceneRect()) 