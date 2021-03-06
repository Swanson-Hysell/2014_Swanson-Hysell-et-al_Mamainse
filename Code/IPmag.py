import pmag, pmagplotlib
import pylab
import numpy
import matplotlib.pyplot as plt

def iflip(D): #function simplified from PmagPy pmag.flip function
    """
    This function returns the antipode (flips) of the unit vectors in D (dec,inc,length).
    """
    Dflip=[]
    for rec in D:
        d,i=(rec[0]-180.)%360.,-rec[1]
        Dflip.append([d,i,1.])
    return Dflip

def iplotDI(DIblock,color='k'):
    """
    Plot declination, inclination data on a equal area plot

    This function modifies the plotDI function of PmagPy for use in the IPython notebook environment

    Parameters
    ----------

    DIblock : a DIblock is comprise of a list of unit vectors [dec,inc,1.]
    color : the default color is black. Other colors can be chosen (e.g. 'r')
    """
    # initialize the variables
    X_down,X_up,Y_down,Y_up=[],[],[],[]
    for rec in DIblock:
        Up,Down=0,0
        XY=pmag.dimap(rec[0],rec[1])
        if rec[1] >= 0:         
            X_down.append(XY[0])
            Y_down.append(XY[1])
        else:
            X_up.append(XY[0])
            Y_up.append(XY[1])

    if len(X_up)>0:
        pylab.scatter(X_up,Y_up,facecolors='none', edgecolors=color)

    if len(X_down)>0: 
        pylab.scatter(X_down,Y_down,facecolors=color, edgecolors=color)
        
def iBootstrap(Data1,Data2,NumSims=1000):
    """
    Conduct a bootstrap test (Tauxe, 2010) for a common mean on two declination, inclination data sets
    
    This function modifies code from PmagPy for use calculating and plotting bootstrap statistics. 
    Three plots are generated (one for x, one for y and one for z).
    If the 95 percent confidence bounds for each component overlap each other, the two directions are not significantly different.

    Parameters
    ----------

    Data1 : a list of directional data [dec,inc]
    Data2 : a list of directional data [dec,inc]
    NumSims : number of bootstrap samples (default is 1000)
    """         
    counter=0
    BDI1=pmag.di_boot(Data1)
    BDI2=pmag.di_boot(Data2)
    print ""
    print "==============="
    print ""
    print "Here are the results of the bootstrap test for a common mean"
    CDF={'X':1,'Y':2,'Z':3}
    pylab.figure(CDF['X'],figsize=(4,4),dpi=160)
    pylab.figure(CDF['Y'],figsize=(4,4),dpi=160)
    pylab.figure(CDF['Z'],figsize=(4,4),dpi=160)
    pmagplotlib.plotCOM(CDF,BDI1,BDI2,["",""])


    
