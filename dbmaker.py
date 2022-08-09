#python3
##Can be run standalone by calling testRun()
from tkinter import *
import windowfeatures as uw
import sys,os
from common import *

class dbWin():
	def __init__(self,root,eb=''):
		self.root=root
		self.frame1 = Frame(root,bd=2)
		self.frame1.grid(row=0, column=0,padx=5,pady=5)
		self.items=[]
		self.ui=userinput()
		readDefaultFile(self.ui)
		self.rb1=[] #used in load Values
		self.rb2=[]	
		self.rbadd=[]
		self.eb=eb
		
	def populateWin(self):
		mast=self.frame1
		f2 = Frame(mast,bd=2);f2.grid(row=0, column=0)
		r=0;c=0; self.items=[]
		uw.makeLabel(self,f2,"<<D A T A B A S E   M A K E R>>",r,0,exp=3,sticky=EW);r+=1
		uw.makeLabel(self,f2,"Takes in glycan compositions in shorthand (H3N2)",r,0,exp=3,sticky=EW);r+=1
		uw.makeLabel(self,f2,"Calculates masses and atomic compositions based on user-selected options.",r,0,exp=3,sticky=EW);r+=1
		uw.makeLabel(self,f2,"Outputs all with publication-style terminology (Hex3HexNAc2).",r,0,exp=3,sticky=EW);r+=1
		blankf = Frame(f2,bd=2);blankf.grid(row=r, column=0, columnspan=3, pady=10);r+=1
		uw.makeLabel(self,f2,"* * * O P T I O N S * * *",r,0,exp=3,sticky=EW);r+=1

		#Modifications and defaults start here
		uw.makeLabel(self,f2,"Preparation",r,0)
		labopt=getFirstValues(self.ui.defaults['preparation'])
		uw.makeDropDownMenu(self,f2,labopt,labopt[1],r,1,'process',sticky=W);
		uw.makeButton(self,f2,"Edit Defaults",lambda: self.editwin('preparation'),r,2);r+=1
		uw.makeLabel(self,f2,"Modification:",r,0)
		labopt=getFirstValues(self.ui.defaults['modifications'])
		uw.makeCheckButtonList(self,f2,r,1,labopt,text="Choose one or more",key='mods',exp=1)
		uw.makeButton(self,f2,"Edit Defaults",lambda: self.editwin('modifications'),r,2);r+=1
		uw.makeLabel(self,f2,"Adduct:",r,0)
		labopt=getFirstValues(self.ui.defaults['adductIons'])
		f4 = Frame(f2,bd=0);f4.grid(row=r, column=1, sticky=EW,columnspan=2)
		uw.makeDropDownMenu(self,f4,labopt,labopt[0],r,0,'addons',sticky=W)
		uw.makeLabel(self,f4,"\tNumber:",r,1)
		uw.makeDropDownMenu(self,f4,["-1","1","2","3","1-2","1-3","2-3"],"1",r,2,'ionnum',sticky=E)
		uw.makeButton(self,f2,"Edit Defaults",lambda: self.editwin('adductIons'),r,2);r+=1
		uw.makeLabel(self,f2,">>NOTE: AssignMALDI assumes z=1 only",r,0,exp=3);r+=1
		r+=1
		uw.makeLabel(self,f2,"More Defaults:",r,0)
		f3 = Frame(f2,bd=2);f3.grid(row=r, column=1, sticky=EW,pady=20)
		uw.makeButton(self,f3,"AtomMasses",lambda: self.editwin('atomMass'),0,0,sticky=E)
		uw.makeButton(self,f3,"Monosaccharides",lambda: self.editwin('monosaccharides'),0,1,sticky=W)
		uw.makeButton(self,f3,"Output Order",lambda: self.editwin('outputOrder'),0,2,sticky=W);r+=1
		uw.makeLabel(self,f2,"* * * G L Y C A N   I N P U T * * *",r,0,exp=3,sticky=EW);r+=1
		f4 = Frame(f2,bd=2);f4.grid(row=r, column=0, columnspan=3)
		uw.makeLabel(self,f4,"Shorthand abbreviations listed under [Monosaccharides] default above.",2,0,sticky=EW);r+=1
		uw.makeLabel(self,f2,"Single Entry:",r,0)
		uw.makeEntry(self,f2,r,1,20,key="sentry")
		uw.makeButton(self,f2,"Calculate",lambda: self.singleEntry('sentry'),r,2,sticky=EW);r+=1
		uw.makeLabel(self,f2,"Results:",r,0)
		uw.makeTextBox(self,f2,r,1,width=40,key="sresults")
		uw.makeButton(self,f2,"Add to file",lambda: self.append2file(),r,2,sticky=EW);r+=1
		uw.makeLabel(self,f2,"* * * O R * * *",r,0,exp=3, sticky=EW);r+=1        
		uw.makeFileRow(self,f2,r,c,"Multiple entry file: ","infile",ewidth=50);r+=1
		uw.makeFileRow(self,f2,r,c,"New Database file: ","outfile",type='fileout',ewidth=50);r+=1;
		uw.makeButton(self,f2,"Write Database",lambda: self.saveDatabase(),r,1, sticky=EW);r+=1
		uw.makeButton(self,f2,"Help",lambda: uw.showHelp(self.ui.helpfile,'dbmaker'),r,2, sticky=W);r+=1
		self.getOldValues()
	
	def singleEntry(self,key):
		self.saveValues()
		oligo=calculateOligo(self.ui.sentry,self.ui)
		self.setValue('sresults',oligo)
		
		
	def append2file(self):
		#adds manually entered values to file if known
		self.saveValues()
		oligo=calculateOligo(self.ui.sentry,self.ui)
		aline=self.setValue('sresults',oligo)
		append2database(self.ui.outfile,aline)
		
	def saveDatabase(self):
		self.saveValues()
		writeNewDatabase(self.ui,self.eb)
		
	def editwin(self,what):
		#what should match labels in default file
		self.saveValues()  #save current options?
		t=Toplevel()
		t.wm_title("Edit default "+what)
		ew=EditWin(t,self.ui,self)
		if what=='outputOrder': ew.orderWin(what,self.ui.defaults[what])
		else: ew.populateWin(what,self.ui.defaults[what])

	def getOldValues(self):
		#reads last user-entered values from database file
		#first figure out the filename
		cwd=os.getcwd()		#current working directory
		name="lastdb.txt"
		dbfile=os.path.join(cwd,name)
		self.ui.dbfile=dbfile
		#now try and open it and get values:
		self.ui.getUserInput()  #values stored under userinput class
		self.loadValues() #values pulled from userinput class by comparison with self.items
		
	def setValue(self,key,value):
		#for text widgets only!  Value is a list
		aline='';ww=40
		for val in value:
			if len(val)>ww: ww=len(val)
			if aline: aline+='\n'
			aline+=val
		for wid,k in self.items:  #find the box in self.items
			if k==key:
				wid.config(width=ww,height=len(value))
				wid.delete('1.0',END)
				wid.insert(END,aline)
		return aline  #in case want to send to file
		
	def loadValues(self):
		for i,j in self.items:  #widget,key
			val=self.ui.returnValue(j)

			if j=='mods' or j=='process' or j=="addons" or j=='format':		#radiobutton!
				i.set(val)		#val=value of radiobutton setting==mode.
				rblist=self.rb1
				if j=='mods': rblist=self.rb2
				if j=='addons':rblist=self.rbadd
				for rb,text,mode in rblist:
					if val==mode:
						rb.select()
					else:
						rb.deselect()
				continue
			
			try:
				i.delete(0,END)
				i.insert(0,val)
			except:
				pass#print (val)

	def saveValues(self):
		for pnt,key in self.items:  #pnt=pointer to widget
			if key=='sresults': continue  #this is to results box - output only
			self.ui.updateUserInput(key,pnt.get())
		self.ui.saveUserInput()
		
