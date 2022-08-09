#This file conains data processing functions
#called from AssignMALDI_Win
##030821 Converting to python3x

import sys,os
sys.path.insert(1, r'./../functions')  # add to pythonpath

from isotope_ed import isotope_fun
from bisect import bisect_left
import math
from pickpk_lmp import pickpk
from common import *


def convertcomp(comp):
	#takes in chemical formula and makes a list in a specific order
	#input composition is C20H38O11Na1
	#output should be [38,20,(n),11,(s),0]
	comp = comp.replace('\n','')
	alist=[0,0,0,0,0,0]
	order=['H','C','N','O','S','X']
	for i,c in enumerate(order):
		
		if c in comp:
			
			num = getint(comp,comp.find(c)+1)
			try: num = int(num)
			except: print ('skipping '+num); pass
			alist[i]=num
		
	return alist
	
def getint(astr,i):
	#Gets an int at or after i
	#i is where to start in A23B22
	#called from convertComp
	val=''
	while i<len(astr):
		c=astr[i]
		if c>='0' and c<='9':
			val+=c
		else:
			try: val = int(val); break
			except: return 0
		i+=1
	return val
	
def takeClosest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.
    If two numbers are equally close, return the smallest number.
    """
    #called from matchMasses
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0],0
    if pos == len(myList):
        return myList[-1],len(myList)
    before = myList[pos - 1]
    after = myList[pos]
    
    if after - myNumber < myNumber - before:
       return after, pos
    else:
       return before,pos-1	
	

def getMax(i4,i2,wh):  #masses, intensities
	#called from matchMasses
	maxi=0;co=0
	for r in range(0,len(i4[wh])):
		if i2[wh][r]>maxi: maxi=i2[wh][r]; co=r
	return co	
	

def getIsoInts(i2,pki,wh=0):
	#Converts iso %s to intensities based on first peak in picked series
	#i2 = isotopic intensity list from a series
	#pki=pk intensity from pk of interest
	i2adj=[]
	bpk=pki/i2[wh] #finds OF based on first peak (IS)/%
	for per in i2:  #isotopic intensities from one assignment
		i2adj.append(bpk*per)  #% * of = is
	
	return i2adj

def teststart(ui):
    pklist = processData([],ui,ui.infiles[0],0) #returns picked peaks
    spath=os.path.dirname(os.path.realpath(sys.argv[0]))
    nufile=os.path.join(spath,ui.pickedpks)
    write2DList(nufile,pklist,'w')
    return nufile
    

def subtractLists(alist,blist,limit=False):
    #subtract b from a
    #bstart tells where to start in b
    #limit says to only subtract parts of list that exist if true
    sublist=[]
    for a,b in zip(alist,blist):  sublist.append(a-b)
    if len(alist)>len(blist) and limit==False: sublist+=alist[len(blist):]
    if len(blist)>len(alist) and limit==False: 
        for b in blist[len(alist):]: sublist.append(-1*b)
    
    return sublist


def firstOrBiggest(iints,alist,test=False):
    #iints are isotopic intensities.  alist is a list of adjusted intensities
    #called from compareToPrediction
    ria=[];mins=''
    ia0 = getIsoInts(iints,alist[0],wh=0)#wh shifts up since we don't know the intensities before 0
    ia0dif = subtractLists(alist,ia0)
    #if test==True:print('alist',alist);print('ia0',ia0);print('dif',ia0dif)
    asum=sum([abs(d) for d in ia0dif]) #total differences for each r
    if not mins: mins=asum; ria=ia0  #save smallest differences
    elif mins>asum: mins=asum;ria=ia0
    #if test==True: print('asum0',asum)
    im = alist.index(max(alist))
    iam = getIsoInts(iints,alist[im],wh=im)#based on biggest peak
    iamdif = subtractLists(alist,iam)
    #if test==True:print('iam',iam[:5])
    msum=sum([abs(d) for d in iamdif]) #totals absoluted differences for each r
    if mins>msum: mins=msum;ria=iam
    #if test==True: print('asumBig',asum,msum,mins)
    return ria,mins    
        
def compareToPrediction(pks,iints,X,Y,err):
    #pks is peak series of interest = [[mass,area,XYiteratr,unadjusted area,times used]]
    #iints=isotopic intensities from a series
    #overlap is taken care of in pickpatterns::
    #  A rough iterwin by area is deleted from peak patterns
    #  before getting next peak pattern.  
    #  the adjusted area is at ii=1 in pks while the original area is at ii=3
  
    tf=False #testing flag
    #if 1905<pks[0][0]<1906: tf=True
    besti=[];ms=0
    ys = [Y[pk[2]] for pk in pks] #gets actual intensities
    yu = [pk[-1] for pk in pks] #gets whether used or not
    if tf==True: 
        print ('ys',ys)
        for pk in pks: print('>',pk[-1])
    for e,yused in enumerate(yu[1:5]): #see if any peaks have no overlap
        if tf==True: print('0',getIsoInts(iints,ys[0],wh=0))
        if yused==1:
            besti = getIsoInts(iints,ys[e+1],wh=e+1);
            sublist=subtractLists(ys,besti,limit=True)
            avg,std=astdev(sublist[1:5]) #c12 pk causing issues for higher mw
            if tf==True: print('besti',besti);print('sublist',sublist)
            if avg<1:besti=[]
            if tf==True: print('avg',avg,std)
            #print('using',pks[0][0],e+1,avg,len(besti));
            break
        
    if not besti:
        yadj = [pk[1]/pk[3]*yi for yi,pk in zip(ys,pks)] #gets adjusted intensities
        besti,ms=firstOrBiggest(iints,yadj,test=tf)
    if tf==True: print('ys',ys);print('besti',besti)
    area=0;isom=[];isoi=[]
    for pk,bi in zip(pks,besti): #this will stop at shortest list
        area+=bi/Y[pk[2]]*pk[3] #percent difference times calculated area of the whole peak
        isom.append(pk[0])
        isoi.append(bi)  #this is just to make lists the same length below
    
    #if tf==True: exit()
    return area,isoi,isom


def matchMasses(X,Y,pks,isodm,infile,pltnum,ui):
	#called from processData
	#X=mass list from spectra
	#Y=int list from spectra
	#pks = picked = list of list of [mass,area,midpoint Xiter,unadjusted.area]
	#isodm = isotopic patterns by mass [mass,[masslist,intenlist,name]]
	#axl = list of plot axis
	
		
	isodm.sort()  #lowest mass first?
	i1=[]; i2 = []  #separate into 2 lists
	i3=[]
	i4=[];i5=[];i6=[]
	err=ui.error
	ca=0
	for a,b in isodm:  #isotopic patterns
		i1.append(a)	#monoisotopic mass predicted
		i2.append(b[1])  #intensities %s
		i3.append(b[2])  #names
		i4.append(b[0])  #masses
		whm=getMax(i4,i2,ca) #returns ii to highest intensity
		i5.append(whm) #where mass and intensity with most intensity in that set
		i6.append(b[0][whm])  #biggest mass (centroid)
		ca+=1
	
	mX=[]  #stores matches
	mY=[]
	labels=[]
	#matches filter if first peak and 2nd peak 
	isowin=[]
	isowhere=[]
	totarea=[]
	matches=[]
	masses=[]

	for i,pk in enumerate(pks):  # pk = list of peaks in series
		mass,ara,midi,yy,tu = pk[0]  #[mass,area,midpoint Xiter,unadjarea,times used]
		error=err
		area=0;i2adj=[];isom=[]
		#compares library masses (i1) to picked peak mass
		answ = takeClosest(i1,mass) #close = value, where = iter in i1 & i2 &labels
		close,where=answ #where is iosotope iter.  Close is isotope mass
		
		if where>=len(i1): continue  #was causing error further down
		go=False
		if mass>3000: #mainly to avoid first of list problem, but blob pks start here
			if 0<(mass-close)<3 and mass-pks[i-1][0][-1]>3: #pkmass is within 3 daltons higher than library mass and there's no close mass to the left
				area,i2adj,isom=centerSearch(i2[where],i5[where],i6[where],pks[i],Y)
				if area>0:go=False;True
		if abs(mass-close)<=error: # and abs(X[start]-close)<=err:  #found match
			
			#need to get intensities at masses that match intensities in i2adj = i4[where]
			ee=i-1;iw=[]
			if i==0: ee=0;
			
			area,i2adj,isom = compareToPrediction(pk,i2[where],X,Y,err)
			go=True
		if go==True:    
			if labels:
				if i3[where]==labels[-1]: #same as before!
					if area<totarea[-1]: continue  #smaller than before
					#else the new peak is larger - use it.
					isowin[-1]=i2adj; isowhere[-1]=isom
					mX[-1]=pk[0][0];mY[-1]=Y[pk[0][2]]
					totarea[-1]=area
					continue
			isowin.append(i2adj)  #list of predicted intensities
			isowhere.append(isom) #list of predicted masses
			mX.append(pk[0][0])#mass 
			mY.append(Y[pk[0][2]])#realInt
			labels.append(i3[where])
			totarea.append(area)
			
			masses.append(mass)

	nulabels,nuX,nuY,nutotarea,numasses,skips = sumMod(labels,mX,mY,totarea,masses,ui)#adds -32 pk intensity to main pk
	nufile=output1(nulabels,nuX,nutotarea,infile,numasses)	#goes to tables
	ui.pfiles.append(output2(labels,mX,mY,infile,masses,isowhere,isowin,skips)) #holds processed data to insert into spectra
	
	return nufile

def centerSearch(iints,iwh,bmi,alist,Y):
    #what if blob peak or higher MW?  Can I identify using biggest iterator?
    #bmi = biggest mass of iterator. alist = ten pks close to search for mass;iwh=where mass is biggest in iso
    #iints = iso int % intensities
    #called from matchMasses
    pks =[];maxi=0;ints=[];mi=0 #maxi=max intensity;ints=list of pkIntensities
    #first get rid of extra peaks.
    
    i=0
    for pk in alist[1:]:
        i+=1
        if pk[0]-alist[i-1][0]<=2: #current pk mass - previous pk mass
            pks.append(alist[i-1]) #cluster peaks within 2 daltons of each other
            ints.append(Y[alist[i-1][2]]) #intensities
            if ints[-1]>maxi: maxi=ints[-1]; mi=i-1 #save max int and location
        else: break
    if len(pks)<3: return 0,[],[] #want at least 3 peaks in our blob
    #now see if bmi matches a peak
    st=mi
    if mi>0: st=mi-1
    isoints=[]

    for i,pk in enumerate(pks[st:mi+1]):  # biggest peak and one on either side.
        mass,ara,midi,yy,tu = pk  #[mass,area,midpoint Xiter,unadjarea,times used]
        if abs(mass-bmi)<0.5:  #match to biggest peak
            isoints=getIsoInts(iints,maxi,iwh)#isopercents,max pk intensity,which isoint to use

    if not isoints: return 0,[],[] #nothing found
    #add missing peaks based on isowin.  need mass,int,area
    ratio = pks[mi][1]/bmi #ratio of biggest pk area to biggest isoints

    sub=iwh #assumes 1Da z.  biggest isomass - iterator = starting mass
    area=0;isom=[];isoi=[]
    for bi in isoints[:10]: #cut off at 10 
        area+=bi*ratio #percent difference times calculated area of the whole peak
        isom.append(bmi-sub);sub+=1
        isoi.append(bi)  #this is just to make lists the same length below
    

    return area,isoi,isom
		
					
def matchAssignments(X,Y,pks,isodm,infile,pltnum,ui,alist):
	#called from processData
	#assignments already verified by user.  Just need to get area and redo files.
	#X=mass list from spectra
	#Y=int list from spectra
	#pks = picked = iterator in list (first,mid,last)..now list of list of [mass,area,midpoint Xiter]
	#isodm = isotopic patterns by mass [mass,[masslist,intenlist,name]]
	#alist = list of assignments [label,mX,masses,mY]
	labels=[];mX=[];masses=[];mY=[]

	for a,b,c,d in alist: #previously assigned pks
		labels.append(a)
		mX.append(b)
		masses.append(c)
		mY.append(d)
	totint= [0]*len(mY)
	error=ui.error
	unass = [pk[0][0] for pk in pks] #list of picked,unassigned masses
	for e,mass in enumerate(masses): #already picked pks
	
		answ = takeClosest(unass,mass) #close = value, where = iter in i1 & i2 &labels
		close,where=answ #where is pks iter.  Close is unassigned mass
		
		if abs(mass-close)<=error: # and abs(X[start]-close)<=err:  #found match
			ilist=[];area=0;maxa=0;maxi=0
			for pip in pks[where]: #pks in series
				area+=pip[1]
			totint[e]=area
			
	nulabels,nuX,nuY,nutotint,numasses,skips = sumMod(labels,mX,mY,totint,masses,ui)#adds -32 pk intensity to main pk
	
	nufile=output1(nulabels,nuX,nutotint,infile,numasses) #prints off procpks.txt	
	
	
	return nufile


def updateAverages(ui):
	#coming from saveChanges in plot window
	#need to convert the new pks-gp files to pks.txt files, the call makeOutputFiles
	#reprocess everything but force new assignments!   
	nufiles=[]
	co=1
	for f,p in zip(ui.infiles,ui.pfiles):
		data=readFile(p,True,special='###') #name, foundmass,calcmass,int

		data = sorted(data,key=lambda x:x[2])#by mass?
		nufiles.append(processData(ui.glylist,ui,f,co,data))#returns procpks.txt file
		co+=1
	makeOutputFiles(ui,nufiles)
		
def getMaxY(X,Y,ui):
	#pulls out highest Y between limits of X set by user
	try: start=int(ui.mzstart); end=int(ui.mzend)
	except: return max(Y)
	maxy=0
	for x,y in zip(X,Y):
		if x>=start and x<=end:
			if y>maxy: maxy=y
	return maxy+(maxy*.05)        

def subMod(ui,name):
    #returns name without mod if mod is in it..Subtracts!
    #only one mod should be in each name.
    for mod in ui.mods:  #things subtracted or added such as incomplete pm
        ans=name.find(mod[0]) #returns index or -1
        if ans>-1: 
            name=name[:ans]+name[ans+len(mod[0]):]
    return name        
        
def sumMod(labels,mX,mY,totarea,masses,ui):
	#if a mod like -32, then need to add it into the results.
	#for testing calculate an average %  - if above, then adjust  accordingly and indicate own assignment?

	suml = []
	nuL=[];nuX=[];nuI=[];nuY=[]; nuM=[]
	for L,M,T,Y,mas in zip(labels,mX,totarea,mY,masses): #stick them all together so can sort
		suml.append([L,M,T,Y,mas])
	suml.sort()  #by label
	oldL=''; oldT='';oldM='';oldY=0; oldmas=0;skips=[];co=0
	for L,M,T,Y,mas in suml:
		co+=1
		aname = subMod(ui,L)
		if aname!=L: #something was subtracted, so mod exists.
			if aname==oldL: #mod peak and parent peak exist
				if T/oldT>0.5: print('check ',oldL,'! mod peak big',oldT,T)
				oldT+=T  #add mod to reg
			else: #mod peak with no parent
				skips.append(co)
		else: #parent peak
			if oldL:
				if not nuL or oldL!=nuL[-1] and oldL!=L:  #happens if modpeak without parent or if same assi twice
					nuL.append(oldL); nuX.append(oldM); nuI.append(oldT);nuY.append(oldY);nuM.append(oldmas)
				if L==oldL: #may be a repeat.  Take biggest if is
					if oldT>T: continue  #skip that peak.  Otherwise gets reset below
						
			oldL=L
			oldT=T
			oldM=M
			oldY=Y
			oldmas=mas
	#catch last
	if not nuL or oldL!=nuL[-1]:
		nuL.append(oldL); nuX.append(oldM); nuI.append(oldT); nuY.append(oldY);nuM.append(oldmas)
		
		
	return nuL,nuX,nuY,nuI,nuM,skips
	
def output1(labels,mX,totint,infile,masses):
	#output final masses including with -32pk added, for example.
	outfile=getbase(infile) #returns infile without .txt
	outfile += 'pks.txt' #adds pks.txt
	
	fout = open(outfile,'w')
	header = "Name\tFMass\tCMass\tIntensity\n"
	t='\t'
	fout.write(header)
	for i,l in enumerate(labels):
		line = l+t+'%.4f'%mX[i]+t+'%.4f'%masses[i]+t+'%.0f'%totint[i]+'\n'
		
		fout.write(line)
		
	fout.close()
	return outfile

def output2(labels,mX,mY,infile,masses,isowhere,isowin,skips):
	#outputs initial masses for use in graph.  Name: '57-1pks-gp.txt'
	#was going to a working directory, but if I want to save project for later, needs to go with data.
	#skips = iterators of modded assignments without parents - so skip!
	base=getbase(infile)
	base += 'pks-gp.txt'

	###May want to put a try statement here to avoid admin errors!
	#if not os.path.exists(wdir): os.makedirs(wdir)
	#outfile = os.path.join(wdir,base)
	fout = open(base,'w')
	header = "Name\tFMass\tCMass\tIntensity\n"
	t='\t'
	fout.write(header)
	
	for i,l in enumerate(labels):
		if i in skips: continue
		line = l+t+'%.4f'%mX[i]+t+'%.4f'%masses[i]+t+'%.0f'%mY[i]+'\n'
		fout.write(line)
	fout.write("###\n")
	co=-1
	for ir,iw in zip(isowhere,isowin):
		co+=1
		if co in skips: continue
		line = str(ir)+'\t'+str(iw)+'\n'
		fout.write(line)
	fout.close()
	return base
	
				
	

			
def averageList(files,ui,Hex=False):
	#from APL - edited to take in files [name,mass,int]
	#list = expected [name,mass,???,[data1 name,mass,area,%abun],[data2 name,mass,area,%abun]]
	#If Hex = false don't include Hex or sugs with HexNAc1 in natural abundance calc and don't output
	#NOTE: When done, total percentage won't = 100 because average of all files.  It should = 100 for individual files
	
	nulist=[]
	nudic={} #name:[mass,[inte]]
	
	permonol={}
	performl=[0,0,0,0]  #store #without dhex or sa, #with just dhex, with just sa or with both
	start,end = os.path.split(files[0])
	start,end = os.path.split(start)
	
	for f in files:
		fin=open(f,'r')
		namel=[]
		massl=[]
		intl=[]
		intl2=[]
		calmass=[]
		#1. get data from file
		for line in fin:
			
			if 'Name' in line: continue #header
			name,cmass,mass,inte=line.split()
			###FILTERS for N-glycans!
			if Hex==False:
				ad = makeDictFromName(name)
				if 'HexNAc' not in ad: continue
				if 'HexNAc' in ad: 
					if ad['HexNAc']<2:continue
				#if name=='HexNAc2': continue  #throwing off % abundance
			
			namel.append(name)
			massl.append(float(mass))
			intl.append(float(inte))
			calmass.append(float(cmass))  #calculated mass  #should be the same for same assignments
		fin.close()	
		if not intl: continue
		
		#2. calculate %abundance
		totsum = sum(intl)
		maxnum = max(intl)
		perint=[] 
		for i,inte in enumerate(intl):  #for each intensity
			
			try:
				intl2.append((inte/float(totsum))*100)  #% abundance
				perint.append((inte/float(maxnum))*100)  #what about % of greatest
			except: intl2.append(0); perint.append(0)	
		
		permono={'Hex':0,'HexNAc':0,'NeuAc':0,'dHex':0}#061718 for perMono
		for i,n in enumerate(namel): #for each label
			lets,nums = getSugNums(n)  
			for sug,num in zip(lets,nums): #i.e. hex,2
				try: permono[sug]+=num*intl2[i]
				except: pass
			#for average	
			if n not in nudic:
				nudic[n]=[calmass[i],[massl[i]],[intl2[i]],[perint[i]],[intl[i]]] #list of [mass,[%abun],[pergreatest],[percent area]]
			else:  #makes lists of %abun and %highest so can average below
				nudic[n][1].append(massl[i])
				nudic[n][2].append(intl2[i])  #add onto inte list
				nudic[n][3].append(perint[i])
				nudic[n][4].append(intl[i])
			
		for k,v in permono.items():  #get lists of each type
			if k not in permonol: permonol[k]=[]
			permonol[k].append(v)
	
	for name,alist in nudic.items():  #contains info from each file for each assignment
		
		if len(files)==1:
			nulist.append([name,myround(alist[0],2),myround(alist[1][0],2),
				str(myround((alist[0]-alist[1][0])/(alist[0]*1e-6),1)),
				alist[2][0],0,alist[3][0],0,1]+alist[4]) #alist[0]=mass
			continue
		if len(alist[1])<ui.minfile: continue
		avg0,std0=astdev(alist[1])  #for found mass
		avg1,std1=astdev(alist[2])  #for %abundance
		avg2,std2=astdev(alist[3])  #for percent of highest
		avg3,std3=astdev(alist[4])  #for area
		delta = str(myround((avg0-alist[0])/(avg0*1e-6),1))
		astr = str(myround(avg0,2))+' +/- '+str(myround(std0,2))
		#calculate percent with each type-051320
		if 'dHex' in name:
			if 'NeuAc' in name: performl[3]+=avg1
			else: performl[1]+=avg1
		elif 'NeuAc' in name: performl[2]+=avg1
		else: performl[0]+=avg1
		nulist.append([name,myround(alist[0],2),astr,delta,avg1,std1,avg2,std2,len(alist[1])]+alist[4]) #alist[0]=mass
		
	mono=[end]  #mutant name	
	if permonol:	
		mono+=astdev(permonol['Hex'])+astdev(permonol['HexNAc'])+astdev(permonol['dHex'])+astdev(permonol['NeuAc'])
	
	return nulist,[mono]  #mono is [name, avg+std of hexoses, avg+std of N's, avg+std of D's, avg+std SA]
	
def getSugNums(astr):
	#gets numbers from long hand list
	#called from AverageList
	lets=[]
	nums=[]
	
	co=0
	tn=''  #tempnum
	tl=''  #templet
	
	for ch in astr:
		if ch.isalpha() or ch=='*': 
			tl+=ch
			if tn: nums.append(int(tn)); tn=''
		else:
			tn+=ch
			if tl: lets.append(tl) ; tl=''
	if tn:
		try: anum = int(tn)
		except: anum = getTotalNum(tn)  #in case '-' in number -happens at end
		nums.append(anum); tn=''  #catch last
	if tl: lets.append(tl) ; tl=''  #shouldn't happen
	
	return lets,nums


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

def subtractBaseline(X,Y,baseline):
	#baseline=[[x,y]] may not start on X. So use first or most recently passed bx as baseline
	nuY=[]; eb=0; bx=baseline[eb][0]; 
	for x,y in zip(X,Y):
		if x>bx and eb<len(baseline)-1:  eb+=1  #I'm assuming x will never skip, but bx might
		by = baseline[eb][1]
		nuv=y-by
		if nuv<0: nuv=0
		nuY.append(nuv)
	return nuY	
			

def findClosest(alist,val,wh):
    #returns value and iterator in 2Dlist.
    #wh is where in 2D list
    ans=alist[min(range(len(alist)),key=lambda i: abs(alist[i][wh]-val))]
    ii=alist.index(ans)
    
    return ans,ii  #ans is a list from the 2D list

def guessIsowinArea(mass,area):
	##Calculate areas for isowin?
	win=[]
	win.append(1.0048*math.exp((-5.719e-4)*mass))
	win.append(-0.7813+1.1228*math.exp(-0.5*(math.log(mass/1736.3154)/1.7195)**2))
	win.append(0.0825+0.1694*math.exp(-0.5*(math.log(mass/3319.5970)/0.6294)**2))
	win.append(0.0185+0.1949*math.exp(-0.5*(math.log(mass/5407.1746)/0.7066)**2))
	win.append(0.0043+0.2093*math.exp(-0.5*(math.log(mass/8648.3239)/0.7315)**2))
	#ma=max(win)  #peak with maximum area
	#ind = win.index(ma)
	total = area/win[0]  #assumes first peak in series
	areas=[]
	for w in win:
		areas.append(w*(total))
	return areas #, ind  #list and index of max intensity


def pickPatterns(X,Y,pklist,derr,ca=True,perr=0.1):
	#perr=in percent, derr=dalton error
	#ca = calculate area.  Only do first time
	#baseline = [int]
	#figured out slopes of each isotope mass vs. (int1-int2)/int1 = linear.
	#can I use them to pick isotopic windows?  Will iterate through list, subtracting windows each time till all picked.
	#slopes up to five isotopes peak:(slope,y-intercept)
	#092921 - issues with overlaps.  try using isotopic wins to adjust areas.
	areas=pklist
	nuY=Y[:]#baseline 
	if ca==True:
		areas = calcArea2(X,nuY,pklist) #returns mass,area,Xiterator(mid)
	else: areas=pklist
	
	plist=[] #pattern list
	nua=[a for a in areas]  #simple copy was affecting areas when nua changed
	nc=0
	isoareas=[]; maxlen=len(nua)
	rejects=[]  #for testing
	
	while nc<maxlen:  #for each peak
		tf=False
		#if 4314<nua[nc][0]<4315: tf=True
		if tf==True: print('1070START',nua[nc])
		x,a,it = nua[nc][:3] #mass, area,iter of picked peaks
		
		if len(nua[nc])<4: nua[nc]+=[a,0]  #adds area to 4th position and times used to 5th
		if tf==True: print('MASS',nua[nc])
		nd=nc; nc+=1
		if a<=0: continue #no area, skip
		
		series = []; temp=[];isoa=0
		##Grab 10 picked peaks from list
		temp=nua[nd:nd+11] #only first has yy at end.
		
		##initialize series
		series.append(temp[0])  #first peak to start
		e=0;elist=[nd]  #temp counter
		while e <len(temp):  #first 10 peaks in case of overlap - just need 5 
			xo=series[-1][0]  #get mass of last peak added
			##find closest peak 1 dalton away
			ans,e=findClosest(temp,xo+1,wh=0) #+1= a dalton
			if e==-1: break  #not found
			if tf==True: print ("error test",abs(ans[0]-(xo+1)),'vs',derr/2)
			div=2
			if xo>3000: div=1  #for blob peaks
			if abs(ans[0]-(xo+1))>derr/div: break #more than a dalton away
			if len(temp[e])==3: temp[e]+=[temp[e][1],0] #add area to fourth position and times used to 5th
			series.append(temp[e])
			elist.append(nd+e)
		if tf==True: print('SERIES',len(series),series)
		if len(series)<2: continue 
		##get isowin areas
		isoareas = guessIsowinArea(x,a)#findBestIsowin(series)
		silist=[s[1] for s in series] #areas
		if tf==True:print('SC ',series[0][0],silist,'**',isoareas)
		if slopeCheck(silist,isoareas)==False:
			yints=[Y[s[2]] for s in series]  #try it with intensities!
			if tf==True: print('WITH INTS',yints)
			if slopeCheck(yints,isoareas)==False:
				if tf==True:print('1105 slopecheckfail')#,series[0][0],silist,'\n',isoareas)
				continue
		##go through series and adjust a as needed based on isowin
		nuseries=[]
		for e,s in enumerate(series):
			x,a,it,aa,tu=s
			if e<len(isoareas):  #isoareas only 5 pks long
				isoa = isoareas[e]
			else:
				if isoa<100: break  #way down in noise
				else: isoa=isoa/2  #will be small, just decrease it
			ratio=1
			if a!=0 and isoa!=0: ratio=min([a,isoa])/max([a,isoa])
			tu+=1 #true if new series is longer than 1!
			if isoa>=a or ratio>0.9: 
				nua[elist[e]]=[x,0,it,aa,tu] #used up whole area a,y stay the same

			if a*0.9>isoa: 

				nua[elist[e]]=[x,a-isoa,it,aa,tu] #append what's left of a and y for next series
				a=isoa

			if tf==True:print('FINAL',x,a,isoa,aa,nua[elist[e]])
			nuseries.append([x,a,it,aa,tu]) #append a and y of this pk/series
			
		if tf==True: print('series',nuseries)
		if len(nuseries)>1: plist.append(nuseries)
		else: rejects.append(nuseries)
	#need to update times used in stuff saved earlier
	os=[0]#iterators to old series
	for f,series in enumerate(plist[1:]): #for each series
		for p1 in series:#for eack peak in series
			poplist=[]
			for e,ii in enumerate(os):  #for each old series
				if plist[ii][-1][0]<p1[0]:poplist.append(e);continue
				for g,p2 in enumerate(plist[ii]):   #for each pk in old series
					
					if p2[2]==p1[2]:plist[ii][g][4]+=1;break #was used in next series

			poplist.reverse()
			for n in poplist: #go backwards since list is getting shorter!
				os.pop(n)
		os.append(f+1)    
	
	return plist        


def slopeCheck(alist,blist):
    #isotopic windows past 2K go up then down, make sure window has same pattern as peaks
    #alist/blist = 1D lists of intensities.  Assume blist is isowin, alist is data
    #Can only test for unexpected negative slopes - overlap can cause unexpected upper ones
    maxb=max(blist);mbi=blist.index(maxb)
    maxa=max(alist);mai=alist.index(maxa)
    if alist[0]==maxa and blist[0]==maxb: return True #both slope down
    co=0;close=True
    for a,b in zip(alist,blist): #slope in that fuzzy range - see if all pks w/n 10% of max
        if abs(a-b)/maxa>0.1: close=False
        co+=1
        if co==max([mbi,mai]): break #limit comparison cause may be overlap
    if close==True: return True
    if mai<mbi:  #alist goes down while blist still going up
        if mai+1!=mbi: return False #possibly intensities of c12x and c12x+1 pks really close but c12x+1 should ==mbi
        if len(alist)>mai+1:
            if alist[mai+1]/alist[mai]>0.9 and blist[mbi-1]/blist[mbi]>0.9:
                return True #c12x and c12x+1 close intensities
        return False
    else: mai=mbi
    
    bslope = (maxb-blist[0])/(mbi+1) #treating X is 0,1,2,3,etc
    aslope = (maxa-alist[0])/(mai+1) #+1 avoids 0
    if bslope>0 and aslope>0: return True #both are positive

    return False

def calcArea2(X,Y,pklist):
	#Can I do this for broad peaks AND take into account gross overlap?
	#datai = iterators to peaks
	#range = all iterators to peaks in isotopic window
	#make sure dataints not too far from iosints...will do later
	alist=[]  #stores mass,area,miditerator
	for s,m,e in pklist: #start, middle, end
		area=0
		for ci in range(s,e+1):  #iterators I hope
			wid=X[ci+1]-X[ci]
			ls=Y[ci];ll=Y[ci+1]  #leg short, long leg
			if ls>ll: ll=ls; ls=Y[ci+1]
			area += (wid*ls)+(wid*(ll-ls)/2)  #rectangle + triangle
		alist.append([X[m],area,m])
	return alist			#mass,area, miditerator
	
	
def write2DList(fileout,alist,flag):
	#if testFile(fileout)=="False": print "Could not open ",fileout; return
	fout = open(fileout,flag)
	
	for row in alist:
		line=''
		for i,item in enumerate(row):
			try: line+=item
			except: line+=str(item)
			
			if i<len(row)-1:
				line+='\t'
		line+='\n'
		fout.write(line)
	print("Writing",fileout)
	print("\nALL DONE!")
	fout.close()
	
def orderList(data,ui):#glylist,useall='False'):
	#order by mass and glylist.  Apply filters to what is output
	#if useall==True then include everything in lib even if not found
	#if useall=allN include everything with >1HexNAc. someN=only assigned N-glycs
	#data format = [name,mass,avgint,stdev]
	#glylist format = [name,mass,chemicalformula]
	glylist = ui.glylist
	useall = ui.useout
	if ui.oligos=='yes': #save N-glycans only
		if ui.useout=='True': useall='allN' #outputs all assigned or unassigned N-glycans
		else: useall='someN'
	
	adict={}  #store name and where for data
	header=['sugar','calcmass','avgmass(Da)','delta(ppm)','%abun','std','%max','std','#files']
	nulist=[header]
	linelen=len(glylist[0])
	data = sorted(data,key=lambda x:x[1])#by mass
	glylist = sorted(glylist,key=lambda x:x[1])#by mass
	dc=0;gc=0 #counters
	dline=[]; gline=[]
	while(dc<len(data) or gc<len(glylist)):
		if dc<len(data):dline=data[dc];
		if gc<len(glylist):gline=glylist[gc]
		if dline[0]==gline[0]:  #library name matches assignment
			if dc<len(data):  nulist.append(data[dc]) #
			dc+=1; gc+=1; continue
		if dline[1]<gline[1] or gc>=len(glylist): #an assignment not in library
			if dc<len(data):  nulist.append(data[dc]); dc+=1 #make sure just not at end of data
			
		if gline[1]<dline[1] or dc>=len(data): #an assignment only in glylist
			if useall=='someN' or useall=='allN':  #print only expected N-glycans
				name = gline[0];use=True 
				ad = makeDictFromName(name)
				if 'HexNAc' not in ad: use=False
				if 'HexNAc' in ad: 
					if ad['HexNAc']<2:use=False
				if '-' in name: use=False  #mods
				#if name=='HexNAc2': use=False  #throwing off % abundance
				if use==False: gc+=1; continue
			if useall=='True' or useall=='allN':
				nulist.append([gline[0]]+[0]*linelen); #prints blanks  
			gc+=1
				
	return nulist			
	

def getglylist(libf):
	#list of longname, mass, chemistry
	glylist=[]
	fin = open(libf,'r')
	for line in fin:
		glylist.append(line.split())
	fin.close()
	glist = [[a,float(b),c] for a,b,c in glylist] #get floats
	glylist =sorted(glist,key=lambda x:x[1])
	return glylist

def testmod(ui,name):
    #Mods are things like missed permethylation
    for mod in ui.mods:
        if mod[0] in name: return False
    return True
	
def getBuildingBlocks(ui,limit=750):
    #for GUESSING assignments
    #limit is maximum daltons of block
    bbdic={};err=.00005
    co=0;
    if not ui.glylist: ui.glylist=getglylist(ui.libfile) #might happen when open previous
    glist = ui.glylist #[[a,float(b),c] for a,b,c in ui.glylist]  #library[name,mass,chem]

    while(co<len(glist)):
        if testmod(ui,glist[co][0])==False: co+=1;continue #is mod in name?
        sdic=makeDicFromName(glist[co][0],ui)
        smass = float(glist[co][1])
        schem = makeDicFromName(glist[co][2],'') #puts atoms in dict, not sugs

        if len(sdic)==1: co+=1; continue #skip hexoses
        for a,b,c in glist[co+1:]: #name,mass,chem  #all but first
            b=float(b)
            if b-smass>limit: continue
            cdic=makeDicFromName(a,ui)
            if len(cdic)==1: continue #skip hexoses
            dicd=subtractDict_neg(cdic,sdic) #subtracts lower mass dic from d1
            ans=convertDicToString_special(dicd,ui.order)  #using order to make sure can compare in dic

            if '-' in ans: continue
            if ans not in bbdic: 
                bbdic[ans]=[b-smass, subtractDict_neg(makeDicFromName(c,''),schem)] #mass and chem diffs

        co+=1
    ui.blocks=[]
    for k,v in bbdic.items():
        ui.blocks.append([v[0],k,v[1]]) #mass,name,chem-dic
    ui.blocks.sort()
    
def getOrder(glylist):
    #gets user preferences for order and monosaccharides from incoming library
    #should be before monos (-14D) is added.
    order={} #holds mononame and order
    for name,mass,CF in glylist:
        #make list from name
        alist=convertStringToList(name)
        alist.reverse() #gives 2, HexNac, 5 Hex
        co=-1
        for part in alist:
            if isnum(part): continue  #skip numbers
            co+=1
            parts=part.split('*')  #in case tag
            sug=parts[-1]  #because tag sticks to the following sugar (*pp*Hex)
            if not sug: continue #tag was on end of sugar so gives ''
            if sug not in order: order[sug]=co
            else: 
                if order[sug]<co: order[sug]=co #will adjust co up only
   
    #now convert to list
    olist=[];r=0
    while len(olist)<len(order):          
        for k,v in order.items():
            if r==v: olist.append(k)
        r+=1
    olist.reverse()
    
    return olist       
           
def makeDicFromName(name,ui):
    #takes in Hex5HexNAc2.  Returns {'hex':5,'hexNac:2}
    #tags come after * and are repeated instead of numbered *aa*, *ab*.  NeuAc2*ab*Hex4
    #labels will be NeuAc*a, NeuAc*b - have to split count.
    #ui.torder is an attempt to figure out order of monos in labels from library instead of user question.

    def addToDic(astr,anum,ui):
        if anum:
            if astr not in adic: adic[astr]=0
            adic[astr]=int(anum); 
            astr=''; anum=''        
        return astr,anum    
    ####################    
    adic={}
    astr='';anum='';tagf=False;tags={}
    if ui:
        for mod in ui.mods:  #things subtracted or added such as incomplete pm
            ans=name.find(mod[0]) #returns index or -1
            if ans>-1: 
                addToDic(mod[0],1,ui)
                name=name[:ans]+name[ans+len(mod[0]):]
    for ch in name:
        if ch=='*': #will catch prior to isnumeric.
            if tagf==False: tagf=True; continue  #skip first '*'
            if tagf==True: #flags collected, now do something with them
                tagf=False; #set for next time
                tot=int(anum) #keep track of total tags added cause some tags may be either/or
                for tag,num in tags.items():
                    t1,t2 = addToDic(astr+'*'+tag,num,ui) #this will add ie. NeuAc*p
                    tot-=num
                if tot>0: t1,t2=addToDic(astr,tot,ui) 
                astr='';anum='';tags={}
            continue  #skip '*'
        if ch.isalpha():
            if tagf==True: 
                if ch not in tags:  tags[ch]=0
                tags[ch]+=1
                continue
            astr,anum = addToDic(astr,anum,ui)  #doesn't work if no anum  
            astr+=ch
        if ch.isnumeric():  anum+=ch
    astr,anum = addToDic(astr,anum,ui) #catch last if there
    return adic

def convertDicToString_special(adic,order):
    #order is order of keys.  Adic=name:num
    #special to handle tags...NeuAc*h and NeuAc become NeuAc2*h*
    #if negative though, tags won't work, so reject negatives.
    astr=''
    td = adic.copy()

    for o in order:  #for each monosaccharide (no labels)
        num=0;tags='*'
        for s,n in td.items():  #oligosaccharide dictionary (with labels)
            if n<0: return '-'
            parts=s.split('*')  #in case of labels
            if o==parts[0]:
                if len(parts)>1: tags+=parts[1]*n #catches tag.
                num+=n #catches total atoms

        if num!=0: #item matching o was found above
            if tags=='*': tags='' #no tags were found
            else: 
                tg=sorted(tags); tags="".join(tg);tags+='*'  #sorted/join puts in alphbetical order
            astr+=o+str(num)+tags

    return astr
	


def addMod(glylist,mass,CF,abbr,err):
	#for line in glylist, add a adjusted line
	#glylist is ['name','mass','chemical formula']
	#CF = chemical formula;
	nulist=[]
	for gn,gm,gf in glylist:  #full name, mass, formula

		tlist=[]
		tlist.append(gn+abbr)
		gm = float(gm)
		gm+=mass #mass will be negative
		tlist.append(str(gm))
		tlist.append(addNames(gf,CF)) #was if mass>0, but sending in -#s in cf now so can add.
		nulist.append(tlist)
	
	return nulist

def addNames(name1,name2,add=True):
	#name1 = 'H1N1', name2 = 'N2', return 'H1N3'
	dict1 = makeChemDic(name1)
	dict2 = makeChemDic(name2)
	ddict=sumDict(dict1,dict2)
	
	nustr = makeStringFromDic(ddict)

	return nustr		

def makeChemDic(name):
	nudic={}
	let=''
	num=''
	flag='let'  #start with letters
	for c in name:
		#assume letters are first
		if flag=='let':
			if testInt(c)>=0 or c=='-':	num=num+c; flag = "num"; continue
			else: let=let+c
		if flag=='num':
			if testInt(c)<0 and c!='-':  #not a number!
				nudic[let]=int(num)
				let=c; num=''
				flag='let'	
			else: num=num+c	
			
	if let!='' and num!='':
		nudic[let]=int(num)
	return nudic

def makeStringFromDic(adic):
	
	nustr=''
	for k,v in adic.items():
		nustr+=k
		nustr+=str(v)
	return nustr	
	
def IDMod(mod):
	#returns[mass,chem,name]
	#to add new, just update dictionary.
	mods={-14:[-14.026617,"C1H2","14"],-32:[-32.165,"C1H4O","32"],-28:[-28.053235,"C2H4","28"]}
	if mod in mods: return mods[mod]
	else: cout(mod+" not found.  Try editing IDMod")
	return []
	

def start(ui):
	#called from GO under mainWin
	glylist=getglylist(ui.libfile)  #returns [[longname,mass,chemical]]
	ui.order=getOrder(glylist)

	if ui.pmf=='yes': #look for incomplete permethylation
		temp=[]
		for modL in ui.mods:
			name,mass,chem = modL
			temp += addMod(glylist,mass,chem,name,ui.error)#returns only modified glycans, so add to list
		glylist+=temp

	ui.glylist=glylist[:]
	getBuildingBlocks(ui)
	
	nufiles=[]
	co=1
	for f in ui.infiles:
		nufiles.append(processData(glylist,ui,f,co))#returns nufile

		co+=1
	makeOutputFiles(ui,nufiles)


def makeOutputFiles(ui,nufiles):
	Hex=False
	if ui.oligos=='no': Hex=True
	if not nufiles: return
	data,mono=averageList(nufiles,ui,Hex=Hex)	#returns [name,mass,avgint,stdev]
	data=orderList(data,ui)#ui.glylist,useall=ui.useout) #order by library and list everything in lib if useall==true
	begin,end = os.path.split(ui.inputdir)
	
	write2DList(os.path.join(ui.inputdir,ui.outfile),data,flag='w')
	write2DList(os.path.join(begin,end+ui.outfile),data,flag='w')  #automatically copy sum file to previous directory with name of mutant
	#write2DList(os.path.join(begin,'HNS.txt'),mono,flag='a') ##mono is [name, avg+std of hexoses, avg+std of N's, avg+std of D's, avg+std SA]

def makeNewSpectrumFile(ui,infile,X,Y):
    xylist = [(x,y) for x,y in zip(X,Y)] #put baseline Y into xylist
    write2DList(infile,xylist,'w')#writes new peaklist

def saveProcFiles(infiles):
    #coming from GO.  Should just be original files that haven't been copied yet
    nufiles=[]
    for infile in infiles:
        path,end=os.path.split(infile)
        e,s = end.split('.')
        nuname=os.path.join(path,e+'-proc.'+s)
        copyFiles(infile,nuname)
        nufiles.append(nuname)
    return nufiles


def processData(glylist,ui,infile,count,asslist=[]):
	#called from start or updateAverages
	#glylist is sugar library,Count is file counter,asslist comes in from updateAverages
	fin = open(infile,'r')
	
	pklist,X,Y=pickpk(infile,ui) #returns picked list (baseX,mid,baseI) - all are iterators to X,Y
	if ui.cpp=='yes': return pklist
	if not pklist: return '' #returns a filename below, so no file here.
	makeNewSpectrumFile(ui,infile,X,Y) #rewrites spectrum file with zero'd baseline
		
	#along with matchmasses - some isos don't line up with peaks.
	pplist=pickPatterns(X,Y,pklist,ui.error,perr=0.1)  #[[mass,area, midpointiter],[...] for each system]]
	
	isodn={}  #by name
	isodm=[]  #by mass
	for name,mass,comp in glylist:  #library
		comp2 = convertcomp(comp) #gets just atom #s in a certain order
		massa,intea = isotope_fun(comp2)  #should return isotopic window lists, to be adjusted by Na mass.
		##for each peak in the library! = 9 peaks?
		massl = massa.tolist()  #converts to lists = mass
		intel = intea.tolist()  #intensity
		diff = float(mass)-massl[0]  #mass of library glycan - first mass in isotope list?  Diff about 24dalton
		ml=[]
		for m in massl:
			ml.append(m+diff) #adjust iso mass by sodium ion if there
		#adjust intel by percent of highest?
		maxi = max(intel)
		for i,m in enumerate(intel):
			intel[i]=m/maxi   #percent of maximum
	
		isodn[name]=[ml,intel]	#dictionary
		isodm.append([ml[0],[ml,intel,name]]) #list sorted by starting mass
	if asslist: #updating averages
		return matchAssignments(X,Y,pplist,isodm,infile,count,ui,asslist)
	return matchMasses(X,Y,pplist,isodm,infile,count,ui) #returns a file




def findByMass(X,ui,err=0.2):
    #compare X to glylist [[name, mass, chem]]
    found=[]; nulist=[]
    alist=ui.glylist
    for a,b,c in alist:
        if abs(float(b)-X)<=err: found.append(a+' '+str(b)+' '+c); nulist.append(a+'  '+str(round(X-float(b),3)))
    return nulist,found

def guessUsingBlocks(X,ui,limit=750):
    #called from assignMALDI_win
    #ui.blocks= [mass-diff,name-diff,chem-diff(dic)]; glylist=[name,mass,chem]
    glist = [[float(b),a,c] for a,b,c in ui.glylist]
    nulist=[];outlis=[];namel=[]
    if not ui.byoniclist: ui.byoniclist=readByonicDBfile(ui.byonicDB)
    if not ui.blocks: getBuildingBlocks(ui)
    for gm,gn,gc in glist:  #go through glylist [mass,name,chem] this time
        diff=X-gm  #wanted shift - mass from glylist.
        if diff<0-ui.error: break  #too small
        if diff>limit:continue  #too big
        for bm,bn,bc in ui.blocks: #see if a block matches the diff
            if abs(bm-diff)<=ui.error: #a match!
                G='' #will be Y if in human glycam database
                nudic=addDict(makeDicFromName(gn,''),makeDicFromName(bn,''))
                nuname=convertDicToString_special(nudic,ui.order)
                if '-' in nuname: continue
                cbd = checkByonicDatabase(ui.byoniclist,nudic)
                if cbd==True: G='Y'  #found
                if cbd==False: G='n' #not found in database
                if nuname not in namel: namel.append(nuname)
                else: continue  #already used.
                nudic=addDict(makeDicFromName(gc,''),makeDicFromName(bc,'')) #makes chemical formula
                nuchem=convertDicToString(nudic,['C','H','N','O','P','S','D','Na'])
                nulist.append(nuname+' '+str(round(bm+gm,4))+' '+nuchem)
                outlis.append(nuname+'  '+str(round(X-(bm+gm),3))+'  '+G)
      
    return outlis,nulist #outlist is input in pick peak window. nulist is name,mass,formula

def makeisotrace(aline,mass,intensity,ui):
	#called from AssignMALDI_win
	#send in mass, intensity, comp return isolist[[X],[Y]]
	parts = aline.split(' ')
	comp=''
	if len(parts)==1: #sent in assignment only.  Find closest comp
		alist,blist = findByMass(mass,ui,err=10)  #alist is ['name mass comp']
		tlist=[]
		for line in alist:
			p2 = line.split(' ')
			tlist.append(abs(float(p2[1])-mass),p2[2]) #[diff,comp]
		tlist.sort() #smallest difference first
		if not tlist: return [],[]
		comp = tlist[0][1] #get comp with closest mass
	if len(parts)==3: comp = parts[2]
	if not comp: return [],[]
	comp = convertcomp(comp)
	massa,intea = isotope_fun(comp)  #should return isotopic window lists, to be adjusted by Na mass.
	##for each peak in the library
	massl = massa.tolist()  #converts to lists = mass
	intel = intea.tolist()  #intensity
	diff = float(mass)-massl[0]  #mass of library glycan - first mass in isotope list?  Diff about 24dalton
	ml=[]
	for m in massl:
		ml.append(m+diff)
	#intel is in percent. adjust by intensity. first pk=max?
	maxi = intensity/intel[0]
	for i,m in enumerate(intel):
		intel[i]=m*maxi   #calculated intensity    
	return ml,intel

def checkByonicDatabase(blist,test):
	#making human glycan data file searchable 7-28-22
	#downloaded byonic file from https://data.glygen.org/. after search for 'human glycans' or just 'glycans'
	#input - "glytoucan_ac","byonic"
	#input - "G02438LG","HexNAc(1)dHex(2) % 484.174789"
	#test = HexNAc2Hex5 or NexNAc*ab*Hex5...comes in as dic from 'guessUsingBlocks'
	#returns true if found in database
	if not blist: return 'fail'
	#remove labels from test
	tsug={}
	for sug,num in test.items():
		if '*' in sug: parts = sug.split('*'); sug=parts[0]
		if sug not in tsug: tsug[sug]=num
		else: tsug[sug]+=num ; #add up labeled stuff with same sugar.  Compositions are same
	
	#now compare
	for bdic in blist:
		if len(bdic)!=len(test): continue #quick filter
		match=True
		for bsug,bnum in bdic.items():
			if bsug not in tsug: match=False;break #not a match
			if bnum!=tsug[bsug]: match=False;break
		if match==True: return True	
	return False
	
