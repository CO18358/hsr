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
        return (self.b-other.b) / (other.m-self.m)

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

def visible_intersections(V):
    """
    Render the visibile sections of a set of visible lines.
    :param V: list of visible lines sorted by increasing slop.
    :return: list of x-co-ordinates of intersections where index i is the
    intersection between line i and line i+1 from V. 

    Note: by our mathematical consideration the returned X will be in
    increasing order. 
    """
    X = []
    for i in range(len(V)-1):
        x = V[i].intersection(V[i+1])
        X.append(x)
    return X
    # more pytonic:
    # return [ V[i].intersection(V[i+1]) for i in range(len(V)-1) ] # O(n)
    
def render_visible(V):
    """
    Render the visibile sections of a set of visible lines.
    :param V: set of visible lines sorted by increasing slope.
    :return X,Y: x and y between which to render a straight line.
    """

    # make V into list sorted by slope: O(nlogn)
    V = sorted(V, key=lambda l: l.m)
    X = visible_intersections(V)

    # add point beyond left end point to have a support point for the line
    # with smallest slope
    X = [X[0]-5] + X

    # Calculate the corresponding Y values:
    Y = [ l.y(x) for l,x in zip(V,X)]

    # and now a support point for the lines with greatest slope:
    X.append( X[-1]+5 )
    Y.append( V[-1].y(X[-1]+5) )
    return X,Y

def render_visible2(V):
    """
    Render the visibile sections of a set of visible lines.
    :param V: set of visible lines sorted by increasing slope.
    :return:
    This is just a version of render_visible2 that can by plotted by sympy.
    """

    # make V into listed sorted by slope: O(n)
    V = sorted(V, key=lambda l: l.m)
    X = visible_intersections(V)

    x = sym.Symbol("x")
    piecewise = [ (V[i].m*x + V[i].b, x < X[i]) for i in range(len(X))]
    piecewise.append( (V[-1].m*x + V[-1].b, True) )
    return piecewise

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
    # Base Cases
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
            x0 = L[0].intersection(L[1])
            x1 = L[1].intersection(L[2])
            return L, [x0,x1]

    # divide
    middle = len(L)//2

    # get visible lines from LEFT and their intersections
    Left, xL = divide_and_conquer(L[:middle])

    # get visible lines from RIGHT and their intersections
    Right, xR = divide_and_conquer(L[middle:])

    # indices into left and right halves
    l = 0
    r = 0

    # find last visible line from LEFT:
    while l < len(xL)-1 and r < len(xR)-1:

        if xL[l] < xR[r]:
            # at x and to the left of it, Left[l] is uppermost in Left:
            x = xL[l]

            # height of intersection point between Left[l] and
            # Left[l+1]
            yL = Left[l].y(x) 
            
            # x is left of xR[r], so Right[r] is uppermost in Right:
            yR = Right[r].y(x)

            if yR > yL : # Right[r] is the first visible from Right!
                x0 = Left[l].intersection(Right[r])
                # x0 is to the left of xL[l] -- so Left[l+1] is
                # covered by Right[k] and so are all other lines from
                # Left with indices greater than l+1 as Right[k] is
                # steeper than all of them.
                # Therefore the visible lines from Left are:
                VL = Left[:l+1]
                # Remaining visible intersection points:
                xLL = xL[:l]
                # break # out of the while loop
                VR = Right[r:]
                xRR = xR[r:]

                return VL + VR, xLL + [x0] + xRR
                
            else: # xL[i] wasn't the first point where LEFT is higher
                # than RIGHT
                l+=1
        else: # xR[r] < xL[l] (and xL[l-1] < xR[r] < xR[r] -- we would
            # not have increamented l-1 to l if not xL[l-1] < xR[r]
            # at x and to the left of it Right[r] is uppermost in Right
            x = xR[r]
            yR = Right[r].y(x)
            yL = Left[l].y(x)
            if yL > yR: r+=1 # x is not the point where Right has
            # become uppermost.
            else: # Right has become uppermost for the first time, and
                # hence will remain so at intersection r -- so Line r
                # and steeper are visible
                VR = Right[r:]
                xRR = xL[r:]
                VL = Left[:l+1]
                xLL = xL[:l]
                x0 = Left[l].intersection(Right[r])
                return VL + VR, xLL + [x0] + xRR

    print "We should never have got here?"
    x0 = Left[-1].intersection(Right[0])
    return Left+Right, xL + [x0] + xR
        

def hidden_surface_removal(L):
    """Wrapper for the D&C implementation
    """
    L.sort(key=lambda l: l.m) # O(n log n)
    visible,_ = divide_and_conquer(list(L))
    return visible


# Python-equivalent of "main" method
#if __name__=="__main__":
def hundred_lines():
    # list of 100 random lines.
    #L = [ Line(m=2*rnd.random()-1,b=2*rnd.random()-1) for _ in range(100)]
    # list of a just few lines for debugging
    L = [ Line(-1,-2), Line(-2,-3), Line(-3,-5), Line(3,-1000)]

    visible, poi = refined_brute_force(L)

    print "Visible: {} out of {}".format(str(len(visible)), str(len(L)))
    print "Range of x-coordinates of intersections:", poi[0], poi[-1]

    render = render_visible2(visible)
    p = sym.Piecewise(*render)
    pR = sym.plot(p, line_color="red", show=False)

    # Hack to plot with sympy:
    x = sym.Symbol("x")
    sL = [l.m*x+ l.b for l in L]
    pL = sym.plot(*sL, show=False, line_color="black") 
    sV = [l.m*x+ l.b for l in visible]
    pV = sym.plot(*sV, show=False, line_color="blue")
    #pL.show()
    #pV.show()
    #pL.extend(pV)
    #pL.show()
    #pDC = su

    #pA = sym.plot(0)
    #pA.extend(pL)
    #pA.extend(pV)

    visible2 = hidden_surface_removal(L)
    visible3 = sorted(visible, key=lambda l:l.m)
    
    print visible3
    print visible2
    assert visible2 == visible3


    
    return pL, pV, pR, visible


if __name__=="__main__":
    pL, pV, pR, visible = hundred_lines()

    