class EditWin():
	def __init__(self,root,ui,parent):
		self.root=root
		self.ui = ui
		self.parent=parent  #main window
		self.frame1 = Frame(root,bd=2,relief=SUNKEN)
		self.frame1.grid(row=0, column=0)
		self.items=[]	
		self.values={}  #filled in GO
		self.wident=11 #wider entry size
		self.sment=3 #smaller entry size
		self.r = 0

	def populateWin(self,name,data,Me=True):
		#need labels depending on type of data coming in
		atoms=[]
		mast=self.frame1
		f2 = Frame(mast,bd=2);f2.grid(row=0, column=0)
		r=0;c=0
		#FIRST, make labels in pop-up window
		comments = [line for line in data if '>' in line[0]]  #comment from default file
		for line in comments: #prints comments out to pop-up window
			note=makeLine(line,sp=' ')
			uw.makeLabel(self,f2,note,r,0,exp=12);r+=1
		ans=1;labco=0
		for lab in data[len(comments)]: #should be on header line
			if "number" in lab: ans=12
			uw.makeLabel(self,f2,lab,r,c,exp=ans);c+=1 #sugar, symbol...
			labco+=1
		c=0;r+=1
		
		longlen=len(data[len(comments)+1]);shortlen=0
		if findInList(data[-1],'=')>0: #'=' separates atoms from #'s in default file
			c=labco-1
			for ak,av in self.ui.defaults['atomMass']:  #makes atom labels
				if '>' in ak or "atom" in ak: continue  #skip comments and labels
				uw.makeLabel(self,f2,ak,r,c);c+=1
				atoms.append(ak)  #list used below
			if Me==True:uw.makeLabel(self,f2,'Me',r,c); atoms.append('Me')#adds non atom to end
			c=0;r+=1
			shortlen=len(atoms) ;longlen=labco-1
		#Now add ENTRIES
		for e,line in enumerate(data[len(comments)+1:]):
			xx=0 #counts items without '='
			for f,item in enumerate(line):
				if '=' not in item:	uw.makeEntry(self,f2,r,c,self.wident,text=item,key=str(r)+'-'+str(c));c+=1;xx+=1
				else: #make line in order of atoms including blanks, then make entries
					for ca,atom in enumerate(atoms):
						valu=''
						for eit in line[f:]:
							parts = eit.split('=')
							if parts[0]==atom: valu=parts[1];
						uw.makeEntry(self,f2,r,ca+xx,self.sment,text=valu,key=str(r)+'-'+str(c));
					break
			c=0;r+=1
		
		bf = Frame(mast,bd=2);bf.grid(row=1, column=0, sticky=EW)
		uw.makeButton(self,bf,"Add Row",lambda: self.addRow(f2,longlen,shortlen),0,0);
		uw.makeButton(self,bf,"Save",lambda: self.saveValues(name,longlen,atoms,self.ui),0,1);
		uw.makeButton(self,bf,"Close",lambda: self.root.destroy(),0,2);
		self.r=r+1 #save in case add row used

	def orderWin(self,name,data):
		mast=self.frame1
		f2 = Frame(mast,bd=2);f2.grid(row=0, column=0)
		r=0;c=0
		#FIRST, make labels
		comments = [line for line in data if '>' in line[0]]
		for line in comments:
			note=makeLine(line,sp=' ')
			uw.makeLabel(self,f2,note,r,0,exp=12);r+=1
		ans=1;labco=0
		for lab in data[len(comments)]: #should be on label line
			if "number" in lab: ans=12
			uw.makeLabel(self,f2,lab,r,c,exp=ans);c+=1 #sugar, symbol...
			labco+=1
		c=0;r+=1
		longlen=len(data[len(comments)+1])
		
		uw.makeSortableList(self,f2,data[len(comments)+1:],1,0,name);r+=1

		bf = Frame(mast,bd=2);bf.grid(row=1, column=0, sticky=EW)
		uw.makeButton(self,bf,"Save",lambda: self.saveValues(name,longlen,[],self.ui),0,1);
		uw.makeButton(self,bf,"Close",lambda: self.root.destroy(),0,2);
		self.r=r+1

	def shapeWin(self,name,data):
		shapes=['square','circle','triangle','diamond','hexagon','triangle-down','star','pentagon','plus','filled_X','triangle_left','triangle_right']
		colors=['blue','green','red','orange','darkorchid','mediumorchid','lightskyblue','palegreen','lightsalmon','cyan','peru','yellow','pink','silver','black','white']

		mast=self.frame1
		f2 = Frame(mast,bd=2);f2.grid(row=0, column=0)
		r=0;c=0
		#FIRST, make labels
		comments = [line for line in data if '>' in line[0]]
		for line in comments:
			note=makeLine(line,sp=' ')
			uw.makeLabel(self,f2,note,r,0,exp=12);r+=1
		ans=1;labco=0
		for lab in data[len(comments)]: #should be on label line
			if "number" in lab: ans=12
			uw.makeLabel(self,f2,lab,r,c,exp=ans);c+=1 #sugar, symbol...
			labco+=1
		c=0;r+=1
		longlen=len(data[len(comments)+1])
		
		#Now add ENTRIES.  Line is symbol, shape, color.
		for e,line in enumerate(data[len(comments)+1:]):
			uw.makeEntry(self,f2,r,c,self.wident,text=line[0],key=str(r)+'-'+str(c));c+=1;
			uw.makeDropDownMenu(self,f2,shapes,line[1],r,1,str(r)+'-sh',sticky=EW);
			uw.makeDropDownMenu(self,f2,colors,line[2],r,2,str(r)+'-co',sticky=EW,color=True);
			c=0;r+=1

		bf = Frame(mast,bd=2);bf.grid(row=1, column=0, sticky=EW)
		uw.makeButton(self,bf,"Add Row",lambda: self.addRowShape(f2,shapes,colors),0,0);
		uw.makeButton(self,bf,"Save",lambda: self.saveValues(name,longlen,[],self.ui),0,1);
		uw.makeButton(self,bf,"Close",lambda: self.root.destroy(),0,2);
		self.r=r+1

	def addRowShape(self,f2,shapes,colors):
		uw.makeEntry(self,f2,self.r,0,self.wident,text='',key=str(self.r)+'-'+str(0));
		uw.makeDropDownMenu(self,f2,shapes,shapes[0],self.r,1,str(self.r)+'-sh',sticky=EW);
		uw.makeDropDownMenu(self,f2,colors,colors[0],self.r,2,str(self.r)+'-co',sticky=EW,color=True);
		
		self.r+=1

	def addRow(self,f2,longlen,shortlen):
		#longlen = #entries using self.wident; shortlen=#entries using self.sment
		for c in range(longlen):
			uw.makeEntry(self,f2,self.r,c,width=self.wident,text='',key=str(self.r)+'-'+str(c),exp=1)
		for r in range(shortlen):
			uw.makeEntry(self,f2,self.r,r+longlen,width=self.sment,text='',key=str(self.r)+'-'+str(r+longlen),exp=1)
		self.r+=1
		
	
	def saveValues(self,name,longlen,atoms,ui):
		#longlen=length of part without '=' signs
		#name is key in ui.defaults
		#atoms are for options that have them
		co=0
		dfile = ui.defaultfile
		nudata=[]; okey=''; temp=[];good=False#key=row-column
		
		for pnt,key in self.items:  #using key to keep track of rows
			key=getInt(key,neg=False)
			if not okey: okey = key #just at beginning
			valu=pnt.get();
			if key!=okey: 
				if '' not in temp[:longlen]: good=True#These spaces should all have a value    
				temp = [ab for ab in temp if ab!=''] #skips blanks for atom assignments    
				if good==True: nudata.append(temp); good=False
				okey=key;temp=[]
			
			if atoms!=[] and len(temp)>=longlen and valu!='': #null values will still be added below.
				valu=atoms[len(temp)-longlen]+'='+str(valu)
			temp.append(valu)
		if temp:
			if name=='outputOrder': #temp is [[]]
				nudata = temp[0];
			else:
				if '' not in temp[:longlen]: good=True#These spaces should all have a value    
				temp = [ab for ab in temp if ab!=''] #skips blanks for atom assignments    
				if good==True: nudata.append(temp); good=False
		
		
		ui.defaults[name]=nudata
		updateDefaultFile(dfile,name,nudata)
		readDefaultFile(ui) #read in changed stuff
		self.parent.populateWin()
		self.root.destroy()