def iWatsonV(Data1,Data2,NumSims=5000):
    """
    Conduct a Watson V test for a common mean on two declination, inclination data sets
    
    This function calculates Watson's V statistic from inumpyut files through Monte Carlo simulation
    in order to test whether two populations of directional data could have been drawn from a common mean.
    The critical angle between the two sample mean directions and the corresponding McFadden and McElhinny (1990) classification is printed.


    Parameters
    ----------

    Data1 : a list of directional data [dec,inc]
    Data2 : a list of directional data [dec,inc]
    NumSims : number of Monte Carlo simulations (default is 5000)
    """   
    pars_1=pmag.fisher_mean(Data1)
    pars_2=pmag.fisher_mean(Data2)

    cart_1=pmag.dir2cart([pars_1["dec"],pars_1["inc"],pars_1["r"]])
    cart_2=pmag.dir2cart([pars_2['dec'],pars_2['inc'],pars_2["r"]])
    Sw=pars_1['k']*pars_1['r']+pars_2['k']*pars_2['r'] # k1*r1+k2*r2
    xhat_1=pars_1['k']*cart_1[0]+pars_2['k']*cart_2[0] # k1*x1+k2*x2
    xhat_2=pars_1['k']*cart_1[1]+pars_2['k']*cart_2[1] # k1*y1+k2*y2
    xhat_3=pars_1['k']*cart_1[2]+pars_2['k']*cart_2[2] # k1*z1+k2*z2
    Rw=numpy.sqrt(xhat_1**2+xhat_2**2+xhat_3**2)
    V=2*(Sw-Rw)
    # keep weighted sum for later when determining the "critical angle" 
    # let's save it as Sr (notation of McFadden and McElhinny, 1990)
    Sr=Sw 
    
    # do monte carlo simulation of datasets with same kappas as data, 
    # but a common mean
    counter=0
    Vp=[] # set of Vs from simulations
    for k in range(NumSims): 
       
    # get a set of N1 fisher distributed vectors with k1,
    # calculate fisher stats
        Dirp=[]
        for i in range(pars_1["n"]):
            Dirp.append(pmag.fshdev(pars_1["k"]))
        pars_p1=pmag.fisher_mean(Dirp)
    # get a set of N2 fisher distributed vectors with k2, 
    # calculate fisher stats
        Dirp=[]
        for i in range(pars_2["n"]):
            Dirp.append(pmag.fshdev(pars_2["k"]))
        pars_p2=pmag.fisher_mean(Dirp)
    # get the V for these
        Vk=pmag.vfunc(pars_p1,pars_p2)
        Vp.append(Vk)

    # sort the Vs, get Vcrit (95th percentile one)

    Vp.sort()
    k=int(.95*NumSims)
    Vcrit=Vp[k]

    # equation 18 of McFadden and McElhinny, 1990 calculates the critical
    # value of R (Rwc)

    Rwc=Sr-(Vcrit/2)

    # following equation 19 of McFadden and McElhinny (1990) the critical
    # angle is calculated. If the observed angle (also calculated below)
    # between the data set means exceeds the critical angle the hypothesis 
    # of a common mean direction may be rejected at the 95% confidence
    # level. The critical angle is simply a different way to present 
    # Watson's V parameter so it makes sense to use the Watson V parameter
    # in comparison with the critical value of V for considering the test
    # results. What calculating the critical angle allows for is the 
    # classification of McFadden and McElhinny (1990) to be made
    # for data sets that are consistent with sharing a common mean.

    k1=pars_1['k']
    k2=pars_2['k']
    R1=pars_1['r']
    R2=pars_2['r']
    critical_angle=numpy.degrees(numpy.arccos(((Rwc**2)-((k1*R1)**2)
                                               -((k2*R2)**2))/
                                              (2*k1*R1*k2*R2)))
    D1=(pars_1['dec'],pars_1['inc'])
    D2=(pars_2['dec'],pars_2['inc'])
    angle=pmag.angle(D1,D2)

    print "Results of Watson V test: "
    print "" 
    print "Watson's V:           " '%.1f' %(V)
    print "Critical value of V:  " '%.1f' %(Vcrit)

    if V<Vcrit:
        print '"Pass": Since V is less than Vcrit, the null hypothesis'
        print 'that the two populations are drawn from distributions'
        print 'that share a common mean direction can not be rejected.'
    elif V>Vcrit:
        print '"Fail": Since V is greater than Vcrit, the two means can'
        print 'be distinguished at the 95% confidence level.'
    print ""    
    print "M&M1990 classification:"
    print "" 
    print "Angle between data set means: " '%.1f'%(angle)
    print "Critical angle for M&M1990:   " '%.1f'%(critical_angle)
    
    if V>Vcrit:
        print ""
    elif V<Vcrit:
        if critical_angle<5:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'A'"
        elif critical_angle<10:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'B'"
        elif critical_angle<20:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'C'"
        else:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'INDETERMINATE;"
            
def lat_from_i(inc):
    """
    Calculate paleolatitude from inclination using the dipole equation
    """
    rad=numpy.pi/180.
    paleo_lat=numpy.arctan( 0.5*numpy.tan(inc*rad))/rad
    return paleo_lat
    
