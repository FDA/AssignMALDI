#windows for AssignMALDI 
#execute program by typing python AssignMALDI_win.py
import numpy as np
import windowfeatures as wf
import matplotlib.pyplot as plt
import dbmaker as db
import matplotlib
import matplotlib.font_manager as FM
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
from functools import partial #to send in more than event with callbacks
from matplotlib.backend_tools import ToolBase, ToolToggleBase
from AssignMALDI_fun import *
import sys,os,warnings
from PIL import Image as PILimage
matplotlib.use('TkAgg')
plt.rcParams['toolbar'] = 'toolmanager'

warnings.simplefilter("ignore") #to ignore warnings about tool classes

from tkinter import *
if sys.version[0]<'3':
    print("Requires python 3.x.  If you have multiple versions of python, try using the Python3.x executable before the program name.")
    exit()


    
class mainWin():
	def __init__(self,root):
		
		self.root=root
		self.items=[]	
		db.readDefaultFile(ui)
		self.dir=''
		self.plots=[]
		self.fignum=0
		self.root.protocol("WM_DELETE_WINDOW",lambda: self.exit())
		self.eb1=''
		self.eb2=''
		self.dir=''
		self.modlist=[] #so can update if defaults changed
		self.populateWin()
        
	def populateWin(self):
		if self.modlist: self.updateOptions();return#exists!! update default stuff only.
		frame = Frame(root,bd=2)
		frame.grid(row=0, column=0, padx=5, pady=5)
		f1 = Frame(frame,bd=2)
		f1.grid(row=0, column=0, padx=0, pady=0)
		r=0
		wf.makeLabel(self,frame,"* * * I N P U T * * *",r,0,exp=3,sticky=EW);r+=1
		wf.makeFileRow(self,frame,r,0,'Directory with exported spectra in text format','inputdir',type='dir',id=self.dir);
		self.eb1=self.items[len(self.items)-1][0]
		r+=1
		wf.makeFileRow(self,frame,r,0,'Glycan database file','libfile',type='filein',id='');
		self.eb2=self.items[len(self.items)-1][0]
		r+=1
		wf.makeButton(self,frame,"Make Glycan Database",lambda: self.runCalcMass(),r,1,columnspan=2,sticky=E);r+=1
		wf.makeLabel(self,frame,"* * * P R O C E S S I N G    O P T I O N S * * *",r,0,exp=3,sticky=EW);r+=1
		r2=0
		f2=Frame(frame,bd=2); f2.grid(row=r,column=0,columnspan=3,sticky=EW)
		wf.makeCheckButton(self,f2,'Zero baseline.', r2,0,state='off',key='zerob');r2+=1
		wf.makeCheckButton(self,f2,'Smooth Data.', r2,0,state='off',key='smf');
		wf.makeLabel(self,f2,"window_size (ie.11)",r2,1,exp=1,sticky=E); 
		wf.makeEntry(self,f2,r2,2,width=5,text="",key="smwin",exp=1); 
		wf.makeLabel(self,f2,"   polynomial order (ie.3)",r2,4,exp=1); 
		wf.makeEntry(self,f2,r2,5,width=5,text="",key="smord",exp=1);r2+=1 
		wf.makeCheckButton(self,f2,'Calibrate Spectra.', r2,0,state='off',key='usecalib');
		wf.makeLabel(self,f2,"current low mass",r2,1,exp=1,sticky=E);
		wf.makeEntry(self,f2,r2,2,width=8,text="",key="culow",exp=1);
		wf.makeLabel(self,f2,"   current high mass",r2,4,exp=1);
		wf.makeEntry(self,f2,r2,5,width=8,text="",key="cuhi",exp=1);r2+=1
		wf.makeLabel(self,f2,"correct low mass",r2,1,exp=1,sticky=E);
		wf.makeEntry(self,f2,r2,2,width=8,text="",key="colow",exp=1);
		wf.makeLabel(self,f2,"   correct high mass",r2,4,exp=1);
		wf.makeEntry(self,f2,r2,5,width=8,text="",key="cohi",exp=1);r2+=1
		wf.makeCheckButton(self,f2,'Check z-score.',r2,0,state='off',key='cpp');
		wf.makeLabel(self,f2,"z-score cutoff for noise reduction(try 3.0)",r2,2,exp=3,sticky=E); 
		wf.makeEntry(self,f2,r2,5,width=5,text="",key="cutoff",exp=1);r2+=1;r+=3
		wf.makeLabel(self,frame,"Error(dalton)",r,0,exp=1); 
		wf.makeEntry(self,frame,r,1,width=10,text="",key="error",exp=1,type='num'); r+=1
		wf.makeLabel(self,frame,"Assignment must be found in at least this many files to be real.",r,0,exp=1); 
		wf.makeEntry(self,frame,r,1,width=10,text="2",key="minfile",exp=1,type='int'); r+=1
		wf.makeLabel(self,frame,'Look for mod like missed permethylation.',r,0);
		fm=Frame(frame,bd=2); fm.grid(row=r,column=1,columnspan=3,sticky=EW)
		labopt=db.getFirstValues(ui.defaults['modifications'])
		self.modlist=wf.makeCheckButtonList(self,fm,0,0,labopt,text="Choose none or more",key='mod',exp=1)
		wf.makeButton(self,fm,"Edit Defaults",lambda: self.editWin('modifications'),0,1)
		r+=1
		
		wf.makeLabel(self,frame,"* * * O U T P U T    O P T I O N S * * *",r,0,exp=3,sticky=EW);r+=1
		wf.makeCheckButton(self,frame,"Limit M/Z axis to:",r,0,state='off',key='mzr');
		f2 = Frame(frame,bd=2)
		f2.grid(row=r, column=1, padx=0, pady=0)
		wf.makeEntry(self,f2,0,0,width=10,text="",key="mzstart",exp=1,type='num')
		wf.makeLabel(self,f2,"-",0,1,exp=1);
		wf.makeEntry(self,f2,0,2,width=10,text="",key="mzend",exp=1,type='num');r+=1
		wf.makeCheckButton(self,frame,'Use shapes',r,0,state='off',key='useshapes')
		wf.makeButton(self,frame,"Set shapes & colors",lambda: self.shapeMenu(),r,1);r+=1
		wf.makeLabel(self,frame,"Shape size(9-14)",r,0,exp=1,sticky=E); 
		wf.makeEntry(self,frame,r,1,width=10,text="",key="shapesize",exp=1,type='int'); r+=1
		wf.makeCheckButton(self,frame,'Show masses',r,0,state='off',key='usemasses');r+=1
		wf.makeCheckButton(self,frame,'Save N-glycans only.',r,0,state='off',key='oligos');r+=1
		wf.makeLabel(self,frame,"What assignments should be in output file?",r,0,exp=1);
		MODES = [
			("Only Assigned", "False"),#("Only expected N-linked glycans", "pseudo"),
			("Everything", "True")        
			]
		wf.makeRadiobuttons(self,frame,MODES,'True',r,1,'useout',dir='v');r+=3
		
		bf = Frame(root,bd=2);bf.grid(row=r, column=0, padx=5, pady=5,columnspan=3)
		c=0
		wf.makeButton(self,bf,"Assign",lambda: self.GO(),0,c);c+=1
		wf.makeButton(self,bf,"Open Previous",lambda: self.openOld(),0,c);c+=1
		wf.makeButton(self,bf,"Help",lambda: wf.showHelp(ui.helpfile,'main'),0,c);c+=1
		wf.getValues(self.items,ui)
		self.dir = self.eb1.get()
		

	def updateOptions(self):
		labopt=db.getFirstValues(ui.defaults['modifications'])
		self.modlist=wf.updateCheckButtonList(self,self.modlist,labopt)


	def exit(self):
		plt.close('all')
		self.root.destroy()
		
		
	def GO(self):
		
		ui.mods=[]  #reset!
		dict1=vars(ui)  #so can expand on variables in ui as needed
		defaults=db.getAllValues(ui.defaults['modifications']) #returns list of [[name,atom,atom],[name,atom,atom,atom]]
		for pnt,key in self.items:  #pnt=pointer to widget
			val=pnt.get()
			try: val=float(val)  #save as number if it is one
			except: pass
			for d in defaults:
				if key ==d[0] and val==1:  #was selected
					#Calculate mass of mod
					amlist=db.getAllValues(ui.defaults['atomMass'])
					d.insert(1,d[0]) #need a placeholder symbol for dbmaker
					mod = db.sugar(d,amlist)
					mod.calcWeight(amlist)
					ui.mods.append([mod.name,mod.weight,mod.printCS(useneg=True)])
				 
			dict1[key]=val

		wf.saveValues(dict1,os.path.join(ui.inputdir,ui.UIfile))
		try: files = os.listdir(ui.inputdir)
		except: 
			print("could not find files in input directory")
			return False

		ui.infiles=[]  #reset!
		ui.pfiles=[];tempfiles=[];orig=False
		for file in files:
			if 'pks' in file: continue
			if 'uifile' in file: continue
			if 'sum' in file: continue
			if '.txt' not in file: continue
			if '-proc' in file: continue;orig=True;
			if ' ' in file: file = killSpaces(ui.inputdir,file)
			nufile = os.path.join(ui.inputdir,file)
			ui.infiles.append(nufile)
		ui.infiles=saveProcFiles(ui.infiles)  #no orig, copy all files to infiles.  First time
		wf.saveDir(ui)	
		if ui.cpp=='yes': #just looking at picked peaks - not processing
			ppfile=teststart(ui) #file with list of iterators[s,m,e]

			pw=plotWin(ui)
			pw.testplot(ppfile)
		else:
			start(ui)
			pw=plotWin(ui)
			pw.addAllData()
		
	def openOld(self):
		#opens previously processed data
		dict1=vars(ui)  #so can expand on variables in ui as needed
		for pnt,key in self.items:  #pnt=pointer to widget
			val=pnt.get()
			try: val=float(val)  #save as number if it is one
			except: pass
			dict1[key]=val
				
		
		ui.glylist=getglylist(ui.libfile)
		
		try: files = os.listdir(ui.inputdir)
		except: 
			print("could not find files in input directory")
			return False
		
		ui.infiles=[]  #reset!
		ui.pfiles=[]
		
		for file in files:
			if 'pks.txt' in file: continue
			if 'uifile' in file: continue
			if 'sum' in file: continue
			if '.txt' not in file: continue
			if '-orig' in file: continue  #in theory have something else?
			if 'pks-gp' in file: ui.pfiles.append(os.path.join(ui.inputdir,file));continue
			if '-proc' in file: 
				nufile = os.path.join(ui.inputdir,file)
				ui.infiles.append(nufile)
		
		pw=plotWin(ui)
		pw.addAllData()		
		
		
	def AvgOnly(self):	
		
		nufiles=[]
		dict1=vars(ui)  #so can expand on variables in ui as needed
		
		for pnt,key in self.items:  #pnt=pointer to widget
			
			val=pnt.get()
			try: val=float(val)  #save as number if it is one
			except: pass
			
			dict1[key]=val
				
		wf.saveValues(dict1,os.path.join(ui.inputdir,ui.UIfile))
		glylist=getglylist(ui.libfile)
		try: files = os.listdir(ui.inputdir)
		except: 
			print("could not find files in input directory")
			return False
		for file in files:
			if 'pks' not in file: continue
			nufile = os.path.join(ui.inputdir,file)
			print (nufile)
			nufiles.append(nufile)
		wf.saveDir(self.ui)		
		data=averageList(nufiles,ui)	#returns [name,mass,avgint,stdev]
		data=orderList(data,ui)#glylist,useall=ui.useout) #order by library and list everything in lib if useall==true
		write2DList(os.path.join(ui.inputdir+ui.outfile),data,flag='w')

		
		
	def runCalcMass(self):
		from dbmaker import dbWin
		t=Toplevel()
		t.wm_title("dbMaker")
		db=dbWin(t)
		db.populateWin() 	
		
	def editWin(self,what):
		#editWin is under dbmaker!
		#what = 'modifications' = finishes title
		t=Toplevel()
		t.wm_title("Edit default "+what)
		ew=db.EditWin(t,ui,self)
		ew.populateWin(what,ui.defaults[what],Me=False)
		
	def shapeMenu(self):
		#editWin is under dbmaker!
		#what = 'modifications' = finishes title
		t=Toplevel()
		t.wm_title("Edit default shapes")
		ew=db.EditWin(t,ui,self)
		ew.shapeWin("Shapes",ui.defaults["Shapes"])

