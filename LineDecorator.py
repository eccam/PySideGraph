'''
Created on Oct 20, 2011

@author: htruskova
'''
from PySide.QtCore import *
from PySide.QtGui import *
import math

class LineDecorator(object):
    """\brief Class for calculating polygon at the line ends, e.g: arrows, circles  """
    def calcDecorator(self, line):
        pure_virtual()
        
class LineDecoratorNone(LineDecorator):
    """\brief Class for empty line decorators  """
    def __init__(self):
        LineDecorator.__init__(self)
        
    def calcDecorator(self, line):        
        return []        
        
class LineArrowOnStart(LineDecorator):
    def __init__(self, arrowSize = 10):
        LineDecorator.__init__(self)
        self.arrowSize = arrowSize
            
    def calcDecorator(self, line):        
        if line.length() == 0:
            return []
        #line = QLineF(sourcePoint, destPoint)        
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = math.pi * 2.0 - angle

        sourceArrowP1 = line.p1() + QPointF(math.sin(angle + math.pi/ 3) * self.arrowSize,
                                                          math.cos(angle + math.pi / 3) * self.arrowSize)
        sourceArrowP2 = line.p1() + QPointF(math.sin(angle + math.pi - math.pi/ 3) * self.arrowSize,
                                                          math.cos(angle + math.pi - math.pi / 3) * self.arrowSize);

        polygons = []
        polygons.append(QPolygonF([line.p1(), sourceArrowP1, sourceArrowP2]))
        return polygons
               