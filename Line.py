'''
Created on Oct 14, 2011

@author: Hana Truskova
'''
from PySide.QtCore import *
from PySide.QtGui import *
import math
from LineCalc import *
from LineDecorator import *

class Line(QGraphicsItem):
    """\brief base class which implements dragging and scaling of content and line connection to parent  """
    def __init__(self, lineCalc, lineDecorator, sourceNode, destNode):
        QGraphicsItem.__init__(self, destNode)
        self.lineCalc = lineCalc
        self.lineDecorator = lineDecorator
        self.lineRect = QRectF()
        self.sourceNode = sourceNode
        self.destNode = destNode
        
    def boundingRect(self):
        """important method for proper redrawing and not leaving artefacts"""     
        return self.lineRect
    
    def paint(self, painter, option, widget):
        self.prepareGeometryChange()
        #Local coords !!    
        sourceRect = self.sourceNode.contentSceneRect()
        destRect = self.destNode.contentSceneRect()
        
        """ method for drawing line and decorators connecting parent and child node,
        recalculates also the line bounding box, which is used in node bounding box """
        
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
            self.lineRect = self.lineRect.united(polygon.boundingRect()) 
        
        