######################################################

class plotWin():
    def __init__(self,ui):
        self.fig = None
        self.tm=None
        self.zid=None 
        self.qtfig=None #attempt to add bars, put fig in qtfig
        self.cw=None  #click win
        ui.figco+=1
        self.ypos=[]  #list of axis positions[[y0,y1]]. goes with axl
        self.aw=None #averagewin
        dpi = ui.dpi#wf.getDPI()
        #wx,wy=wf.getScreenSize()
        self.width=ui.screenwidth/dpi*0.9
        self.height=ui.screenheight/dpi*0.9
        self.axl=self.setupfig()
        self.inputdir = ui.inputdir
        self.pfiles = ui.pfiles
        self.lfont=ui.lfont
        self.useshapes=ui.useshapes
        self.usemasses=ui.usemasses
        self.maxy=0 #need this for shapes - get_yaxis not returning correct #. In window everything synced to max Y
        #a = ScrollableWindow(self.fig)
        self.shapesize = ui.shapesize
        
    def setupfig(self):
        #run from init
       
        plt.ion()  #turns on interactive mode
        fig=plt.figure(figsize=(self.width,self.height)) 
        fig.canvas.manager.window.wm_geometry("+50+50") #initial placement on screen
        fig.canvas.manager.set_window_title('Spectra Window')
        tm=fig.canvas.manager.toolmanager
        
        tm.remove_tool('help')
        
        tm.add_tool('P', peakSelectButton)
        tm.add_tool('Save',saveDataTool)
        tm.add_tool('+',zoominTool)  #TOO SLOW :(
        tm.add_tool('-',zoomoutTool)
        tm.add_tool('<',panLeftTool)
        tm.add_tool('>',panRightTool)
        tm.add_tool('^',zoomUpTool)
        tm.add_tool('v',zoomDownTool)
        tm.add_tool('AvgPlot',averageWinTool)
        tm.add_tool('?',helpTool)
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('Save'), 'io')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('+'), 'zoompan')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('-'), 'zoompan')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('^'), 'zoompan')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('v'), 'zoompan')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('<'), 'zoompan')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('>'), 'zoompan')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('P'), 'zoompan')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('AvgPlot'), 'io')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('?'), 'io')
        
        fig.canvas.mpl_connect('pick_event',onpick)
        fig.canvas.mpl_connect('close_event',onclose)
        self.tm = tm
        self.zid=self.tm.toolmanager_connect('tool_trigger_zoom',onpress)
        axl=[]
        co=1
        for f in ui.infiles:
            num = len(ui.infiles)*100 + 10 + co
            ax=''
            if axl:
                ax=fig.add_subplot(num, sharex=axl[0], sharey=axl[0])
            else: 
                ax=fig.add_subplot(num)
            
            if ui.mzr=='yes':
                try: ax.set_xlim([int(ui.mzstart),int(ui.mzend)])
                except: pass  #in case something other than a number entered.
            
            axl.append(ax)
            box=ax.get_position()
            self.ypos.append([box.y0,box.y1])
            axl[-1].title.set_text(getBasename(f))
            axl[-1].title.set_x(0)
            if ui.cpp=='yes': break #only make one subplot.
            co+=1
        fig._gid='pw'+str(ui.figco)
        self.fig=fig
        ui.figdic[fig._gid]=self #self is pw
        return axl  #returns to init.

    def clear(self):
        self.fig.clear()
        
    
    def addAllData(self):
        DL=[];maxY=0
        for r in range(0,len(ui.infiles)): 
            temp,py=self.addData(r)
            DL.append(temp)
            if py>maxY: maxY=py
        self.addLabels(DL,maxY)    
        plt.xlabel("m/z",fontsize=14)
        plt.draw(); #plt.pause(0.01)

    def addData(self,idx):
        #idx is iterator to which file to use
        X,Y = getdata(ui.infiles[idx],numonly=True) #all X,Y in spectrum
        mX,mY,labels,isowin,isowhere=getProcData(idx)
        DL=[idx,mX,mY,labels,isowin,isowhere]
        ax=self.axl[idx]
        if ui.mzr=='yes': #adjust mz axis
            ans=getMaxY(X,Y,ui)
            ax.set_ylim([0,ans])

        ax.plot(X,Y,linewidth = 0.5,color='b')
        ax.set_ylabel('Intensity',fontsize=14)
        maxh=max(mY)
        
        if self.useshapes=='yes': 
            makeShapeDic()
            ax.callbacks.connect('ylim_changed',partial(on_ylim_change,axl=self.axl,ax=ax))
        y1,y2 = ax.get_ylim()    
        
        return DL,y2
        
        
        
    def addLabels(self,alist,maxY):
        #called after addData - need to open all files and get max Y before calculating where to put images
        for idx,mX,mY,labels,isowin,isowhere in alist: #
            xo=0;yo=0;ax=self.axl[idx]
            for l,txt in enumerate(labels):
                agid=str(idx)+'-'+txt#str(l)
                ax.scatter(mX[l],mY[l],color='crimson',s=10,picker=True,gid=agid) #added gid to pair with label.
                yadj=0;xadj=0
                
                if self.useshapes=='yes': 
                    useShapeLabels(txt,ax,xo,yo,mX[l],mY[l],agid,maxY,self.shapesize,self.usemasses,self.fig)
                    #if self.usemasses=='yes':
                    #    abbox=ab.get_window_extent(self.fig.canvas.get_renderer()) #returns dimensions
                    #    xr,yr=wf.getDotsToDataRatio(ax)
                    #    
                    #    ax.annotate(str(mX[l]),(mX[l],mY[l]+abbox.height/yr),size='x-small', verticalalignment='bottom', horizontalalignment='center',picker=True,gid=agid)
                else: 
                    if self.usemasses=='yes': txt+='-'+str(round(mX[l],1))
                    ax.annotate(txt,(mX[l],mY[l]+maxY*0.01),rotation=90, size='x-small', verticalalignment='bottom', horizontalalignment='center',picker=True,gid=agid)
                ax.vlines(isowhere[l],0,isowin[l],picker=True,gid=agid)
                


    def testplot(self,afile):
        #this plots win with just picked peaks for z-score check  
        idx=0
        X,Y = getdata(ui.infiles[idx],numonly=True) #all X,Y in spectrum
        alist=readFile(afile,False)
        if not alist: return
        ax=self.axl[idx]
        if ui.mzr=='yes':
            ans=getMaxY(X,Y,ui)
            ax.set_ylim([0,ans])
        ax.plot(X,Y,linewidth = 1.0,color='b')
        ax.set_ylabel('Intensity',fontsize=14)
        pX=[];pY=[]
        for s,m,e in alist:
            if m>len(X):
                continue
            x=X[m];y=Y[m]
            pX.append(x);pY.append(y)
        ax.plot(pX,pY,'ro')
        
