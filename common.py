#common stuff
#python 3.x
import os,sys,math
from shutil import copyfile as cff
#USEFUL THINGS
##To convert a dict to a list alist = dict.items()
##to sort a 2D list: sorted(alist,key=lambda x:x[where])  #(x[0],x[1],x[2]) for multidimensions
##to list all class varibles as a dict: dict1=vars(self.ui)
## string.replace(old,new)


def cout(str):
	#in case want to change output to somewhere else at a later time
	print(str)
	
def saveLastDir(mydir,fname='lastdir.txt'):
	spath=os.path.dirname(os.path.realpath(sys.argv[0]))
	nufile=os.path.join(spath,fname)
	olddir = spath
	try:
		fout=open(nufile,'w')
		fout.write(mydir)
		fout.close()
	except:
		cout("error writing old directory")
	
def getLastDir(filein='lastdir.txt'):
	#want to get last working directory.  Should be saved in program directory.
	#save last directory is global
		
	spath=os.path.dirname(os.path.realpath(sys.argv[0]))
	nufile=os.path.join(spath,filein)
	olddir = spath
	try:
		fin=open(nufile,'r')
		olddir = fin.readline()
		fin.close()
	except:
		pass
		
	return	olddir
	
def testFile(filein):
	try:
		with open(filein) as f:
			f.close()
			return True
	except IOError as e:
		cout("could not open file ",filein); return False
        
def checkPermissions(my_file,pri=False):
    #returns lists of permissions (r)ead,(w)rite,(e)xecute
    #failing every time.  Erg.  Was using to try and figure out error, but os.access has a bug
    #opening a file to read or write works even if this fails. 062922
    astr=''
    if not os.access('my_file', os.F_OK): 
        if pri==True:
            for ld in os.listdir(): print(ld,checkPermissions(ld,pri=False))
        return ''#'cannot access '+my_file # Check for existance of file
    if os.access('my_file', os.R_OK)==True: astr+='r'  # Check for read access
    if os.access('my_file', os.W_OK)==True: astr+='w'# Check for write access
    if os.access('my_file', os.X_OK)==True: astr+='e' # Check for execution access
    return astr

def readFile(filein,header,sp='\t',special=None):
    #sp is separator between columns in line
    #special is where function stops
    #if header==True, skip first line.
    fin=open(filein,'r')
    nulist=[]
    for line in fin:
        #print('line',line)
        if header==True: header=False; continue
        if special:
            if special in line: break
        parts = line.split(sp)
        temp=[]
        for p in parts:
            temp.append(tonum(p))
        nulist.append(temp)
    fin.close()

    return nulist
		
def appendFiles(topfile,botfile):
	#append botfile to the bottom of top file
	fin = open(botfile,'r')  
	fout = open(topfile,'a')
	for line in fin: fout.write(line)
	fout.close()
	fin.close()
	
	
def copyFiles_old(fromfile,tofile):
	#still in use even though it's 'old'
	fin = open(fromfile,'r')  #infile
	fout = open(tofile,'w') #outfile
	try:
		for line in fin:  #10-21-2021  Working fine yesterday now giving invalid argument errors at end of file.  fix with Try/Except.
			fout.write(line)
	except: pass
	fout.close()
	fin.close()
    
def copyFiles(fromfile,tofile):
    cff(fromfile,tofile)
    
def killSpaces(adir,infile):
    #spaces in filenames can cause problems.  Just copy to newfiles with _ and use those
    nufile = infile.replace(' ','_')
    of = os.path.join(adir,infile)
    nf = os.path.join(adir,nufile)
    copyFiles_old(of,nf)  #because os.system won't work with spaces.
    if os.path.getsize(of)==os.path.getsize(nf): os.remove(of)
    else: print('Attempted to make a file without spaces in the name.  May have failed.  Please check that the peak file name '+of+' is the correct size and does not have spaces.')
    return nufile
	