class userinput():
	#stores stuff from window.
	def __init__(self):
		self.infile=''
		self.outfile=''
		self.sentry=''
		self.sresults=''
		self.mods=[] #which label to use
		self.process='' #which treatment to use
		self.addons='' #which ion to use
		self.dbfile=''
		self.glyorder = [('me'),('neugc'),('neuac'),('pc'),('hexa'),('dhex'),('hex'),('hnac')]
		self.defaultfile="dbmaker_defaults.txt"
		self.defaults={} #stores values from default file name:[values]
		self.ammass=[] #stores atoms and masses
		self.monos={} #stores sugar objects
		self.labels={} #stores modifications as sugar objects
		self.shorthand={} #stores ['h':'Hex']
		self.treatment={} #stores reducing end mods i.e. beta-elimination
		self.addonmass=0  #goes with self.addons which comes from dropdown menu. set in setmonos
		self.ionnum=1  #how man addons to use (ions)
		self.helpfile = "assignMaldi_help.txt"

	def returnValue(self,key):
		#Used to return a single value
		dict=vars(self)
		for k in dict:
			if key==k:
				return dict[k]
		return ''
		
		
	def getUserInput(self):
		#called from getOldValues
		#reads in last values used and saved in database file
		if self.dbfile=='': return
		filein=self.dbfile
		
		"""assigns sting values to dictionary"""
		dict=vars(self)
		try:
			fin = open(filein,'r')
			for line in fin:
				
				if '[' in line or '{' in line: continue #skip lists and dicts
				
				line=line.strip()  #removes spaces,tabs
				if len(line)==0: continue  #too short
				if line[0]=='#': continue  #skip comment
				sline = line.split('=') #to fix prob with 'defaults'
				for key in dict:
					if sline[0].find(key)>-1:
						dict[key]=self.getValue(line)
						
					if key=='dbfile': dict[key]=filein  #reset here or it will keep saving to the old one!    
			fin.close()
		except:
			return

	def saveUserInput(self):
		#need to timestamp the file or something to prevent writing over old files.
		#Also, what directory should I store it in, the user directory + my own \userinput directory?
		#called from dbwin.saveValues after updateUserInput below
		if self.dbfile=='': return
		fileout=self.dbfile
		self.setMonos() #only do this the first time..reads default time
		try:
			fout = open(fileout,'w')
			dict=vars(self)
			for v in dict: 
				line=v+' = '+str(dict[v])+'\n'
				#print('line',line)
				fout.write(line)
				#print v, dict[v]
			fout.close()
			
			return
		except IOError:
			print ('>>>Cannot open',fileout)
		else:
			print ('>>>Error opening',fileout)
	
	def setMonos(self):
		#replaces setGlycans.  getAllValues reads stuff from default file
		self.monos={};self.ammass=[]
		
		amlist=getAllValues(self.defaults['atomMass']) #skips > and label

		for n,m in amlist: self.ammass.append([n,float(m)])
		alist=getAllValues(self.defaults['monosaccharides'])

		for sug in alist:
			s=sugar(sug,amlist)
			self.monos[s.name]=s
			self.shorthand[s.sym.lower()]=s.name

		#also setting labels
		self.labels={}
		alist=getAllValues(self.defaults['modifications'])
		for sug in alist:
			s=sugar(sug,amlist)
			self.labels[s.name]=s
		#and preparation
		self.treatment={}
		alist=getAllValues(self.defaults['preparation'])
		for sug in alist:
			s=sugar(sug,amlist)
			self.treatment[s.name]=s
		alist=getAllValues(self.defaults['adductIons'])
		for ion,mass in alist:
			if ion==self.addons: self.addonmass=float(mass); 

	def updateUserInput(self,key,val,iter=0):
		#iter = iterator for lists if applicable
		#updates stuff in UI from stuff entered by user
		
		dict=vars(self)
		if key in dict:
			if isinstance(dict[key],list)==True:	#so userinput item is a list
				dict[key].append(val)
			else: dict[key]=val
		else:  #must be mod
			if isinstance(dict['mods'],str): dict['mods']=[dict['mods']] #put string into list
			if val==0: #not selected
				if key in dict['mods']: dict['mods'].remove(key)
			if val==1: #selected
				if key not in dict['mods']: dict['mods'].append(key)

	def getValue(self,line):
		#skip over '=' and spaces and collect value to end of line
		i = line.find('=')
		i=i+1
		if i>=len(line): val=''; return val
		i=self.skipSpaces(line,i)
		if i>=len(line): val=''; return val
		val=""	
		while i<len(line):
			val=val+line[i]
			i=i+1
		return val
				
	def skipSpaces(self,line,i):
		
		while i<len(line):
			if line[i]!=' ': break
			i=i+1
		if i>=len(line): return -1
		return i
		