class averageWin():
    def __init__(self,dpi):
        self.width=ui.screenwidth/dpi*0.7  #converts to inches
        self.height=ui.screenheight/dpi*0.7
        self.dpi=dpi
        self.fig=None  #set up in makePlot called from setupfig
        self.setupfig()

        
    def setupfig(self):
        #run from init
        X,Y,Z=self.getData()
        fig =plt.figure(figsize=(self.width,self.height))
        fig.canvas.manager.set_window_title('Average Plot')
        fig.canvas.manager.window.wm_geometry(f'+{10}+{70}') #directs where window shows up on screen
        tm=fig.canvas.manager.toolmanager
        tm.remove_tool('help')
        tm.add_tool('Sort',sortTool)
        tm.add_tool('?',helpTool)
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('Sort'), 'io')
        fig.canvas.manager.toolbar.add_tool(tm.get_tool('?'), 'io')
        ui.figco+=1
        fig._gid='aw'+str(ui.figco)
        ui.figdic[fig._gid]=self
        self.fig=fig
        self.makePlot(X,Y,Z)
        
    def getData(self):
        path,end = os.path.split(ui.infiles[0])
        infile = os.path.join(path,'MS-sum.txt')
        X,Y,Z=getdata(infile,sp='\t',ix=0,iy=4,iz=5,header=True) #name,intensity,std
        return X,Y,Z    
        
    def getWinWidth(self,fs,num):
        #trying to avoid label overlap
        #fs = fontsize (12), num=number of labels.
        minfs = 9  #minimum font size
        minxtra=6  #minimum space to add to font
        xtra=10  #extra space to add to fontsize
        nuwid=((fs+xtra)*num)/self.dpi
        while fs>minfs:
            while xtra>minxtra:
                if nuwid>self.width/0.7:  #full screen size
                    xtra-=1
                    nuwid=((fs+xtra)*num)/self.dpi
                else: break
            if nuwid>self.width/0.7:  #full screen size
                fs-=1
                nuwid=((fs+xtra)*num)/self.dpi
            else: break    

        return nuwid,fs
        
    def makePlot(self,X,Y,Z):    
        #get length of longest label so can adjust margin
        maxl=0;ee=0;madj=0
        for e,ml in enumerate(X):
            if len(ml)>maxl: maxl=len(ml);ee=e

        fdim=wf.getTextDimensions(X[ee],11,'Arial',ui.dpi) #returns (x,y)   
        madj=fdim[0]/(self.height*self.dpi) #xsize/screenheight*dpi
        fig=self.fig
        nuwid,fs =self.getWinWidth(fdim[1],len(X)) #ysize,
        fig.set_size_inches(nuwid,self.height) #try to keep labels from overlapping
        ax=fig.add_subplot(111)
        ax.bar(X,Y,yerr=Z)
        ax.set_ylabel('Percent Abundance (%)',fontsize=16)
        ax.set_xticklabels(X,rotation=90,fontsize=fs)#45,ha='right')
        
        plt.subplots_adjust(bottom=madj)
        plt.margins(0.005) #gets rid of extra space between Y-axis and first bar
        plt.show()
        self.fig=fig
    
    def sort(self):
        #want to sort data by #HexNAc, then #Hex
        X,Y,Z=self.getData()  #name, intensity, std
        lablist=[];
        options=[]
        #first figure out all monos
        for e,lab in enumerate(X):
            tdic=makeDicFromName(lab,ui) #breaks it into [sug,#,sug,#]
            for k,v in tdic.items():
                if k not in options: options.append(k)
        #get order
        t=Toplevel()
        t.wm_title('sort by')
        sw = sortOrderWin(t,options,X,Y,Z,self)
                
        
     