def makeNewFile(afile):
	#file exists, so copy to a different file then the file of interest can be written over
	import datetime
	current = datetime.datetime.now()
	time = current.strftime("_%H%M%S")  #just gives time
	parts = os.path.split(afile)
	pa= parts[1].split('.')
	nufile = pa[0]+time
	if len(pa)>1: nufile+=pa[1]
	else: nufile+='.pf'
	nufile = os.path.join(parts[0],nufile)
	copyFiles(afile,nufile)
	
def getbase(afile):
    #returns base of file - file end if there
    path,end = os.path.split(afile)
    parts = end.split('.')
    base=path
    if len(parts)<=2: base=os.path.join(base,parts[0])
    else: #more than one pesky '.'
        astr=''
        for p in parts[:-1]: 
            if astr: astr+='.'
            astr+=p
        base = os.path.join(base,astr)
    return base
    
def readHeader(aline):
	#reads header line and returns as dictionary with col:index
	indx={}
	
	for e,col in enumerate(aline):
		col = col.strip('#')
		
		indx[col] = e
	return indx	
		
   
def sort2DList(alist,where):
	#where can be single iterator or list of up to 3 columns.
	if isinstance(where,list):
		if len(where)==1: where = where[0]
		if len(where)==2:
			return sorted(alist,key=lambda x:(x[where[0]],x[where[1]]))
		if len(where)>2:
			return sorted(alist,key=lambda x:(x[where[0]],x[where[1]],x[where[2]])) 	
	return sorted(alist,key=lambda x:x[where])
		
def write1DList(fileout,alist,header,flag):
	#030217 = 1D list
	try:	fout = open(fileout,flag)
	except: cout('could not open '+fileout+' for writing'); return
	if header: fout.write(header)
	for a in alist:
		if a[-1]!='\n': a+='\n'
		fout.write(a)
	fout.close()
	return
	
def write2DList(fileout,alist,flag,header='',sp='\t'):
	#Takes in 2D list. inner list is columns, outer list is lines
	fout = open(fileout,flag)
	if header: fout.write(header+'\n')
	for row in alist:
		line=''
		
		for i,item in enumerate(row):
			try: line+=item
			except: line+=str(item)
			
			if i<len(row)-1:
				line+=sp
		line+='\n'
		fout.write(line)
	fout.close()
	
def readInListFromLine(line):
    #takes in a line with one list and returns list with nums or strs.
    astr=''  ; alist=[]
    for r in range(len(line)):
        if line[r]=='[': continue
        if line[r]==']': 
            parts=astr.split(',')
            for val in parts: alist.append(tonum(val)) #converts to a num if is one
            break
        astr+=line[r]
    return alist
		
def makeCDLLine(alist):
	#Everything has to have quotes and separated by commas
	line=''
	for item in alist:  
		if isinstance(item,list):  #whole list has " on either side, not within
			nul=''
			for i in item:
				if nul: nul+=','
				nul+=str(i)
			item = nul	
		
		if line: line+=','
		if item: line+='\"'+str(item)+'\"'
		else: line+='\"'+'\"'
	
	return line		

def mysplit(aline):
    #tries tabs, commas, then spaces
    parts=[];temp=''
    sp=''
    if '\t' in aline: sp='\t'
    elif ',' in aline: sp=','
    elif ' ' in aline: sp=' '
    for ch in aline:
        if ch=='\n': 
            if temp: parts.append(temp); temp=''; 
            break
        if ch==sp:
            if temp: parts.append(temp);temp=''
            continue
        temp+=ch
    if temp: parts.append(temp)
    return parts
    
def addLists(list1,list2):
	#adds 2 lists together but makes sure only 1 item in each.
	error = 0.0001  #just to keep the computer honest
	if len(list1)<1:
		list1=list2
		return list1
	for l1 in list1:
		for l2 in list2:
			if l2 not in list1: #l1-error<=l2<=l1+error:
				list1.append(l2)
	return list1	
	
def remove1DRepeats(alist):	
	#removes repeats from a 1D list
	nulist = []
	alist.sort()
	oa=''
	for a in alist:
		if a!=oa:
			nulist.append(a)
			oa = a
		
	return nulist	

