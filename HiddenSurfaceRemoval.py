import random as rnd
import sympy as sym

class Line :
    """
    A line L(x) = m*x + b is given by its slope m and its section offset b on the y-axis.
    """
    def __init__(self, m, b) :
        """Constructor: Create line with slope m and offset b
        :param m: the slope
        :param b: the offset on the y-axis
        """
        self.m = m
        self.b = b

    def y(self,x) :
        """ 
        :param x: x-coordinate 
        :return: y-coordinate of this line at x
        """
        return self.m*x + self.b

    def intersection(self, other):
        """ calculate the x-coordinate of the intersetion of this line with another line
        :param other: another line
        :return: x-coordinate of the intersection
        """
        return (self.m-other.m) / (other.b-self.b)

    def __repr__(self):
        """Python-equivalent of the Java toString method
        """
        return "Line(m={}, b={})".format(self.m,self.b)

def refined_brute_force(L) :
    """
    Not quite brute force as we utilise the geometric argument that
    the uppermost line can only change at points where there is an
    intersection. Compare the reasoning in the Hidden Surface Removal
    slides to justify this algorithm.
    :param L: list of Line objects.
    :return: set of line objects visible from above
    :return: list of points between all intersetions -- for estimating the x range in plotting.
    """
    intersections = [ L[i].intersection(L[j]) for i in range(len(L)) for j in range(i+1,len(L)) ]  # O(n^2)
    intersections.sort() # O(n^2 log n^2)

    # Points of interests lie between the crossing points -- we would
    # have to take special measure here if intersections happen at the
    # same x coordinate.
    poi = [ (intersections[i] + intersections[i+1]) / 2.0 for i in range(len(intersections)-1)] # O(n^2)

    # Add last points of interest to the left [right] of first [last] intersection. O(1)
    poi = [ intersections[0] - 1 ] + poi + [intersections[-1] + 1]

    # Evaluate all lines at all poi:
    visible = set()

    for x in poi: # O(n^2) times
        uppermost = max(L, key= lambda l: l.y(x)) # O(n) lines to go through.
        visible.add(uppermost) # best case: O(1), worst case O(n^2).
    return visible, poi

def divide_and_conquer(L) :
    """
    Divide and Conquer core of 
    :param L: list of lines sorted by increasing slope
    :return: list of visible lines in order of increasing slope
    :return: list of x-coordinates of intersection points in x
    order. Value at index i represents intersection between V[i] and
    V[i+1] if V is the list of visible lines also returned. 
    """
    n = len(L)
    if n == 0: return L, []
    elif n == 1: return L, [] 
    elif n == 2:
        return L, [ L[0].intersection(L[1]) ]
    elif n == 3: # first interesting case. TODO subsume in to core D&C
        x = L[0].intersection(L[2])
        y = L[0].y(x) # y coordinate of intersection
        y1 = L[1].y(x) # y coordinate of L[1] at x
        if y1 <= y : # L[1] not visible.
            del L[1] # Big-Oh -- note [] is array list!
            return L, [x]
        else: # L[1] is visible and x0,x1 are in order (due to geometry)
            x0 = L[0].intersection(L1)
            x1 = L[1].intersection(L2)
            return L, [x0,x1]

    middle = len(L)//2

    Left,iL = divide_and_conquer(L[:middle])
    Right,iR = divide_and_conquer(L[middle:])

    j = 0
    k = 0

    while j < len(iL) and k < len(iR):

        if iL[j] < iR[k] :
            x = iL[j]
            # at x and to the left of it, Left[j]) is uppermost in Left 
            yV = Left[j].y(x)
            # at x, Right[k] is uppermost in Right and to the left of iR[k]
            yW = Right[k].y(x)
            if yW > yV : # Right[k] is visible!
                xx = Left[j].intersection(Right[k])
                # xx must be to the left of iL[j] -- so Left[j+1] is covered by Right[k]
                # and so are all lines in Left with indices greater than
                # j+1: only lines Left[:j+1] visible.                # xx
                # must be to the right of iR[k-1] -- so Right[k-1] is
                # covered: only Right[k:] visible and lines with smaller
                # index than k in Right 
                visibile = Left[:j+1] + Right[k:]
                # intersection j (and bigger) are covered by Right[k], 
                intersections = iL[:j] + [xx] + iR[k:]
                return visibile, intersections
            else : j+= 1 
        else : # iL[j] >= iR[k] -- in fact iL[j] > iR[k] as we excluded
            # triple intersections
            x = iR[k]
            # at x and to its left, Right[k] is uppermost in Right 
            yW = Right[k].y(x)
            # at x (which is to the right of iL[j-1]), Left[j] is uppermost
            yV = Left[j].y(x)

            if yW > yV : # Right[k] is visible!
                xx = Right[k].intersection(Left[j]) # ??

                # Left[j] is the last visible on the left side, and Right[k:]
                # the first on the right side
                visible = Left[:j+1] + [xx] + Right[k:]
                intersection = iL[:j] + [xx] + iR[k:]
                return visibile, intersections
            else : k+= 1

    # either iL or iR has been exhausted so far, so there are?

    # Can this happen? I think not: At the latest the the last iR will
    if j == len(iL) :
        print "iL exhausted"
    elif k == len(iR) :
        print "iR exhausted. ie at none of the given intersection points is iR heigher than iL"
        print 2# Test for intersection to the right of the last
        # intersection point?"
    else :
        raise Exception("Go back to coding")

def hidden_surface_removel(L):
    """Wrapper for the D&C implementation
    """
    L.sort(key=lambda l: l.m) # O(n log n)
    visible,_ = divide_and_conquer(list(lines))
    return visible




    
            
            
# Python-equivalent of "main" method
if __name__=="__main__":
    # list of 100 random lines.
    L = [ Line(m=2*rnd.random()-1,b=2*rnd.random()-1) for _ in range(100)]
    # list of a just few lines for debugging
    # L = [ Line(-1,-2), Line(-2,-3), Line(-3,-5), Line(3,-1000)]

    visible, poi = refined_brute_force(L)

    print "Visible: {} out of {}".format(str(len(visible)), str(len(L)))
    print "Range of x-coordinates of intersections:", poi[0], poi[-1]

    # Hack to plot with sympy:
    x = sym.Symbol("x")
    sL = [l.m*x+ l.b for l in L]
    pL = sym.plot(*sL, show=False, line_color=0.0) 
    sV = [l.m*x+ l.b for l in visible]
    pV = sym.plot(*sV, show=False, line_color="red")
    pL.show()
    pV.show()
    pL.extend(pV)
    pL.show()



    #sDC = 
    #pDC = su


    

    