class sortOrderWin():
    '''pops open when user clicks on sort in Table'''
    def __init__(self,root,options,X,Y,Z,aw):
        #root = toplevel window; options = list of label info
        self.root=root
        self.order=[]
        self.items=[]
        self.X=X;self.Y=Y;self.Z=Z
        self.aw=aw
        f1 = Frame(root,bd=2)
        f1.grid(row=0, column=0, padx=0, pady=0)
        
        r=1
        wf.makeLabel(self,f1,"Sort in what order?",r,0,exp=1); r+=1
        wf.makeLabel(self,f1,"first by:",r,0,exp=1);
        wf.makeDropDownMenu(self,f1,options,options[0],r,1,'0',sticky=W); r+=1
        co=1
        for o in options[1:4]:  #limits # of sortbys to 4
            wf.makeLabel(self,f1,"then by:",r,0,exp=1);
            wf.makeDropDownMenu(self,f1,options,o,r,1,str(co),sticky=W); r+=1
            co+=1
        		
        f2=Frame(f1,bd=2)
        f2.grid(row=r, column=0, padx=0, pady=0, columnspan=3)
        wf.makeButton(self,f2,"Sort",lambda: self.sort(),0,1)
        wf.makeButton(self,f2,"Cancel",lambda: self.cancel(),0,2)
        	
        
    def getValues(self):
        #Gets user-entered values assign and rbchoice
        for pnt,key in self.items: #this should be in order already key=='0','1',etc
            ans=pnt.get()
            if ans in self.order: break  #assume finished?
            self.order.append(ans)
                
    def cancel(self):
        self.root.destroy()
        
    def sort(self):
        ##continuation of sort under AverageWin
        self.getValues() #user decides how to sort
        #link options with names
        lablist=[]
        for e,lab in enumerate(self.X):
            tdic=makeDicFromName(lab,ui) #breaks it into [sug,#,sug,#]
            tlist=[]
            for o in self.order: #this makes lists of [2,5,0,0] for sorting
                if o in tdic: tlist.append(tdic[o])
                else: tlist.append(0)
            tlist.append(e)    
            lablist.append(tlist) #tlist is [2,5,0,0,e]
            ol=len(self.order) #will be at least 2   
        if ol==2:lablist=sorted(lablist,key=lambda x:(x[0],x[-1]))
        if ol==3:lablist=sorted(lablist,key=lambda x:(x[0],x[1],x[-1]))
        if ol==4:lablist=sorted(lablist,key=lambda x:(x[0],x[1],x[2],x[-1]))
        if ol==5:lablist=sorted(lablist,key=lambda x:(x[0],x[1],x[2],x[3],x[-1]))  #(x[0],x[1],x[2]) for multidimensions
        #make new lists with proper order.
        nuX=[];nuY=[];nuZ=[]
        for lab in lablist: 
            e=lab[-1]
            nuX.append(self.X[e]); nuY.append(self.Y[e]);nuZ.append(self.Z[e])
        self.aw.fig.clear()
        self.aw.makePlot(nuX,nuY,nuZ)
        self.cancel()
        
#####################CLICKS and PRESSES##########################
def onpress(event):
    '''unselects pick button when zoom selected'''
    if getattr(event.tool,'toggled')==False: return
    tm=event.tool.toolmanager
    for group, active in tm.active_toggle.items():
        
        if group!='default':
            if isinstance(active,set):
                if 'P' in active: tm.trigger_tool('P')
            else:
               if active!=None: self.tm.trigger_tool(active)
        
def onclose(event):
    '''want to override close to remove window from ui.figdic'''
    if event.canvas.figure._gid in ui.figdic:
        ui.figdic.pop(event.canvas.figure._gid)
        plt.close(event.canvas.figure)

def onclick(event,fig):
    ###This calls peak picking window. 
    #fig is pw
    dpi=fig.dpi
    ww=fig.get_figwidth()*dpi

    if not event.inaxes: return  #must click in a subplot
    if ui.figdic[fig._gid].cw: ui.figdic[fig._gid].cw.cancel()
    t=Toplevel()
    t.wm_title('pick peak')
    t.geometry(f'+{int(ww/2)}+{60}')#gets location of main window
    ui.figdic[fig._gid].cw = clickWin(t,event)