def closest(alist,val):
	#this returns a value, not an iterator
	return alist[min(range(len(alist)),key=lambda i: abs(alist[i]-val))]
	
def closest2D(alist,val,wh=0):
	# returns a value
	return alist[min(range(len(alist)),key=lambda i: abs(alist[i][wh]-val))]	
	

	
def cleanList(alist,val,p=False):	
	#cleans list based on value #where in list)
	#p is for testing
	e2=.000001
	nulist=[]
	alist=sorted(alist,key=lambda l:l[val])
	if p==True: print (alist)
	oa=0
	for a in alist:
		if isinstance(a[val],float):
			
			if a[val]-e2<=oa<=a[val]+e2: continue  #was a match
			else: nulist.append(a); 
		else:  #a string or something
			if a[val]!=oa: nulist.append(a);
		oa=a[val]	
	if p==True: print (nulist)	
	return nulist		
	
def cleanList2D(alist,vals,p=False):  	
	#cleans list based on vals #where in list)
	#p is for testing
	e2=.000001
	nulist=[]
	if p==True: print (alist)
	oa=[]
	matches={}
	for val in vals:
		alist=sorted(alist,key=lambda l:l[val])
		for e,a in enumerate(alist):
			if isinstance(a[val],float):
				if a[val]-e2<=oa[val]<=a[val]+e2: 
					if e not in matches: matches[e]=0
					matches[e]+=1
			else:  #a string or something
				if a[val]==oa[val]: 
					if e not in matches: matches[e]=0
					matches[e]+=1
			oa=a
	for key,num in matches.items():
		if num<len(vals):
			nulist.append(alist[key])
	if p==True: print (nulist)
	return nulist		
	
def cleanListPlus(alist,val,v2,err):	
	#cleans list based on value #where in list)
	#and adds info to each dimension based on 2nd value (can be 'all')
	
	nulist=[]
	alist=sorted(alist,key=lambda l:l[val])
	oa=0  #old a
	
	for a in alist:
		te=[]
		if v2=='all':	te = a[1:]
		else: te=a[v2]	
		if isinstance(a[val],float):
			e=a[val]*err
			if a[val]-e<=oa<=a[val]+e:  #within range
				nulist[-1].append(te)
				continue  #was a match
			else: nulist.append([a[val],te]) #start anew
		else:  #a string or something
			if a[val]!=oa: #not a match.start anew
				nulist.append(a);
			else:
				nulist[-1]+=(te)
		oa=a[val]	
	
	return nulist	
	
def clean1DList(alist):	
	#cleans list based on value #where in list)
	e2=.000001
	nulist=[]
	alist=sorted(alist)
	oa=0
	for a in alist:
		if isinstance(a,float):
			if a-e2<=oa<=a+e2: continue  #was a match
			else: nulist.append(a); 
		else:  #a string or something
			if a!=oa: nulist.append(a);
		oa=a
	return nulist		
	
	
def bin(alist,wh,err=''):
	#Cluster by differences between values
	#make sure from unique files
	#if err=# make sure value=#
	#wh = where in 2D list
	if len(alist)<2: return alist
	ov=''
	tlist=[]
	ttlist=[]
	if err=='':  #sort by exact value
		for a in alist:
			if a[wh]!=ov:
				if ov!='':  #not first
					tlist.append(ttlist)
				ttlist=[]
				ov=a[wh]
			ttlist.append(a)
	if isnum(err):	
		ov=0
		for a in alist:
			val=float(a[wh])
			if abs(val-ov)>err:  #corrected 012920..not tested
				if ov!=0:  #not the first in theory
					tlist.append(ttlist)
				ttlist=[]
				ov=val
			ttlist.append(a)
	if ttlist: tlist.append(ttlist)  #catch last
	return tlist
			
	
def compareLists(l1,l2):
	#compares values in lists.  Returns true if same
	#print l1,l2
	if len(l1)!=len(l2): return False
	if isinstance(l2,list)==False: return False
	c1=l1[:]; c2=l2[:]
	c1.sort(); c2.sort()
	for i,item in enumerate(c1):
		if isinstance(item,dict): 
			if compareDict(item,c2[i])==False: return False
		if isinstance(item,list): 
			if compareLists(item,c2[i])==False: return False
		if item!=c2[i]: return False
	return True			
		