class sugar():
	def __init__(self,alist,atommass):
		#these are all numbers of atoms or methyl groups
		self.atoms={} #stores # of each atom
		self.sym='' #symbol
		self.order=['C','H','N','O','P','S','D','Na'] #how much does order matter?
		self.weights=[]
		self.mod=''
		self.freq='always'  #for modifications.  Also sometimes
		self.where='' #for modifications
		self.name = ''
		self.weight=0.0
		self.setValues(alist,atommass)

	
	def copy(self):
		adic=vars(self)
		anew=sugar([],[])
		nudic=vars(anew)
		for k,v in adic.items():
			if isinstance(v,dict) or isinstance(v,list): nudic[k]=v.copy()
			else: nudic[k]=v
		return anew
    
	def setValues(s,line,atommass):
		#These come from defaults. line Format is list with name,sym,(frequency),C=3, etc.
		#atommass also from default file
		if not s.order:
			for a,w in atommass: s.order.append(a),s.weights.append(float(w)) 
		for atom in s.order:
			if atom not in s.atoms: s.atoms[atom]=0
		if line==[]: return
		s.name = line[0]
		s.sym = line[1]  
		for item in line[2:]:
			if '=' not in item: #must be modification 
				s.freq = item
				s.where=s.sym; s.sym=s.name
				if s.freq!='always' and s.freq!='sometimes': s.freq='sometimes'; print(s.name+' set to sometimes.')
				continue
			parts = item.split('=');
			if parts[0]=='Me': s.atoms[parts[0]]=0  #special case!
			if parts[0] not in s.atoms:  #error!
				print(parts[0]+" is not in atom list.  Please add the name and mass to the defaults and try again.")
				continue
			try: s.atoms[parts[0]]=int(parts[1]);
			except: print("Could not read how many "+parts[0]+" atoms are in "+s.name+" setting to zero. Check defaults.")

	def calcWeight(s,ammass):
		#s is oligo
		#ammass=[['C',mass],..]
		weight = s.weight
		for n,w in ammass: #name,weight
			w=float(w)
			if n in s.atoms:
				num=int(s.atoms[n])
				weight += w*num
			else: print(n +" not in atoms.  Check atomMass default")
		s.weight = weight
		
		
	def addSugar(s,mod,num,me=''):# mod is a defined sugar
		##Adds atoms to chemical formula and their mass to weight
		#s is the sugar to add to, num is how many mods. ME is '' if no methyl groups,otherwise object.
		s.addAtoms(num,mod,me)  #number of methyl groups for a mono?
		s.weight = s.weight+(num*mod.weight)

	
		
	def addAtoms(s,num,sug,me):
		#this adds the atoms of sugars together. s.atoms and sug.atoms are dict
		#methyl added elsewhere, but needed to know this when adding labels so could subtract if needed.
		if sug=='': return
		for k,v in s.atoms.items(): #name, howmany
			
			if k=='Me':
				if k in sug.atoms: s.addSugar(me,sug.atoms[k]) #me is ME sugar object
				else: continue  #otherwise get error message about ME not present
			if k in sug.atoms: s.atoms[k]+=sug.atoms[k]*num
			else: print(k + ' is not in atomMass default.  Please add')

	def addIon(s,ui,num):
		atom=ui.addons; mass=ui.addonmass
		used = [a for a,m in ui.ammass] #get list of atoms from atomMass
		if atom.lower()=="none": return
		if atom not in s.atoms: s.atoms[atom]=0
		s.atoms[atom]+=num
		if atom not in used: s.weight+=mass*num  #because H is but Na and K aren't

	def printCS(s,useneg=False):
        #CS = chemical something
		temp=''
		for o in s.order:
			if o in s.atoms: 
				num = s.atoms[o]
				if num>0: temp+=o+str(num)
				if useneg==True: temp+=o+str(num) #for mods in assignMALDI
		return temp
			
		