def onpick(event):
    ###when a pre-existing peak or label is selected - delete both
    #first make sure peak selection button is pressed.
    if getattr(event.canvas.manager.toolmanager.get_tool('P'),'toggled')==False: return
    #which one was picked: label or dot
    aflag='dot'
    adic = event.artist.properties()
    gid=event.artist.get_gid()
    if 'fontsize' in adic:  aflag='text' #label picked
    event.artist.remove()
    #find partner
    for ax in event.canvas.figure.axes:
        stuff=ax.collections #default is dots
        for c in stuff:
            if c.get_gid()==gid: c.remove();  ##ID's match so they are a pair.
        for c in ax.texts:
            if c.get_gid()==gid: c.remove(); ##ID's match so they are a pair.
        for c in ax.artists:
            if c.get_gid()==gid: c.remove();
    

def saveChanges(fig):
    ###To save all changes made in spectra to file.Called when toolbar button clicked
    pw = ui.figdic[fig._gid]
    for ax,f  in zip(pw.axl,pw.pfiles):
        nudata=[];isowhere=[];isowin=[];olddata=[]
        for c in ax.collections: #all stuff currently in window
            agid=c.get_gid() #nupks = "name mass chem"
            
            if agid==None: continue
            if ' ' not in agid:
                p2=agid.split('-') #separates axis name from sugar name
                if p2[1] not in olddata: olddata.append(p2[1]);#list of everything from old file that's still there
                continue #gids=spectra-line#(aka order printed)
            parts = agid.split(' ') #has full agid, so NEW!
            temp = c.get_offsets()#returns [[x,y]]
           
            dot=False
            if temp[0][0]!=0 or temp[0][1]!=0: dot=True
            #try: #was saying _is_filled doesn't exist on test computer
            #    if c._is_filled==True: dot=True
            #except: pass
            
            if dot==True: 
                name=parts[0] #default assignment
                if '-' in parts[0]: 
                    np=parts[0].split('-') #goes from 0-name to [0,name]
                    name=np[1]
                nudata.append([name,temp[0][0],parts[1],temp[0][1]])

            else: #it's an isowin set
                temp1=[]; temp2=[]
                for path in c._paths:
                    for obj in path.vertices: 
                        xi=obj[0];yi=obj[1]
                        if yi!=0.0: temp1.append(xi);temp2.append(yi)
                isowhere.append(temp1); isowin.append(temp2)
       
        #adding to -gp file for now.  Will add to pk file when averaged.
        t='\t'; olddata.sort()

        ###update files
        #first, read in file
        fin = open(f,'r')
        flist = fin.readlines()
        fin.close()
        #now overwrite file - have to stick peak info before '###'
        fout = open(f,'w')
        hatchflag=False;deleted=[]
        for fline in flist:
            if 'Name' in fline: fout.write(fline);continue  #header
            if hatchflag==False and '###' not in fline:
                parts=fline.split('\t')
                if parts[0] not in olddata: #name was in file but missing in spectra
                    deleted.append(float(parts[1])); #need to delete matching iso data later-save mass
                    continue
            if hatchflag==True and deleted: #make sure peaks in spectra are in old file. skip if not
                anum=float(fline[1:fline.index(',')]) #gets number
                if abs(anum-closest(deleted,anum))<0.5: continue
                 
            if '###' in fline:
                hatchflag = True
                for al in nudata: #prints new peaks before ###
                    aline=al[0]+t+'%.4f'%float(al[1])+t+'%.4f'%float(al[2])+t+'%.0f'%al[3]+'\n'
                    fout.write(aline)
            fout.write(fline); #print('fline',fline)       
        for iwh,iwi in zip(isowhere,isowin):
            aline = str(iwh)+'\t'+str(iwi)+'\n'
            fout.write(aline)
        fout.close()
        print(f,'updated')
    updateAverages(ui)
    
def getBasename(afile):
    #os gets filename, but I want the name without the .txt and -proc
    bname = os.path.basename(afile)
    skip=['-proc','.txt','.']
    for sk in skip:
        if sk in bname: 
            ii = bname.index(sk)
            return bname[:ii]
    return bname
        
    
####################CLICK WIN######################3            
class clickWin():
	'''pops open when user clicks on a peak'''
	def __init__(self,root,event):
		#root = toplevel window
		self.root=root
		self.items=[]
		self.rblist=[]  #holds radio buttons
		self.event=event
		self.X=event.xdata
		self.Y=event.ydata 
		box = event.inaxes.figbox
		self.y0=box.y0  #bottom boundry of axis
		self.plot=None
		self.assign='' #shorthand entry
		self.rbchoice='' #radiobutton entry
		self.rbassign=''
		self.pw = ui.figdic[event.canvas.figure._gid]
		f1 = Frame(root,bd=2)
		f1.grid(row=0, column=0, padx=0, pady=0)
		alist,blist=findByMass(self.X,ui,ui.error)#alist gets printed out to window.  Blist is name,mass,chem
		clist,dlist=guessUsingBlocks(self.X,ui)

		r=1
		wf.makeLabel(self,f1,"Picked M/Z:  "+str(round(self.X,2)),r,0,exp=1); r+=1 
		wf.makeLabel(self,f1,"Assign As:",r,0,exp=1); 
		wf.makeEntry(self,f1,r,1,width=20,text="",key="assign",exp=1); r+=1

		MODESa = [(a,b) for a,b in zip(alist,blist)]
		MODESb = [(a,b) for a,b in zip(clist,dlist)]
		if MODESa or MODESb: wf.makeLabel(self,f1,"    Name           Delta        Glygen",r,1);r+=1
		if len(MODESa)>0: wf.makeLabel(self,f1,"From Library:",r,0)
		if len(MODESb)>0:wf.makeLabel(self,f1,"Guess:",r+len(MODESa),0)
		MODESa+=MODESb
		self.rblist=wf.makeRadiobuttons(self,f1,MODESa,'',r,1,'rbchoice',dir='v');r+=len(MODESa)+len(MODESb)
		
		f2=Frame(f1,bd=2)
		f2.grid(row=r, column=0, padx=0, pady=0, columnspan=3)
		wf.makeButton(self,f2,"Assign",lambda: self.assignpk(),0,1)
		wf.makeButton(self,f2,"Cancel",lambda: self.cancel(),0,2)
		
		
	def getValues(self):
		#Gets user-entered values assign and rbchoice
		for pnt,key in self.items:
			ans=pnt.get()
			if not ans: continue
			if key=='assign': self.assign=ans
			if key=='rbchoice':
				self.rbchoice=ans  #saves name,mass,comp which is needed iso calculations
				parts=ans.split(' ')# separates assignment from #
				self.rbassign=parts[0] #for assignment


	def cancel(self):
		self.root.destroy()
		
	def setList(self,key,value):
		#for text widgets only!  Value is a list
		aline='';ww=20
		for val in value:
			if len(val)>ww: ww=len(val)
			if aline: aline+='\n'
			aline+=val
		for wid,k in self.items:  #find the box in self.items
			if k==key:
				wid.config(width=ww,height=len(value))
				wid.delete('1.0',END)
				wid.insert(END,aline)
		
	def assignpk(self):
		#takes in user assignment from window and applies to spectrum
		self.getValues()
		#figure out which axis
		if not self.rbassign and not self.assign: print("must have an assignment to add a peak");return
		txt=self.assign;aline=self.assign
		if not txt: aline=self.rbchoice; txt=self.rbassign
		
		err=0.00005  #y0 values should be equal, but just in case using a small error.
		wh=0
		for e,v in enumerate(self.pw.ypos):  #different subplots
			if v[0]-err<self.y0<v[1]+err: wh=e
		ax=self.pw.axl[wh];X=self.X;Y=self.Y    
		agid=str(wh)+'-'+aline

		ax.scatter(X,Y,color='cyan',picker=True,s=10, gid=agid) #using gid to store data
		if ui.useshapes=='yes': 
			y1,y2 = ax.get_ylim()
			useShapeLabels(txt,ax,0,0,X,Y+Y*0.05,agid,y2,ui.shapesize,ui.usemasses,self.event) #if I use self.pw.fig then plot redraws.  Bad.
			
		else:
			if ui.usemasses=='yes': txt+='-'+str(round(X,1))
			ax.annotate(txt,(X,Y+Y*0.05),rotation=90, size='x-small', verticalalignment='bottom', horizontalalignment='center',picker=True,gid=agid)
		###Need to add isowin, isowhere
		iX,iY=makeisotrace(aline,X,Y,ui)
		ax.vlines(iX,0,iY,picker=True,gid=agid)
		plt.draw()
		self.event.canvas.flush_events()
		
		