def compareLetters(s1,s2):
	#what to see if same letters are in mixed up strings
	if len(s1)!=len(s2): return False
	l1=[];l2=[]
	for c in s1:
		l1.append(c)
	for c in s2:
		l2.append(c)
	return compareLists(l1,l2)

def makeDictFromName(name):
    #takes in Hex5HexNAc2.  Returns {'hex':5,'hexNac:2}
    adic={}
    astr='';anum=''
    for ch in name:
        if ch.isalpha():
            if anum:
                if astr not in adic: adic[astr]=0
                adic[astr]=int(anum); 
                astr=''; anum=''
            astr+=ch
        if ch.isnumeric():  anum+=ch
    if anum: #catch last
        if astr not in adic: adic[astr]=0
        adic[astr]=int(anum); 
        
    return adic
	
def compareDict(d1,d2):
	#compares d1 to d2.  Returns True if same

	if len(d1)!=len(d2): return False
	if isinstance(d2,dict)==False: return False
	for k1,v1 in d1.items():
		if k1 not in d2: return False
		if isinstance(v1,dict): 
			if compareDict(v1,d2[k1])==False: return False
		if isinstance(v1,list): 
			if compareLists(v1,d2[k1])==False: return False
		if v1!=d2[k1]: return False
	return True
	
def sumDict(d1,d2):
	#no lists involved.  Simple math
	#copies d2 to d1
	td={}
	
	for key,val in d1.items():
		td[key]=val
		
	for key,val in d2.items():
		if key in td: td[key]+=val
	return td
    
def addDict(d1,d2):
	#copies d2 to d1
	#checks for values
	
	td={}
	
	#make a copy
	for key,val in d1.items():
		td[key]=val
		
	for key,val in d2.items():
		if key in td:
			
			if testInt(val)>0:
				td[key]+=val
			if isinstance(val,list):
				td[key]=addLists(td[key],val)
			 
		else:
			td[key]=val  #addlists?
	return td
	
def subtractDict(d1,d2):
	#subtracts d2 from d1
	td={}
	td=d1.copy()
			
	for key,val in d2.items():
		if key in td:
			if testInt(val)>0:
				td[key]=td[key]-val
				if td[key]==0: td.pop(key,None)
		else:
			return 0  #can't subtract if not there!
	
	return td		

def subtractDict_neg(d1,d2):
	# subtracts d2 from d1.  Returns negative values if something is in d2 but not d1
	td={};kt=d1.copy()
	
	for key,val in d2.items():
		if key in d1:
			kt.pop(key,None)
			diff = d1[key]-val
			if diff!=0:td[key]=diff
		else:  #in d2 but not d1
			diff = 0-val
			if diff!=0:td[key]=diff
	for key,val in kt.items():  #check to see if something is in d1 but not d2
		if key not in td and val!=0: td[key]=val
	
	return td	
    
def convertDicToString(adic,order):
    #order is order of keys.  Adic=name:num
    astr=''
    td = adic.copy()
    for o in order:
        if o in adic:
            if adic[o]!=0:astr+=o+str(adic[o])
            td.pop(o,None)
    #if leftovers put at end
    for k,v in td.items(): 
        if int(v)>0: astr+=k+str(v)
    return astr
	
def mystrip(astr,all=['\n',' ','\r']):
	b=list(astr)
	c=''
	for l in b:
		if l in all: continue
		c+=l
	return c	
	
def getInt(astr):
	'''extracts an int from a string'''
	nuint=''
	for c in astr:
		
		if c>='0' and c<='9':
			nuint+=c
		else:  
			if nuint!='': break
			
	if nuint!='': return int(nuint)
	return 0
	
def getLonelyInt(astr):
	'''get int separated by space from rest of string'''
	parts = astr.split(' ')
	for p in parts:
		if isnum(p):
			return int(p)
	return 0		
	