def getNum(num):
	try: temp = int(num)
	except: return -1
	return temp

def getFirstValues(alist):
	#includes comments with> and headers with mothing!
	nulist=[];co=0
	for e,a in enumerate(alist):
		if a[0]=='#' or '>' in a[0]: co+=1;continue
		if e>co: nulist.append(a[0])

	return nulist

def getAllValues(alist):
	#includes comments with> and headers with mothing!
	nulist=[];co=0
	for e,a in enumerate(alist):
		if a[0]=='#' or '>' in a[0]: co+=1;continue
		if e>co: nulist.append(a)
	return nulist

def readDefaultFile(ui):
    fin=open(ui.defaultfile,'r')
    name='';
    ui.defaults={}
    for line in fin:
        line=line.replace('\n','')
        if '#' in line: #starting new section
            name = line[1:] #to skip # and return
            continue
        if name:
            parts=[];
            if '\t' in line: parts = line.split('\t')
            else:  #must be space  
                p1 = line.split(' ')
                parts = [val for val in p1 if val!=' ' and val!=''] #in case >1 space at a time. 
            if parts:
                if name not in ui.defaults: ui.defaults[name]=[]
                ui.defaults[name].append(parts)  #only one space to separate!

    fin.close()

def updateDefaultFile(afile,name,data):
    fin = open(afile,'r')
    olist = fin.readlines(); fin.close()
    fin = open(afile,'w') #writes over old stuff!
    go=False
    for line in olist:

        if go==True or go=='Pause':
            if '#' in line: go=False; #done updating part of interest
            elif '>' in line: fin.write(line) #copy comments
            if go==True and '>' not in line:
                fin.write(line) #should catch  labels  
                for nul in data: fin.write(makeLine(nul)+'\n'); go='Pause'#this prints off changed lines
                fin.write('\n')  #add a space to make it readable
        if name not in line and go==False: fin.write(line);continue #not correct section - copy
        if name in line:  #wanted name!
            fin.write(line) ; #copy the name line
            go=True
        
            
    fin.close()

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
##################################

	
#--------------------------------------------------------------------------
def getOrder(key,order):
	
	if key in order:
		return order.index(key)
	return 0	

