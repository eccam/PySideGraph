'''
Created on Oct 20, 2011

@author: htruskova
'''
from PySide.QtCore import *
from PySide.QtGui import *
import math
import exceptions

class LineCalc(object):
    """\brief Class for calculating line points, which connects node parent and child node  """
    def calcEndPoints(self, sourceRect, destRect):
        pure_virtual()
        
class NoLine(LineCalc):
    """\brief Class for no connection node parent and child node  """
    def __init__(self):
        LineCalc.__init__(self)   
        
    def calcEndPoints(self, localSourceRect, localDestRect):
        return (QPointF(0,0),QPointF(0,0))
        
        
class CornerCalc(LineCalc):
    """\brief Class for calculating line points, which snaps to bounding box corners  """
    def __init__(self):
        LineCalc.__init__(self)
        
    #in screen coordinates
    def calcEndPoints(self, localSourceRect, localDestRect):        
        #find out line corner origin
        line = QLineF(localSourceRect.center() ,localDestRect.center())
        
        #snap to near corners
        sourceOffset = QPointF()
        destOffset = QPointF()
        
        destW = localDestRect.width()
        destH = localDestRect.height()
        
        sourceW = localSourceRect.width()
        sourceH = localSourceRect.height()
        
        #compute offset from the widget content center
        #source = top right corner, dest = down left corner
        if line.p2().x() > line.p1().x() and line.p2().y() > line.p1().y():
            destOffset = QPointF(-destW/2, -destH/2)
            sourceOffset = QPointF(sourceW/2, sourceH/2)
        # dest = top right corner, source = down left corner
        if line.p2().x() < line.p1().x() and line.p2().y() < line.p1().y():
            destOffset = QPointF(destW/2, destH/2)
            sourceOffset = QPointF(-sourceW/2, -sourceH/2)
        #
        if line.p2().x() > line.p1().x() and line.p2().y() < line.p1().y():
            destOffset = QPointF(-destW/2, destH/2)
            sourceOffset = QPointF(sourceW/2, -sourceH/2)    
        
        if line.p2().x() < line.p1().x() and line.p2().y() > line.p1().y():
            destOffset = QPointF(destW/2, -destH/2)
            sourceOffset = QPointF(-sourceW/2, sourceH/2)
            
        destPoint = QPointF(localDestRect.center().x(), localDestRect.center().y()) + destOffset
        sourcePoint = QPointF(localSourceRect.center().x(), localSourceRect.center().y()) + sourceOffset       
        
        return (sourcePoint, destPoint)
      

class CenterCalc(LineCalc):
    """\brief Class for calculating line points, which connects node parent and child node,
        bounding box center points are connected and shifted on the border 
        modified Cohen-Sutherland algorithm      
        http://en.wikipedia.org/wiki/Cohen%E2%80%93Sutherland_algorithm
    """
    INSIDE = 0; # 0000
    LEFT = 1;   # 0001
    RIGHT = 2;  # 0010
    BOTTOM = 4; # 0100
    TOP = 8;    # 1000    
    
    def __init__(self):
        LineCalc.__init__(self)
        
    #in screen coordinates
    #modified Cohen Sutherland algorithm
    def computeOutCode(self, point, rect): 
        code = CenterCalc.INSIDE
        
        if point.x() < rect.left():
            code |= CenterCalc.LEFT
        else:
            if point.x() > rect.right():
                code |= CenterCalc.RIGHT
        if point.y() < rect.top():
            code |= CenterCalc.TOP
        else:
            if point.y() > rect.bottom():
                code |= CenterCalc.BOTTOM
        return code
    
    def yClamp(self, outcodeOut, y, ymin, ymax):
        val = y
        if outcodeOut & CenterCalc.TOP :
            val = ymin
        if outcodeOut & CenterCalc.BOTTOM :
            val = ymax        
        return val
    
    def xClamp(self, outcodeOut, x, xmin, xmax): 
        val = x
        if outcodeOut & CenterCalc.RIGHT:
            val = xmax
        if outcodeOut & CenterCalc.LEFT: 
            val = xmin    
        return val    
    
    def caclSegmentRectIntersection(self, rect, p1, p2, printd):
        outcode0 = self.computeOutCode(p1, rect);
        #assume p1 is inside rect
        if outcode0 != CenterCalc.INSIDE:
            raise Exception("not expected point")
        outcodeOut = self.computeOutCode(p2, rect); 
        
        #null length arrow
        if outcodeOut == CenterCalc.INSIDE:
            return p1

        # Now find the intersection point;
        # use formulas y = y0 + slope * (x - x0), x = x0 + (1 / slope) * (y - y0)
        x = p1.x()
        x1 = p2.x()
        y = p1.y()
        y1 = p2.y()
        ymax = rect.bottom()
        ymin = rect.top()
        xmin = rect.left()
        xmax = rect.right()        

        #need at max 2 passes (modified algorithm)
        for i in range(2):
            if y1 - y == 0:
                x = self.xClamp(outcodeOut, x, xmin, xmax)
                outcodeOut = self.computeOutCode(QPointF(x,y), rect);
                continue    
            
            if x1 - x == 0:
                y = self.yClamp(outcodeOut, y, ymin, ymax)
                outcodeOut = self.computeOutCode(QPointF(x,y), rect);
                continue 
                
            slope = (x1 - x) / (y1 - y)
               
            if outcodeOut & CenterCalc.TOP : # point is above the clip rectangle
                x = x + slope * (ymin - y)
                y = ymin            
            else:
                if outcodeOut & CenterCalc.BOTTOM : # point is below the clip rectangle
                    x = x + slope * (ymax - y) 
                    y = ymax
                else:    
                    if outcodeOut & CenterCalc.RIGHT : # point is to the right of clip rectangle
                        #print "modify", (xmax - x) / slope
                        y = y  +  (xmax - x) / slope
                        x = xmax
                    else:    
                        if outcodeOut & CenterCalc.LEFT: #    point is to the left of clip rectangle
                            #print "modify", (xmin - x) / slope
                            y = y + (xmin - x) / slope
                            x = xmin
                
            outcodeOut = self.computeOutCode(QPointF(x,y), rect);
     
        # Now we move outside point to intersection point to clip

        return QPointF(x,y)
    
    def calcEndPoints(self, srcRect, destRect):
        #find out line corner origin
        line = QLineF(srcRect.center() ,destRect.center())
        
        #both points inside
        code = self.computeOutCode(line.p2(), srcRect)
        if code == CenterCalc.INSIDE:
            return (QPointF(0,0),QPointF(0,0))

        #print line
        p1 = self.caclSegmentRectIntersection(srcRect, line.p1(), line.p2(), True) 
        p2 = self.caclSegmentRectIntersection(destRect, line.p2(), line.p1(), False)    
        return (p1, p2)
     
        