def testInt(num):
	try:
		if isinstance(num,list): return -1
		if isinstance(num,dict): return -1
		n=int(num)
		if n<0: n=0
		return n
	except ValueError:
		return -1	
		

def getTotalNum(fragment):
	'''extracts and adds up all the integers in a string'''
	nuint=''
	num=0
	for c in fragment:
		if c>='0' and c<='9':
			nuint+=c
		else:
			if nuint!='':
				num+=int(nuint)
				nuint=''
	if nuint!='': num+=int(nuint)  #catch last
	return num	
	
def getListedNum(strin):
	#takes in string with numbers separated by commas or spaces and outputs lists of strings,numbers
	nulist=[]
	parts=[]
	if strin.find(','): parts = strin.split(',') 
	else: parts = strin.split(' ')
	if len(parts)<2: return nulist

	c=1
	for p in parts:
		s="pep"+str(c)
		c=c+1
		try: nulist.append((s,float(p)))
		except: print ("Could not read peptide list."); break
	return nulist	
	
def getBiggestDifference(alist):
	#list of numbers.  Returns biggest difference
	alist.sort()
	max=0; ov=0 #biggest diff could be first step so start at 0!
	for a in alist:
		if (a-ov)>max: max=a-ov
		ov=a
	return max	
	
def stdev(list):  #072516
	c=0		#counter
	total = 0.0
	for i in list:
		total = total+i
		c = c+1
	if c==0: return 0
	average = total/c
	total = 0.0
	for i in list:
		total = total+((i-average)*(i-average))
	stdev = math.sqrt(total/c)
	return stdev 	
	
def findAvg(list):
	#100716
	c=0
	total=0
	for i in list:
		total=total+float(i)
		c+=1
	if c==0: return 0
	return total/c	


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
	
def getStringPos(line,pos=1):
	#gets string between set of quotation marks indicated by pos
	flag = False
	nustr = ''
	co=1
	for c in line:
		if c=="\"":
			if flag==False:
				flag=True; continue
			if flag==True:
				if co==pos: break  #got the right set of quotes
				co=co+1
				nustr=''  #try again
				flag=False
		if flag==True:
			nustr=nustr+c
	return nustr
	
def convertStringToList(astr):
    #takes in alpha numeric string and separates by alpha and numbers
    nulist=[];nus='';num=''
    for ch in astr:
        if ch.isalpha() or ch=='*':
            if num: nulist.append(tonum(num)); num=''
            nus+=ch
        if ch.isnumeric():
            if nus: nulist.append(nus); nus=''
            num+=ch
    #catch last.  Should be one or other
    if num: nulist.append(tonum(num))
    if nus: nulist.append(nus)
    return nulist

def convertStringToList_sp(astr):
    #takes in alpha numeric string and separates by alpha and numbers
    #Special for when there are labels in MALDI assignments
    #comes in as NeuAc2*pE*Hex6.. Labels apply to NeuAc2
    #alist will = [NeuAc,2,*pEHex,6]
    #return as NeuAc*p 1 NeuAc*E 1 or maybe *p 1 *E 1 Hex 6
    alist = convertStringToList(astr) #the *pE* will be with Hex
    if '*' not in astr: return alist #easy
    def searchAndRescue(alist,start):
        #finds labels and fixes things
        nulist=[];temp=[]
        for r in range(start,len(alist),2): #go through sugar list only - skip #'s.  Should never be in first label!
            if '*' not in alist[r]: start=r+2; continue
            parts = alist[r].split('*') #parts[0] will = ''
            #get all labels and count of each
            tdic={};
            for ch in parts[1]:
                if ch not in tdic: tdic[ch]=0
                tdic[ch]+=1;
            pc = alist[r-1] #count of previous sugar
            for k,v in tdic.items():
                temp+=['*'+k,v]; pc-=v #making a list of [*p,1,*E,1]
            if pc>0: temp+=[alist[r-2],pc] #in case any NeuAc left over
            if len(parts)>2: #now add sugar we took the label from if it is there
                if parts[2]!='': temp+=[parts[2],alist[r+1]]
            nulist=alist[:r-2]+temp+alist[r+2:] #removes old and inserts changes    
            start=r+2
            break
        if not nulist: return alist, start
        return nulist, start
    ####################
    alist = convertStringToList(astr) #the *pE* will be with Hex
    if '*' not in astr: return alist #easy    
    ii=2
    while ii<len(alist):
        alist,ii = searchAndRescue(alist,ii) #made recursive since changing alist.  Start with frest alist each time!
    return alist
    