def openFile(filein,shorthand):
	#opens file and returns list of lines
	tlist=[]
	try:
		fin = open(filein,'r')
		for line in fin:
			if 'byonic' in line: return(openByonicFile(filein,shorthand))
			tlist.append(line)
		print (filein,"opened.")
		fin.close()
	except:
		print ("Could not open: ",filein)
	return tlist

def openByonicFile(filein,shorthand):
    #found database file on glycam.  Convert to shorthand for processing
    #format is
    #input - "glytoucan_ac","byonic"
    #input - "G02438LG","HexNAc(1)dHex(2) % 484.174789"
    alist=readByonicDBfile(filein) #returns lists of longhand dic.  Some keys will be missing in list of monosaccharides
    shlist=[];nflist=[]
    longhand={} #flip longhand to keys and shorthand to values
    for k,v in shorthand.items(): longhand[v]=k
    #see if byonic monosaccharides in shorthand - may not be = sulfer groups, etc.
    for adic in alist: #list of dics
        astr=''
        for k,v in adic.items(): #k='Hex',v=#
            aname=''
            if k in longhand: aname=longhand[k] #aname is now shorthand
            if not aname: 
                if k not in nflist: nflist.append(k);
                astr='';break
            astr+=aname+str(v)
        if astr: shlist.append(astr)
    if nflist:
        print('The following monosaccharides were not defined.  Those glycam compositions were skipped.')
        print(nflist)
    print(len(shlist),' compositions converted from '+filein)
    return shlist
    
