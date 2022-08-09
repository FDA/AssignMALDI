
#python 3.x
import os,sys,math
import matplotlib.pyplot as plt
from common import mysplit

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial
    y=np.asarray(y)
    
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError as msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

def smooth(alist,win,ord):
	#using Savitzky-golay...window size, polynomial order
	X=[];Y=[]
	for x,y in alist:
		X.append(x); Y.append(y)
		
	ans=savitzky_golay(Y, int(win), int(ord), deriv=0, rate=1)
	
	nuy=ans.tolist()
	'''
	plt.plot(X, Y, label='Noisy signal')
	#plt.plot(X, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
	plt.plot(X, nuy, 'r', label='Filtered signal')
	plt.legend()
	plt.show()
	'''
	tlist=[]
	for x,y in zip(X,nuy): tlist.append([x,y])
	return tlist
	
	

def getdata(afile):
	alist=[]
	fin = open(afile,'r')  #should be m/z(space)intensity
	
	for line in fin:
		try:
			parts=mysplit(line)
			a=parts[0];b=parts[1]
			alist.append([float(a),float(b)])
		except: continue  #probably header.
	fin.close()	
	
	return alist

def astdev(alist,exp=0,twoD=False,dim=0):
	#exp = what happens if find peaks in only one file but they should be in 3?  exp says how many there should be and plugs in 0's to get a bigger stdev.
	#case where want to add up all values in 2D list: dim='all'
	blist=[]
	if twoD==True:  #Make a list of all positions at 'dim' spot in 2D list
		for line in alist:
			if dim=='all':
				for i in line: blist.append(i)
			else:
				blist.append(line[dim])
		alist=blist[:]	
	if exp==0: exp=len(alist)	
	for r in range(len(alist),exp):
		alist.append(0)	
	average = findAvg(alist)  #100716
	total = 0.0
	c=0
	for i in alist:
		total = total+((i-average)*(i-average))
		c+=1
	
	try:	#12/07/16
		stdev = math.sqrt(total/c)
	except: stdev=0	
	
	return average,stdev 		
	
def findAvg(list):
	#100716
	c=0
	total=0
	for i in list:
		total=total+float(i)
		c+=1
	if c==0: return 0
	return total/c		

def pickpeaks(alist,min):
	#alist is x,y coordinates.  X=m/z Y=intensity
	#min = minimum # of slopes to count as real
	slist=getlandscape(alist,min) #returns list of [['+',i1,i2]...]
	plist=[]
	ps=();pe=();pt=()  #pk start, pk end, pk top
	ns=False  #negative shoulder
	for t,i1,i2 in slist:
		
		if t=='+':  #start of peak
			ns=False
			mid=0
			if ps: #two postives runs in a row - shoulder on left
				if pt: #find midpoint iterator  #should be
					mid = int((pt[1]-pt[0])/2)  #find midpoint of zero part
				else: print ("Two positives in a row - weird")
				plist.append([ps[0],ps[1],mid+ps[1]])
	
			ps=(i1-mid,i2)
			
			pe=()  #should have already saved the peak I think after it came down.
			pt=()  #in case leftover from elsewhere
			
		if t=='0': 
			if ps or pe: pt=(i1,i2)  #save for a moment
			
		if t=='-':
			mid=0	
			if ps:  #prior positive slope
				#if pt: #find midpoint iterator
				#	mid = int((pt[1]-pt[0])/2)
				#else: mid = 0  #it's a difference so no change - use last ps or first pe
				plist.append([ps[0],mid+ps[1],i2])# middle of peak, first and last iterator
				ps=();pt=()

			if pe: #two negative runs in a row - shoulder on right
				mid=0
				if pt: #find midpoint iterator  #should be
					mid = int((pt[1]-pt[0])/2)
				else: print ("Two negatives in a row - weird")
				if ns==True:  #fix last peak
					
					plist[-1][2]+=mid
				plist.append([i1-mid,i1,i2])
				ns=True
				pt=()
	
				
				
			pe=(i1,i2)
	
	return plist
		
		
def getlandscape(alist,min,smoothed=True):
	#returns list of +,0,- for slopes
	#min = minimum # of slopes to count as real
	slist=[0] #list of [0,+,+,+,0,-,-,-]
	x1=alist[0][0];y1=alist[0][1]
	beg=0
	start=1
	if smoothed==False: start=2
	for x2,y2 in alist[1:]:  #starting at 1...was 2
		try: slope = (y2-y1)/(x2-x1)
		except: slope=0
		beg+=1
		x1,y1=alist[beg]
		ans='0'
		if slope>0: ans='+'
		if slope<0: ans='-'
		slist+=[ans]
		
	nulist=[]  #format [(type,i1,i2)].  type=+,-,0
	ot='z';oi=0;zoi=0
	for i,v in enumerate(slist):
		
		if v!=ot:  #change in slopes
			if ot=='+' or ot=='-':
				
				if (i-oi)>=min:  #030222
					nulist.append([ot,oi,i-1])  #should I use i-1 or i?
				else: #count as 0?	
					nulist.append(['0',oi,i-1])
			if ot=='0':
				if len(nulist)>0:
					if nulist[-1][0]=='0':  #last set was 0 too, so add them together
						nulist[-1][2]=i-1
					else: nulist.append(['0',oi,i-1])	
			ot=v	#reset
			oi=i
		
	return nulist	
		