def convertStringToDic(astr):
    #takes in alpha numeric string and separates by alpha(key) and numbers(val)
    #Tested only for alpha first so far. Sep.6,2021
    nudic={};nus='';num='';snus='';snum=0
    for ch in astr:
        if ch.isalpha():
            if num:
                if snus:
                    if nudic[snus]==0: nudic[snus]=tonum(num); num='';snus=''
                else: snum=tonum(num); num=''
            nus+=ch
        if ch.isnumeric():
            if nus:
                if snum:  #number saved first
                    nudic[nus]=snum; nus=''; snum=0 #reset so dont' come here on accident
                else: nudic[nus]=0; snus=nus; nus=''
            num+=ch
    #catch last.  Should be one or other
    if num: nudic[snus]=tonum(num)
    if nus: nudic[nus]=snum
    return nudic
    
def getStringBetween(line,start,end):
	'''start = index#.  end = character.  Skips similar character if before index'''
	nustr = ''
	for i in range(start+1,len(line)):
		if line[i]==end: break
		nustr+=line[i]
	return nustr
	
def getString(line,phrase):
	#gets string between quotes right after phrase
	
	co = line.find(phrase)
	#now have to skip to quotes
	flag = False
	nustr = ''
	for r in range (co,len(line)):
		c = line[r]
		if c=="\"":
			if flag==False:
				flag=True; continue
			if flag==True:
				break
		if flag==True:
			nustr=nustr+c
	
	return nustr	
	

	
def readCDL(line):
		#Read comma delineated line  "a","b","c",
		#return as list
		alist=[]
		str=''
		flag='off'  #not currently collecting a string
		for c in line:
			if c=='\"' and flag=='off':  #at beginning
				flag='on'; continue
			if c=='\"' and flag=='on':
				alist.append(str)
				str=''
				flag='off'
				continue  #skip over all quotes
			if c==',' and flag=='off': continue  #this happens between end and start ","..."
			if c=='\n': continue
			str+=c
		if str: alist.append(str)  #catch end	
		return alist	
	
def toint(val):
	#convert strings to ints
	num=0
	try:
		num=int(val)
	except:
		num = 0
	return num		
	
def isnum(val):
	#convert strings to floats
	num=0.0
	try:
		num=float(val)
	except:
		return False
	return True
	
def toflo(val):
	#convert strings to floats
	num=0.0
	try:
		num=float(val)
	except:
		num = 0.0
	return num		
	
def tonum(val):
	#try converting to number, if not, send back string
	num=''
	if not isinstance(val,str): return val
	if '.' in val:
		try: num=float(val)
		except: num=val
	else: 
		try: num=int(val)
		except: num=val
	return num	
	
def getInt(astr,zero=False,neg=True):
	# pull number out of string
	#return null or zero if no number; if neg=False, '-' are strings
	val=''; gotit=False
	for ch in astr:
		if '0'<=ch<='9' or (ch=='-' and neg==True):
			val+=ch
			gotit=True
		elif gotit==True: break  #reached end of number
	anum=0
	try: anum = int(val)
	except: 
		if zero!=True: anum=''
	return anum
	
def getFloat(astr,zero=False):
	# pull number out of string
	#return null or zero if no number
	val=''; gotit=False
	for ch in astr:
		if '0'<=ch<='9' or ch=='.' or ch=='-': 
			val+=ch
			gotit=True
		elif gotit==True: break  #reached end of number
	anum=0
	try: anum = float(val)
	except: 
		if zero!=True: anum=''
	return anum		
	