def writeNewDatabase(ui,eb=""):
	#filein,fileout,flag,manual=getArg(sys.argv)
	#this is where execution starts for a full infile.
	filein=ui.infile
	fileout=ui.outfile
	
	process=ui.process
	outf=False
	fileflag='a'  #for append - for manual entry
	try: 
		fout = open(fileout,'w')
		outf=True
	except:
		print ("Could not open outfile. no database will be written.")
		outf=False
		
	fin=openFile(filein,ui.shorthand)
	if fin=='': 
		print ("Could not open infile.  Entry is manual only.")
		return
	
	for oligo in fin:
		output=calculateOligo(oligo,ui) #output is now list
		aline=''
		for val in output:
			if aline: aline+='\n'
			aline+=val
		
		if outf==True:	
			fout.write(aline+'\n')

	
	if outf==True:		
		fout.close()
		if eb!='':
			eb.delete(0,END)
			eb.insert(0,fileout)
	
def append2database(fileout,aline):
	#aline just needs a return added. 
	message=True  #let program know if outfile could be opened.
	try: 
		fout = open(fileout,'a')
	except:
		try:fout = open(fileout,'w')
		except: message=False		
	fout.write(aline+'\n')
	fout.close()
	return message
	
def readOligo(oligo):
    #returns dict of sugar name:number
    name=''; num=''; adic={}
    for ch in oligo:
        if 'A'<=ch.upper()<='Z': 
            if num: adic[name.lower()]=int(num); name='';num=''
            name+=ch
        if '0'<=ch<='9': num+=ch
    adic[name.lower()]=int(num) #catch last
    return adic

def getStartOpt(ui):
    #it label goes at START, check frequency. Return values for all freq. options
    opt=[] #holds sugar objects. labels is dict of 'AEAB':sugarobj
    #ui.mods = list of mods

    for mod in ui.mods:
        if mod.lower()=='none': return []
        lab=ui.labels[mod]
        
        if lab.where.lower()=='start': 
            opt=[lab]  #every start label goes here except None
            if lab.freq.lower()=='sometimes': opt.append(sugar([],[])) #lab for one sugar and '' for another
        
    return opt

def checkForMe(ui):
    #checks to see if permethylation mod.  Returns that mod, else returns Null
    for mod in ui.mods:
        lab=ui.labels[mod]
        if lab.where.lower()=='me': return mod
    return ''

def getMonoLabels(ui):
    #get which monos are changed and the labels that go on them
    #frequency - if 'always', apply always.  If sometimes and more than 2 labels to the same mono, assume either or.
    opt=[];temp={}
    for mod in ui.mods: #mod='AEAB', etc
        if mod.lower()=='none': return {} #None supercedes all.
        mono = ui.labels[mod].where.lower()  #'s'
        if mono.lower()=='me': continue  #handled elsewhere
        
        if mono in ui.shorthand:  #mono comes in shorthand - make sure it's in library
            mlong=ui.shorthand[mono]
            if mlong not in temp: temp[mlong]=[]
            temp[mlong].append([mod,ui.labels[mod]])  #get all mods for that mono.
            
        else: print('Unknown monosaccharide ',mono)
    for mono,mods in temp.items():  #see if all sometimes have a partner    
        sco=0  #sometimes count
        for items in mods:
            if items[1].freq=='sometimes': sco+=1
        if sco==1: blank=sugar([],[]);temp[mono].append(['',blank])
    
    return temp #dic of sugar:['AEAB',object]
    

def getIonOpt(ui,ends):
    #gets number or numbers of adduct ions
    #returns all end options: [M+Na,M+2Na]
    nu=[]
    a=ui.ionnum;b=0
    if len(ui.ionnum)>2:
        if '-' in ui.ionnum: a,b=ui.ionnum.split('-')
    a=int(a); b=int(b)
    if b==0: b=a
    for r in range(a,b+1):
        for end in ends:
            end.addIon(ui,r)
            nu.append(end)
    return nu