#########################TOOL BUTTONS#######################		
def testImage(iconfile):
    #image files failing after update so not stable.   Adding this so will default to name if fail.
    afile = os.path.join(sys.path[0],iconfile)
    
    try:
        if checkPermissions(afile,pri=False)=='': return None
        else: return afile  #filename
    except: return None
    
class peakSelectButton(ToolToggleBase):        
    '''turns on ability to select or deselect peaks'''    
    default_keymap = 'P'
    description = 'Select or unselect pick peaks'
    default_toggled = False
    image=testImage("pkpkicon.png")
    name='P'
    
    def __init__(self, *args,**kwargs):
        
        self.cid=''
        super().__init__(*args,**kwargs)
                
    def enable(self, *args):
        '''if pick button picked, then make other buttons pop up'''
        self.manualPick(True)
        tm=self.figure.canvas.manager.toolmanager
        for group, active in tm.active_toggle.items():
            if group=='default' and active!=None: tm.trigger_tool(active) #should untoggle button

    def disable(self, *args):
        self.manualPick(False)

    def manualPick(self,state):
        self.cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)
        if state==False:   self.figure.canvas.mpl_disconnect(self.cid)

    def onclick(self,event):
        onclick(event,self.figure)
        
class zoominTool(ToolBase):
    '''zoomin by 10%'''
    default_keymap='+'
    description = 'Zoom in 10 percent'
    image=testImage("zoomin.png")
    name = '+'
    
    def trigger(self, *args, **kwargs):
        ax = self.canvas.figure.axes[0]
        x1,x2 = ax.get_xlim()
        half=(x2-x1)/2
        x1=half*(0.1)+x1; x2=x2-half*(0.1)
        ax.set_xlim(x1,x2)
        self.canvas.draw()

class zoomoutTool(ToolBase):
    '''zoom out by 10%'''
    default_keymap='-'
    description = 'Zoom out 10 percent'
    image=testImage("zoomout.png")
    name = '-'
    
    def trigger(self, *args, **kwargs):
        ax = self.canvas.figure.axes[0]
        x1,x2 = ax.get_xlim()
        half=(x2-x1)/2
        x1=x1-half*(0.1); x2=x2+half*(0.1)
        ax.set_xlim(x1,x2)
        self.canvas.draw()
        
class zoomDownTool(ToolBase):
    '''zoom down Y-axis - can't see tops of peaks'''
    default_keymap='v'
    description = 'Zoom down 20% on Y-axis (make peaks smaller)'
    name='v'
    
    def trigger(self, *args, **kwargs):
        ax = self.canvas.figure.axes[0]
        y1,y2 = ax.get_ylim()
        
        ax.set_ylim(y1,y2*1.2)
        self.canvas.draw()

class zoomUpTool(ToolBase):
    '''zoom up Y-axis - can't see tops of peaks'''
    default_keymap='^'
    description = 'Zoom up by 20% on Y-axis (make peaks bigger)'
    name='^'
    
    def trigger(self, *args, **kwargs):
        ax = self.canvas.figure.axes[0]
        y1,y2 = ax.get_ylim()
        ax.set_ylim(y1,y2*0.8)
        self.canvas.draw()   
        
class saveDataTool(ToolBase):
    '''pulls data from chart and updates assignment files'''
    default_keymap='a'
    description = 'Save Assignment Changes'
    image=testImage("savedata.png")
    name="Save"
    
    def trigger(self, *args, **kwargs):
        saveChanges(self.canvas.figure)

class helpTool(ToolBase):
    '''pulls data from chart and updates assignment files'''
    default_keymap='?'
    description = 'Help'
    name="?"
    
    def trigger(self, *args, **kwargs):
        #window title should match that in the helpfile!
        wf.showHelp(ui.helpfile,self.canvas.manager.window.wm_title())
        
class panLeftTool(ToolBase):
    '''pan left 90% of screen'''
    default_keymap='<'
    description = 'Pan Left'
    name='<'
    
    def trigger(self, *args, **kwargs):
        ax = self.canvas.figure.axes[0]
        x,y=ax.lines[0].get_data()
        x1,x2 = ax.get_xlim()
        dif=(x2-x1)
        diff=dif*0.9
        x1=x1-diff; x2=x2-diff
        min=x[0]-x[0]*0.01  #not exactly 0
        if x1<min: x1=min;x2=min+dif
        ax.set_xlim(x1,x2)
        self.canvas.draw()

class panRightTool(ToolBase):
    '''pan right 90% of screen'''
    default_keymap='>'
    description = 'Pan right'
    name='>'
    
    def trigger(self, *args, **kwargs):
        ax = self.canvas.figure.axes[0]
        x,y=ax.lines[0].get_data()
        x1,x2 = ax.get_xlim()
        dif=(x2-x1)
        diff=dif*0.9
        x2=x2+diff;x1=x1+diff
        max=x[-1]+x[-1]*0.01  #not exactly max
        if x2>max: x2=max;x1=max-dif
        ax.set_xlim(x1,x2)
        self.canvas.draw()
        
class averageWinTool(ToolBase):
    '''Average Window.  Called from pw'''
    default_keymap='A'
    description = 'Show plot of average percent abundance versus m/z'
    name='AvgPlot'
    
    def trigger(self, *args, **kwargs):
        #hopefully self.canvas.figure == figures in figdic!
        dpi=self.canvas.figure.dpi
        ui.figdic[self.canvas.figure._gid].aw = averageWin(dpi)