def convertToNum(alist,only=False):
	#a is 2D list
	#if only ==True, do not return strings
	nulist=[]
	temp=[]
	for a in alist:
		for item in a:
			if isnum(item):
				temp.append(toflo(item))
			else:
				if only==False:	temp.append(item)
		nulist.append(temp)
		temp=[]
	return nulist	
	
def ztop(zscore,neg=False):
	#11/1/2016
	#takes zscore and converts to p value 
	#finds area from 0 to zscore = probability under curve 0=mean
	#High = 1.0 if *2
	#if neg==True, return p from zscores less than 0 as negatives
	area=0.0
	oldy=0.0
	x=0.0	
	i=0.01  #increment for calculation.  
	nflag=False
	if zscore<0: zscore = zscore*-1.0; nflag=True
	end=False
	while x<=zscore:
		y = (math.exp(-1*x*x/2)/math.sqrt(2*math.pi))
		if oldy==0: oldy=y; x+=i; continue  #first one
		y1=oldy; y2=y
		if y>oldy: y2=oldy; y1=y
		area+=(i*y1)+(i*(y1-y2))/2
		if end==True: break
		if zscore-x<i: x=zscore; end=True
		else: x+=i
		oldy=y
	if neg==True and nflag==True: area=area*-1	
	return area	*2	
	
def multiplyValuesWithSTD(X,xS,Y,yS):
	#for division, send in 1/Y.  yS is treated the same way
	Z=X*Y
	Zs = math.sqrt(((xS/X)*(xS/X)+(yS/Y)*(yS/Y)))*Z
	return Z,Zs
	
def addValuesWithSTD(X,sX,Y,sY):
	#for subtraction, send in -Y.  sY handled same way
	Z=X+Y
	sZ = math.sqrt((sX*sX)+(sY*sY))
	return Z,sZ
	
def myround(anum,dig=0):
	#anum = 1.25, dig=1 (how many digets after period)
	multi = 10 ** dig  #10
	tnum = anum*multi  #1.25*10=12.5
	inum = int(tnum)   #12
	if (tnum-inum)>= 0.5: tnum = inum+1
	else: tnum=inum
	return tnum/float(multi)	
	
def convertMinToSec(amin):
	#assuming float for amin i.e. 22.3
	#.3 minutes = 60*.3
	smin = str(amin)
	parts = smin.split('.')
	sec = 60*int(parts[0])
	if len(parts)>1:
		sec+=60*(float('.'+parts[1]))
	return sec	
def findInList(alist,what):
    #finds partial sequence in a list and returns first index or -1
    for e,item in enumerate(alist):
        if what in item: return e
    return -1
def makeLine(alist,sp='\t'):
    #makes a line from a list using sp.
    aline=''
    for item in alist:
        if aline: aline+=sp
        aline+=str(item)
    return aline
    
def readByonicDBfile(afile):
	#input - "glytoucan_ac","byonic"
	#input - "G02438LG","HexNAc(1)dHex(2) % 484.174789"
	
	try: fin = open(afile,'r')
	except: print('could not open '+afile); return []
	alist=[];wh=1;co=0
	for line in fin:
		line = line.replace('\n','')
		line = line.replace('\"','')
		parts = line.split(',')
		if 'byonic' in parts: wh = parts.index('byonic'); continue
		p2 = parts[wh].split('%')
		bdic = makeDicFromByonicName(p2[0]);co+=1
		if bdic not in alist: alist.append(bdic)
	fin.close()    
	if not alist: print('could not read '+afile); 
	
	return alist	
	
def makeDicFromByonicName(bname):
	#bname = "HexNAc(1)dHex(2)"
	astr=''; anum='';onnum=False
	bdic={}
	for ch in bname:
		if ch=='(':	onnum=True; continue
		if ch==')': 
			try: bdic[astr]=int(anum)
			except: pass  #byonic had + after some numbers - don't know what that means
			onnum=False; astr='';anum=''; continue
		if onnum==False: astr+=ch
		if onnum==True: anum+=ch
	return bdic	    