def testplot(alist,xylist):
	#alist format = where pkstart,mid,end
	#xylist = m/z,intensity
	
	X=[];Y=[]	
	for x,y in xylist: X.append(x); Y.append(y)
	plt.plot(X,Y)
	plt.plot(alist,Y,c='r')
	plt.show()


def noisecalc2(alist,xylist,cutoff=1.0,range=40):
	#what if calculated a running average/stdev over a smaller range
	#range = # datapoints to calculate avg/std
	#cutoff = z-score, so 3.0>97% not within normal distribution or something like that
	#alist= picked peaks.  xylist=all points in spectra
	#first get intensity at each peak
	intpks=[]
	tpks=[]
	picked=[]
	running=[]  #holds peaks to be averaged
	avgl=[];preavg='';prestd=0;
	#noiseTest(alist,xylist,cutoff,range)
	for s,m,e in alist: #start,mid,end iterators
		if m>len(xylist):  #error if here
			print ('Error In pickpk 360 m',m,len(xylist))
			continue
		x,y=xylist[m]
		if len(running)<range:	running.append(y); tpks.append([s,m,e]); avgl.append((x,y)); continue
		avg,std = astdev(running)
		#prevent average from increasing due to abundance of tall peaks?
		if preavg=='': preavg=avg; prestd=std #first time
		if preavg>avg: preavg=avg; prestd=std #reset preavg
		if avg>preavg: avg=preavg; std=prestd #keep avg from going up.
		avgl.append((x,avg-std)) #Very weak baseline - basically used to get rid of deepest wells.
		z = (y-avg)/std
		if z >cutoff: picked.append([s,m,e])
		else: running=running[1:]+[y];tpks.append([s,m,e])
		
	return picked,avgl  #avgl=baseline		
	
def zeroBaseline(xylist,window=50):
    #uses iterators at end of each peak(plist) to pull out lowest points
    #Picks lowest y every window.  Window=m/z or mass
    def doit(olde,e,xylist,baseline,picked):
        temp = sorted(xylist[olde:e],key=lambda k:k[1])#lowest first
        where = len(temp)*0.05 #returns a Y 5% above lowest Ys
        lowX,lowY=temp[int(where)]
        picked.append((lowX,lowY))
        for x,y in xylist[olde:e]: 
            nuY=y-lowY
            if nuY<0: nuY=0
            baseline.append(nuY)
        return baseline,picked
        
    temp=[];baseline=[] #list of adjusted intensities
    picked=[]
    co=xylist[0][0] #start of X
    olde=0
    for e,XY in enumerate(xylist):
        x,y=XY
        if x>co+window: 
            baseline,picked=doit(olde,e,xylist,baseline,picked)
            co=x+window; olde=e
    if len(xylist)>olde:  #something left
        baseline,picked=doit(olde,len(xylist),xylist,baseline,picked)
        
    #testplot(picked,xylist)        
    return baseline
    
    
    

def twoPointCalibration(xylist,ui):
    #Calculate conversion similar to F to C conversion
    try: #convert entries to floats
        culow=float(ui.culow); cuhi=float(ui.cuhi)
        colow=float(ui.colow); cohi=float(ui.cohi)
    except: print("Could not perform two point calibration.  Check entries."); return xylist
    sub = colow-culow
    ratio = (cohi-colow)/(cuhi-culow)
    nuX=[]
    for x,y in xylist:
        nuX.append((x+sub)*ratio)
    for e,x in enumerate(nuX): xylist[e][0]=x
    return xylist    


def pickpk(afile,ui,min=1):
	#cutoff = z-score limit
	#cpp = check peak picking
	#min is # of ++ and -- to declare a peak.  
	#ui also has smord and smwin for smoothing
	cutoff = ui.cutoff
	if not cutoff: cutoff=2.0
	
	baseline=[]
	alist=getdata(afile)  #sorted by m/z.  (X,Y)
	if ui.smf=='yes':  #smooth data
		alist=smooth(alist,ui.smwin,ui.smord)  #only use if needed.
	if ui.zerob=='yes':   
		baseline=zeroBaseline(alist)#returns adjusted Y 10-19-21 was basline
	if ui.usecalib=='yes':    
		alist = twoPointCalibration(alist,ui)
	if not alist: print('could not read specrum file');return [],[],[]
	plist = pickpeaks(alist,min)
	
	plist,avglist = noisecalc2(plist,alist,cutoff)
	X=[]; Y=[]
	for x,y in alist: X.append(x); Y.append(y)
	if baseline: Y=baseline[:]#baseline is corrected Y
	return plist,X,Y 
	
def pickpk_Limited(afile,ui,X,min=3):
	#to pick peaks just near selected X.
	cutoff = ui.cutoff
	if not cutoff: cutoff=2.0
	cpp = ui.cpp
	
	alist=getdata(afile)  #sorted by m/z.  (X,Y)
	if ui.smf=='yes':
		alist=smooth(alist,ui.smwin,ui.smord)  #only use if needed.
	istart=0; iend=0  #iterators for list
	for x,y in alist: #define window of spectra to pull out
		if X>=x-2 and istart==0: istart=x
		if X>=x+10 and iend==0: iend=x ; break
	plist = pickpeaks(alist[istart:iend],min)
	plist,baseline = noisecalc2(plist,alist[istart:iend],cutoff)
	return plist,alist[istart:iend],baseline