class sortTool(ToolBase):
    '''Sorts stuff in Average Window.  Called from average Window'''
    default_keymap='S'
    description = 'Sort oligos by number of HexNAc then Hex'

    name='Sort'
    
    def trigger(self, *args, **kwargs):
        ui.figdic[self.canvas.figure._gid].sort()        
                
########################Other Stuff#######################3        
def on_ylim_change(event,axl,ax): 
    #Adjusts images when present.
    #axl - lists of subplots
    
    y1,y2 = ax.get_ylim() #need ax to get correct y2
    all=True;first=ax._viewLim.height #all are the same-already adjusted coming from home button
    for a2 in axl: 
        if a2._viewLim.height!=first: all=False #something changed
    if len(axl)==1: all=False  
    if all==True: return
    
    xr,yr=wf.getDotsToDataRatio(ax,y2) 
    for ax in axl:
        calcYadj_update(ax,xr,yr,y2)
        
    
    
class UI():
	#Stores all user-input values from main window + other things
	lastdir = 'assignMaldiOD.txt'  #name of file that saves the last directory used.  Under programming directory where exe called
	UIfile = 'uifile.txt' #file that stores values last used.  Under last directory
	inputdir=''
	infiles=[]
	#toutfiles=[] #stores nufiles made at start used to hold processed data
	outfile = 'MS-sum.txt'
	libfile = 'library_NaPM.txt'
	torder={} #to save order while playing with library file?
	order=['NeuGc','NeuAc','Pc','HexA','dHex','Hex','HexNAc']
	error = 0.8
	cutoff = 3.0  #zscore cutoff
	limit = [(870,192),(4000,54)]
	mph=60 #minimum peak height
	pmf='yes' #if yes then look for incomplete permethylation
	cpp='no' #if yes then show picked peaks - only gives first graph for now = red dots
	minfile = 2  #files peak must be in to be printed in sum file
	oligos='no' #if no, assign hex8, hex9, hex10..if 'yes', assign but don't save
	smf='no' #use smooth function
	smwin=5 #must be odd and bigger than smord
	smord=3
	useout='allN'  #what to output - everything (true),just assigned (False),just N-glycs(allN), only assigned N-glys(someN)
	mods=[] #name,mass,formula
	figco=1
	figdic={} #fig:pw
	mzr = 'no' #adjust mz axis?
	mzstart = 1000
	mzend = 5000
	glylist=[]
	cw=None  #clickwin
	pw=None  #plotwin.  Stores axl and fig
	blocks=[] # [mass-diff,name-diff,chem-diff(dic)] #holds building blocks
	pfiles=[]  #holds list of files that hold processed data for use with GUI
	aw=None # points to average window
	pickedpks='pickedpks.txt' #for use with teststart.
	defaults={} ##stores values from default file. name:[values]
	defaultfile="assignMaldi_defaults.txt"
	helpfile="assignMaldi_help.txt"
	usecalib='no'
	culow=0 #current low m/z
	cuhi=0 #current high m/z
	colow=0 #correct low m/z
	colhi=0 #correct high
	zerob='no' #zero baseline?
	lfont='DejaVu Sans' #shapefont #'DejaVu Sans'  #label font
	useshapes='no'
	shapedic={}
	shapesize=10
	usemasses='no'
	dpi=96  #comes from root.
	screenheight=0
	screenwidth=0
	byonicDB='glygen_database.txt'
	byoniclist=[] #filled first time byonicDB is read - dic of glycans 072822
	
def getdata(afile,sp=' ',ix=0,iy=1,iz='',header=False,numonly=False):
	#Gets X,Y data from spectrum file
	##ix=x column. iy=y column
	X=[];Y=[];Z=[]
	fin = open(afile,'r')  #should be m/z(space)intensity
	for line in fin:
		if header==True: header=False; continue #skip first line
		pp = mysplit(line)
		if ix<len(pp) and iy<len(pp): #skip lines if both x and y not present?
			if numonly==True and isnum(pp[ix])==False: continue #header?
			X.append(tonum(pp[ix]))
			Y.append(tonum(pp[iy]))
			if iz: Z.append(tonum(pp[iz]))
			
	fin.close()	
	if iz: return X,Y,Z
	return X,Y
    
    
def getProcData(idx):
    #reads processed data to insert into spectrum.  Idx is index to file
    #input file first has header: name Foundmass Calcmass Int, then line of ### then mX mY
    mX=[]; mY=[]; labels=[]; isowin=[]; isowhere=[]
    nu=[];co=0
    aflag=False
    fin = open(ui.pfiles[idx],'r')
    for line in fin:
        if 'Name' in line: continue
        if '###' in line: aflag=True; continue
        line = line.replace('\n','')
        parts=line.split('\t')
        if aflag==False:
            nu.append([float(parts[1]),parts[0],float(parts[3]),co]);co+=1
        else:
            isowhere.append(readInListFromLine(parts[0]))
            isowin.append(readInListFromLine(parts[1]))
    nu.sort() #by x        
    where=[];win=[]
    for X,L,Y,c in nu:
        mX.append(X); mY.append(Y); labels.append(L)
        where.append(isowhere[c]);win.append(isowin[c])
    return mX,mY,labels,win,where

def makeShapeDic():
    #called once.  Makes dictionary of symbol:[shape,color] based on user input
    #for use with getShapes
    shapes={'square':'s','circle':'o','triangle':'^','diamond':'D','hexagon':'H','triangle-down':'v','star':'*','pentagon':'p','plus':'P','filled_X':'X','triangle_left':'<','triangle_right':'>'}
    for stuff in ui.defaults['Shapes'][1:]: #first line is header
        sh='h'
        if stuff[1] in shapes: sh=shapes[stuff[1]]
        ui.shapedic[stuff[0]]=[sh,stuff[2]] #symbol:[shape,color]
    

def getShapes(txt,size=10):
    #converts text to images with #'s inside.
    #returns list of info for annotation [x,y,marker,size,color,num,xn,yn]
    #x,y = where text supposed to begin in data coordinates. Need shapes in data coordinates!
    #ui.defaults['Shapes']=[[symbol,shape,color]]
    
    sdic=ui.shapedic
    if not size: size=10
    alist = convertStringToList_sp(txt) #['hex',2,'HexNac',5]

    temp=[]
    for k in range(0,len(alist),2): #when reversed goes #,word,#,word
        marker='H' #default is hexagon2
        color='blue' #default white
        if alist[k] in sdic: marker=sdic[alist[k]][0];color=sdic[alist[k]][1]
        try: anum = int(alist[k+1])
        except: print('Not finding a number in label '+str(alist[k+1])+' after '+str(alist[k])); anum=0
        temp.append([marker,color,anum])
    return wf.makeSugImage(temp,int(size))    
     
    
 