def shoot(lon, lat, azimuth, maxdist=None):
    """
    This function enables A95 error ellipses to be drawn in basemap around paleomagnetic poles in conjunction with equi
    (from: http://www.geophysique.be/2011/02/20/matplotlib-basemap-tutorial-09-drawing-circles/)
    """
    glat1 = lat * numpy.pi / 180.
    glon1 = lon * numpy.pi / 180.
    s = maxdist / 1.852
    faz = azimuth * numpy.pi / 180.
 
    EPS= 0.00000000005
    if ((numpy.abs(numpy.cos(glat1))<EPS) and not (numpy.abs(numpy.sin(faz))<EPS)):
        alert("Only N-S courses are meaningful, starting at a pole!")
 
    a=6378.13/1.852
    f=1/298.257223563
    r = 1 - f
    tu = r * numpy.tan(glat1)
    sf = numpy.sin(faz)
    cf = numpy.cos(faz)
    if (cf==0):
        b=0.
    else:
        b=2. * numpy.arctan2 (tu, cf)
 
    cu = 1. / numpy.sqrt(1 + tu * tu)
    su = tu * cu
    sa = cu * sf
    c2a = 1 - sa * sa
    x = 1. + numpy.sqrt(1. + c2a * (1. / (r * r) - 1.))
    x = (x - 2.) / x
    c = 1. - x
    c = (x * x / 4. + 1.) / c
    d = (0.375 * x * x - 1.) * x
    tu = s / (r * a * c)
    y = tu
    c = y + 1
    while (numpy.abs (y - c) > EPS):
 
        sy = numpy.sin(y)
        cy = numpy.cos(y)
        cz = numpy.cos(b + y)
        e = 2. * cz * cz - 1.
        c = y
        x = e * cy
        y = e + e - 1.
        y = (((sy * sy * 4. - 3.) * y * cz * d / 6. + x) *
              d / 4. - cz) * sy * d + tu
 
    b = cu * cy * cf - su * sy
    c = r * numpy.sqrt(sa * sa + b * b)
    d = su * cy + cu * sy * cf
    glat2 = (numpy.arctan2(d, c) + numpy.pi) % (2*numpy.pi) - numpy.pi
    c = cu * cy - su * sy * cf
    x = numpy.arctan2(sy * sf, c)
    c = ((-3. * c2a + 4.) * f + 4.) * c2a * f / 16.
    d = ((e * cy * c + cz) * sy * c + y) * sa
    glon2 = ((glon1 + x - (1. - c) * d * f + numpy.pi) % (2*numpy.pi)) - numpy.pi    
 
    baz = (numpy.arctan2(sa, b) + numpy.pi) % (2 * numpy.pi)
 
    glon2 *= 180./numpy.pi
    glat2 *= 180./numpy.pi
    baz *= 180./numpy.pi
 
    return (glon2, glat2, baz)

def equi(m, centerlon, centerlat, radius, color):
    """
    This function enables A95 error ellipses to be drawn in basemap around paleomagnetic poles in conjunction with shoot
    (from: http://www.geophysique.be/2011/02/20/matplotlib-basemap-tutorial-09-drawing-circles/).
    """
    glon1 = centerlon
    glat1 = centerlat
    X = []
    Y = []
    for azimuth in range(0, 360):
        glon2, glat2, baz = shoot(glon1, glat1, azimuth, radius)
        X.append(glon2)
        Y.append(glat2)
    X.append(X[0])
    Y.append(Y[0])
 
    X,Y = m(X,Y)
    plt.plot(X,Y,color)

def poleplot(mapname,plong,plat,A95,label,color='k',marker='o'):
    """
    This function plots a paleomagnetic pole on whatever current map projection has been set using the basemap plotting library.

    Parameters
    -----------
    mapname : the name of the current map that has been developed using basemap
    plong : the longitude of the paleomagnetic pole being plotted (in degrees E)
    plat : the latitude of the paleomagnetic pole being plotted (in degrees)
    A95 : the A_95 confidence ellipse of the paleomagnetic pole (in degrees)
    label : a string that is the label for the paleomagnetic pole being plotted
    color : the color desired for the symbol and its A95 ellipse (default is 'k' aka black)
    marker : the marker shape desired for the pole mean symbol (default is 'o' aka a circle)
    """
    centerlon, centerlat = mapname(plong,plat)
    A95_km=A95*111.32
    mapname.scatter(centerlon,centerlat,20,marker=marker,color=color,label=label)
    equi(mapname, plong, plat, A95_km,color)

def vgpplot(mapname,plong,plat,color='k',marker='o'):
    """
    This function plots a paleomagnetic pole on whatever current map projection has been set using the basemap plotting library.

    Parameters
    -----------
    mapname : the name of the current map that has been developed using basemap
    plong : the longitude of the paleomagnetic pole being plotted (in degrees E)
    plat : the latitude of the paleomagnetic pole being plotted (in degrees)
    color : the color desired for the symbol and its A95 ellipse (default is 'k' aka black)
    marker : the marker shape desired for the pole mean symbol (default is 'o' aka a circle)
    """
    centerlon, centerlat = mapname(plong,plat)
    mapname.scatter(centerlon,centerlat,20,marker=marker,color=color)