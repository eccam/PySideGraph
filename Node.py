'''
Created on Oct 14, 2011

@author: Hana Truskova
'''
from PySide.QtCore import *
from PySide.QtGui import *
import math
from LineCalc import *
from LineDecorator import *

class Node(QGraphicsItem):
    """\brief base class which implements dragging and scaling of content and line connection to parent  """
    def __init__(self, lineCalc, lineDecorator, parent, name, x , y, w , h):
        QGraphicsItem.__init__(self, parent)
        
        self.lineCalc = lineCalc
        self.lineDecorator = lineDecorator
        
        self.parent = parent
        self.child = []
        """should be unique as it is used for saving and loading position in CVTesting"""
        self.name = name

        #in screen coords
        self.contentPos = QPoint(x,y) #self.scenePos()
        self.setFlag(QGraphicsItem.ItemIsMovable)
               
        #width and height of content (img, text) without the arrows
        self.w = w
        self.h = h

        #variables for proper dragging and scaling
        self.resizeMode = False
        self.moveMode = False   
        self.ignore = False    
        #bounding rectangle which encapsulates the arrow to parent
        self.lineRect = None 
                
    def getName(self):
        return self.name
        
    def addChild(self, node):
        self.child.append(node)
        
    def SetX(self,x):
        self.prepareGeometryChange()
        self.contentPos.setX(x)        
        
    def GetX(self):
        return self.contentPos.x()
    
    def SetY(self,y):
        self.prepareGeometryChange()
        self.contentPos.setY(y)     
    
    def GetY(self):
        return self.contentPos.y()
    
    def GetWidth(self):
        return self.w
    
    def SetWidth(self,w):
        self.prepareGeometryChange()
        self.w = w    
    
    def GetHeight(self):
        return self.h
    
    def SetHeight(self,h):
        self.prepareGeometryChange()
        self.h = h     
               
    def contentSceneRect(self):
        return QRect(int(self.contentPos.x()), int(self.contentPos.y()), self.w, self.h)
    
    def contentSceneRectF(self):
        return QRectF(self.contentPos, QSize(self.w, self.h))    
    
    def contentRect(self):
        return self.mapToItem(self, self.contentSceneRect()).boundingRect()
        
    def boundingRect(self):
        """important method for proper redrawing and not leaving artefacts"""              
        boundingRect = self.contentSceneRectF()
           
        # include also bounding rectangle of arrows
        if self.lineRect is not None:
            boundingRect = boundingRect.united(self.lineRect)        
        
        for w in self.child :
            if w.lineRect is not None:
                boundingRect = boundingRect.united(w.lineRect)
                     
        return boundingRect   
    
    def mousePressEvent(self, event):
        # do not react on events on arrows
        rect = self.contentSceneRect()
        if not rect.contains(int(event.scenePos().x()), int(event.scenePos().y())):
            #ungrab mouse
            event.ignore()
            self.ignore = True
            return
                
        self.ignore = False
        if event.button() == Qt.RightButton:
            self.resizeMode = True
        if event.button() == Qt.LeftButton:
            self.moveMode = True  
            self.offset = event.scenePos() - self.contentPos  
     
            
    def mouseReleaseEvent(self, event):
        if self.ignore:
            event.ignore()
        if event.button() == Qt.RightButton:
            self.resizeMode = False      
        if event.button() == Qt.LeftButton:
            self.moveMode = False              
    
    def mouseMoveEvent(self, event):          
        if self.ignore:
            event.ignore()        
        # calculate in screen coords (item coords is jerky, even.pos())
        if self.resizeMode:
            self.prepareGeometryChange()
            p = event.scenePos() - self.contentPos
            scalex = p.x()/self.w
            scaley = p.y()/self.h
            #rescale only the content, not arrow
            self.w = scalex * self.w
            self.h = scaley * self.h  
            self.update()
            
        if self.moveMode:    
            # move only the content, arrow will be redrawn
            self.prepareGeometryChange()
            p = event.scenePos() - self.offset
            self.contentPos = p
            
            self.update()
            
    def drawRect(self, painter, rect):
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))   
        painter.drawRect(rect)
        
    #draw line and decorators and recalculates bounding box
    def drawLine(self, painter, sourceRect, destRect):
        """ method for drawing line and decorators connecting parent and child node,
        recalculates also the line bounding box, which is used in node bounding box """
        self.prepareGeometryChange()
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        
        (sourcePoint, destPoint) = self.lineCalc.calcEndPoints(sourceRect, destRect)
        #drawing in item coordinates
        sourcePoint = self.mapToItem(self, sourcePoint)
        destPoint = self.mapToItem(self, destPoint)    
        
        self.lineRect = QRectF(sourcePoint, destPoint)
        line = QLineF(sourcePoint, destPoint)
        #nothing to draw
        if line.length() == 0:
            return
        painter.drawLine(line)
        
        decorators = self.lineDecorator.calcDecorator(line)
        painter.setBrush(Qt.black)
        
        for polygon in decorators:
            painter.drawPolygon(polygon)
            self.lineRect.united(polygon.boundingRect())      
            