def calculateOligo(oligo,ui):
	#returns list of possible masses for one oligo due to multiple ions
	#oligo is shorthand sugar ie. H5N2
	sugnum={} #this will hold hex:6, for example
	adic=readOligo(oligo) #shorthand dic
	
	#need to match input to monosaccharides
	aname='';sugnum={}
	for k,v in adic.items(): #k='h',v=#
		if k.upper() in ui.shorthand: aname=ui.shorthand[k.upper()]
		elif k.lower() in ui.shorthand: aname=ui.shorthand[k.lower()]
		if not aname: print(k+' not found.  Check the monosaccharide default symbols');aname=k
		sugnum[aname]= v 	
	##Calculate all possible reducing ends	
	ends=[]
	end=ui.treatment[ui.process].copy()	#definition (object) of enzyme released,etc
	end.name='' #reset since stores process names above
	sopt=getStartOpt(ui)  #returns list of objects such as AEAB
	if not sopt: ends.append(end)
	for obj in sopt: 
		te=end.copy()
		te.addSugar(obj,1)
		ends.append(te)
	amod = checkForMe(ui) #returns the me object or '' if not being used
	if amod: 
		for e,end in enumerate(ends):
			if 'Me' in end.atoms: 
				ends[e].addSugar(ui.labels[amod],end.atoms['Me'])
	ends=getIonOpt(ui,ends) #gets adduct ions
	
	##Get monosaccharide labels if exist
	mdic=getMonoLabels(ui) #dic of 'NeuAc':['pT',pT object]
	
	##GET monosaccharides
	sugd=ui.monos  #returns dict of (key,sugar obj)
	glyorder = getFirstValues(ui.defaults['outputOrder']) #order to print out sugar nomenclature
	coreoligo=sugar([],[]) #initialize
	
	for gly in glyorder:  #loop by order. gly=='hex'
		s=sugar([],[]) #initialize monosaccharide
		if gly in sugd: s = sugd[gly].copy()  #get monosaccharide info
		else: print(gly + " is not known. skipping.");continue  #does not exist!
		
		num=0 #how many of s in the oligo
		if gly in sugnum: num = sugnum[gly]
		if num==0: continue  #not all gly will be in sugnum, only ones in oligo
		coreoligo.name+=s.name+str(num)#Hex5
		
		if amod:#Need to check permethylation for every sugar.
			s.addSugar(ui.labels[amod],s.atoms['Me'])#adds weight and atoms
		coreoligo.addSugar(s,num)		#add sugar weight,atoms  to the oligodict  - the atoms anyway.

	##Now put everything together
	nuoligos=[];temp=[]
	for end in ends: 
		end.addSugar(coreoligo,1);
		end.name = coreoligo.name+end.name
		if not mdic: nuoligos.append(end)
		for sh,vals in mdic.items(): #'NeuAc':['pT',pT object]
			if sh in sugnum: #there was a mono label in our oligo
				ml=calcMonoLabels([],[],vals,sugnum[sh],0) #ml=[[[name,obj],[name,obj]]]
				meo=''
				if amod in ui.labels: meo=ui.labels[amod]
				nuoligos+=addMonoLabels(end,ml,sh,meo)
			else: nuoligos.append(end)    #there were no mono labels
	
	output=[]
	for nuo in nuoligos:
		nuo.calcWeight(ui.ammass)
		t = '\t'	
		output.append(nuo.name+t+"%.4f"%nuo.weight+t+nuo.printCS())#+ratios	

	return output	
	
def calcMonoLabels(strs,astr,labels,SAs,wh):
	#wh is which label we're on. labels are 'name',obj
	#strs and astr start off as [],SAs=# differ mono's possible in that sugar
	#strs is list of all combinations. i.e. AA, AB, BB
	nust=[]
	#print('labels',labels)
	while wh<len(labels):	
		lab=labels[wh]  #[name,obj]
		for r in range(len(astr),SAs):	#r is how many letters to print. rep is max
			nust=astr[:];nust.append(lab) #size of astr changes over time
			if len(nust)==SAs: strs.append(nust);
			else: strs=calcMonoLabels(strs,nust,labels,SAs,wh);break
		wh+=1
	return strs

def addMonoLabels(oligo,alist,mono,amod):
    #oligo is a single end+coresugar. ALIST is a list of all label combos.mono=labeled monosaccharide
    #amod is not '' if ME used.
    #This returns a list of all possible options with the incoming oligo as the starting point
    
    if not alist: return [oligo]  #No labels to add  
    oligos=[]; #startatoms=oligo.atoms.copy()
    for a in alist: #a is [['label',object],['label',object]]

        name='*';nuo=oligo.copy()#sugar([],[]); #nuo.atoms=startatoms.copy()#oligo.copy(); #for some reason need to reset atoms even though copying sugar
        for label in a:
            nuo.addSugar(label[1],1,me=amod)  #mass and atom
            if label[0]: name+=label[0][0]  #use first letter only?
            
        if len(name)>1: nuo.name=insertLabel(name+'*',nuo.name,mono)
        oligos.append(nuo.copy())
    return oligos  #list of copies on incoming oligo with different label combos

def insertLabel(label,name,mono):
    #label='*pp* name=NeuAc2Hex5HexNAc2. mono=NeuAc2  Returns NeuAc2*pp*Hex5HexNAc2
    ##separate out label parts
    alist=[]
    astr='';anum=''
    for ch in name:
        if ch.isalpha():
            if anum:
                alist+=[astr,anum]
                astr=''; anum=''
            astr+=ch
        if ch.isnumeric():  anum+=ch
    if anum: alist+=[astr,anum]#catch last
    ##insert label and make new name
    astr='';aflag=False #flag is to put label after # instead of sugar name
    for a in alist:
        astr+=a
        if aflag==True: astr+=label; aflag=False 
        if a==mono: aflag=True
        
    return astr

def testRun():	
    root = Tk()
    root.title("dbMaker")

    db=dbWin(root)
    db.populateWin() 	
    root.mainloop()