def useShapeLabels(txt,ax,ox,oy,x,y,agid,maxY,size,usemasses,fig):
    #makes and inserts images!
    img = getShapes(txt,size=size) #returns image
    imagebox = OffsetImage(img,zoom=1.0)
    xadj,yadj=calcYadj(ax,imagebox,x,y,maxY) #to keep labels form overlapping

    ap=None
    if yadj>0: ap={'arrowstyle':'-','color':'crimson'}
    ab = AnnotationBbox(imagebox,xy=(x,y),xybox=(x+xadj,y+yadj),frameon=False,pad=0,arrowprops=ap,box_alignment=(0.5,0))
    ab.set_gid(agid)
    ax.add_artist(ab)
    if usemasses=='yes':
        abbox=ab.get_window_extent(fig.canvas.get_renderer()) #returns dimensions
        xr,yr=wf.getDotsToDataRatio(ax)
        ax.annotate(str(round(x,1)),(x+xadj,y+yadj+abbox.height/yr),size='x-small', verticalalignment='bottom', horizontalalignment='center',picker=True,gid=agid)

    
def calcYadj(ax,ib,x,y,maxY,new=()):
    #attempting to move things...works but ugh
    #for some reason not getting Y axis properly scaled.  Had to send in maxY
    #using new to send in Xr,yr from on_ylim_change cause that info only in axis that changes.
    #Evolved so that this fuction used first time shapes inserted and _adjust function below is on_y_lim_changed.
    def checkHigh(ay,bbox,yd,y):
        #ay=axisy, y should be in pixels
        #makes sure inside axis, hopefully
        xd=0
        if y+yd>ay: #too tall
            xd = bbox.width/2 #in pixels
            yd = ay-bbox.height-y
        return xd,yd
        
    if not ax.artists: return 0,0  #first one, no overlap
    ay2=maxY    
    xr,yr = wf.getDotsToDataRatio(ax,yo=maxY) #returns dots:data
    if new: xr,yr=new;#print(x,y,xr,yr)
    y=y*yr;x=x*xr;ay2=ay2*yr
    bbox = ib.get_window_extent(ax.figure.canvas.get_renderer()) #in pixels
    yd=0;xd=0

    #check for overlap and adjust
    maxb=5
    if len(ax.artists)<maxb: maxb=len(ax.artists) #get limited peaks
    temp=ax.artists[-maxb:] #gets last 5 peaks
    used=[] #store ranges already used in case farther away label already there
    for r in range(0,maxb): #starts 5 peaks away
        ox,oy = temp[r].xybox #gets old xbox bottom
        ox=ox*xr; oy=oy*yr #to pixels
        boxh = bbox.height #box height of new box
        if x-ox==0: continue #same
        if abs(x-ox)<(bbox.width):#data to pixels..there is an overlap
            if new: print(x,ox,x-ox,bbox.width)
            nuy=y+yd #add adj
            oldy=oy
            
            obbox=temp[r].get_window_extent(ax.figure.canvas.get_renderer())
            if(abs(nuy-oldy))<=obbox.height: #ydif verses box height
                #y should be slightly above oy+oybbox
                yt=(oldy+obbox.height+2)-y #ytemp
                xd,ya = checkHigh(ay2,bbox,yt,y) #returns amts to adjust x and y by
                if ya==yt: yd=ya #did not get shorter
                 
                for ou,ouh,oux in used:
                    if abs(yd+y-ou)<=ouh: 
                        yt=ouh+2-y
                        xd,ya = checkHigh(ay2,bbox,yt,y) #see if new placement too tall.    
                        if ya==yt: yd=ya #did not get shorter
                
            else: used.append([oy,oy+obbox.height,ox]) #passed but if move could run into problems so save to check 

    return xd/xr,yd/yr #adjustment converted back to data?   

def calcYadj_update(ax,xr,yr,maxY):
    #called by on_ylim_change.  
    #updates peaks with overlaps or those that now don't have them
    def checkHigh(ay,bbox,yd,y):
        #ay=axisy, y should be in pixels
        #makes sure inside axis, hopefully
        xd=0
        if y+yd>ay: #too tall
            xd = bbox.width/2 #in pixels. how far to shift right
            yd = ay-bbox.height-y
        return xd,yd
    
    alist=[];
    for e,a in enumerate(ax.artists): #shapes
        f=''
        x,y=a.xy; 
        bx,by=a.xybox
        a.xybox=a.xy; alist.append([x,y,a,e,f]) #resets bboxes to starting positions!
        
        ##added in case masses added onto shapes
        if ui.usemasses=='yes':
            for f,c in enumerate(ax._children):
                if c.get_gid()==a.get_gid(): 
                    if isinstance(c,matplotlib.text.Annotation): #annotation
                        abox = a.get_window_extent(ax.figure.canvas.get_renderer())#get abox for shape
                        ax._children[f].set(x=x,y=y+abox.height/yr)
                        alist[-1][-1]=f #add counter to list
           
    alist.sort()
    #check for overlap and adjust
    maxY=maxY*yr
    for r in range(1,len(alist)): #loop through all peaks
        x,y,a,e,f = alist[r];y=y*yr;x=x*xr;
        bbox = a.get_window_extent(ax.figure.canvas.get_renderer()) #in pixels
        boxh = bbox.height #box height of new box
        yd=0;xd=0;used=[]
        rr=r-5
        if rr<0:rr=0;
        
        for q in range(rr,r-1): #loops through four previous peaks
            ox,oy,b,oe,of = alist[q] #gets old xbox bottom
            ox=ox*xr; oy=oy*yr #to pixels
            
            #if there's a difference, calc adjustment
            if (x-ox)<(bbox.width):#data to pixels..there is an overlap
                
                obbox=b.get_window_extent(ax.figure.canvas.get_renderer())#gets old bbox
                if(abs((y+yd)-oy))<=obbox.height: #ydif verses box height
                    #y should be slightly above oy+oybbox
                    yt=(oy+obbox.height+2)-y #ytemp
                    xd,ya = checkHigh(maxY,bbox,yt,y) #returns amts to adjust x and y by
                    if ya==yt: yd=ya #did not get shorter
                    for ou,ouh,oux in used: #previously saved pks.
                        if abs(yd+y-ou)<=ouh: 
                            yt=ouh+2-y
                            xd,ya = checkHigh(maxY,bbox,yt,y) #see if new placement too tall.    
                            if ya==yt: yd=ya #did not get shorter
                else: used.append([oy,oy+obbox.height,ox]) #passed but if move could run into problems so save to check 
       
        if xd!=0 or yd!=0: #adjustment needed due to overlap, so do it
            x,y = a.xy #reset to data points
            nux=x+xd/xr;nuy=y+yd/yr
            ax.artists[e].xybox = (nux,nuy)
            alist[r][0]=nux; alist[r][1]=nuy
            if f in ax._children: ax._children[f].set(x=nux,y=nuy+boxh/yr)
            
    
##########################################

root = Tk()
root.title("AssignMaldi")
root.geometry(f'+{25}+{25}') #so it always pops up in same place
ui=UI() 
wf.getScreenParameters(ui,root) #gets DPI,screenwidth and height for later
mw = mainWin(root)
root.mainloop()

