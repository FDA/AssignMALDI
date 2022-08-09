
#python 3.x
from tkinter import *
from tkinter import filedialog, messagebox,scrolledtext
from PIL import Image, ImageDraw, ImageFont, ImageColor
import matplotlib
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
from matplotlib.font_manager import findfont, FontProperties, FontManager #063022

import numpy as np
import ctypes
from common import tonum
import os,sys

class scrolledMsgWin():
    def __init__(self,root,alist,width=80):
        self.root=root
        f1 = Frame(root,bd=2)
        st=scrolledtext.ScrolledText(self.root,wrap=WORD,width=width,height=40,padx=10, pady=10)
        st.grid(column=0,row=0)
        st.insert(INSERT,alist)
        st.configure(state='disabled')
        
def showHelp(helpfile,window):
    #opens a text file with instructions for each window
    width=80 #for text and output window
    fin=open(helpfile,'r')
    astr=''; go=False
    for line in fin:
        if '#'+window in line: go=True; continue
        if '#' in line and go==True: break #reached end of section
        if go==True:
            while len(line)>width: #insert return and 3 spaces
                tw=width
                while line[:tw][-1]!=' ': tw-=1
                astr+=line[:tw]+'\n'
                line = '   '+line[tw:]
                
            astr+=line
        
    fin.close()
    
    t=Toplevel()
    t.wm_title("Help "+window)
    ew=scrolledMsgWin(t,astr,width)
		

class MyCheckButton(Checkbutton):
	def __init__(self,*args,**kwargs):
		self.var=kwargs.get('variable',IntVar())
		kwargs['variable']=self.var
		Checkbutton.__init__(self,*args,**kwargs)

	def is_checked(self):
		return self.var.get()

	def insert(self,where,value):
		#insert normally has a 'where' to start value - I'm trying to copy that function so this will work in a loop with other tkinter objects
		if value=='yes' or value=='on': self.select()
		if value=='off' or value=='no': self.deselect()
		
	def get(self):
		return self.var.get()

class MySortableList():
    def __init__(self,root, alist,r,c):
        self.alist = alist
        self.af = Frame(root,bd=2); self.af.grid(row=r,column=c)
        self.sv = StringVar(value=alist)
        self.abox = Listbox(self.af,listvariable=self.sv,height=len(alist))#height=# of lines!
        r=0;c=0
        self.abox.grid(row=0,column=0,rowspan=2)
        self.upb = makeButton(self,self.af,'^',lambda: self.move(-1),0,1,sticky='NS')
        self.dob = makeButton(self,self.af,'v',lambda: self.move(1),1,1,sticky='NS')
        
    def move(self,num):
        #num = -1 for up and 1 for down!
        self.idxs = self.abox.curselection()
        if not self.idxs:
            return
        for pos in self.idxs:
            text=self.abox.get(pos)
            self.abox.delete(pos)
            self.alist.pop(pos)
            if pos==len(self.alist) and num==1: pos=-1; #sets at beginning if at bottom and going down
            if pos==0 and num==-1: pos=len(self.alist)+1; #sets at end if at top and going up
            self.abox.insert(pos+num, text)
            self.alist.insert(pos+num, text)
            self.abox.selection_set(pos+num)
    def get(self):
        return self.alist

def makeSortableList(self,frame,alist,row,col,key):
    #self is calling window
    msl = MySortableList(frame,alist,row,col)
    self.items.append((msl,key)) 

def makeFileRow(self,frame,row,col,label,key,type='filein',id='',ewidth=30):
	#id = initial directory in the event that a value hasn't been saved yet.
	
	makeLabel(self,frame,label,row,col)
	makeEntry(self,frame,row,col+1,key=key,width=ewidth,type='str')
	eb=self.items[len(self.items)-1][0]
	makeButton(self,frame,"Browse",lambda: browse(self,eb,type,pnt=True,initialdir=id),row,col+2)

def loadValues(self):
	keys=[]	#for lists = stores keywords so can track when we've already pulled it up
	counters=[] #counters for lists
	for i,j in self.items:
		val=self.ui.returnValue(j)
		if val=='yes' or val=='no':
			try:
				if val=='yes': i.state='on'
				if val=='no': i.state='off'
			except:
				print ("Problem in loadValues",val)
			continue
		if isinstance(val,list)==True:
			co=0;adj=False
			for k,c in zip(keys,counters):
				if k==j:	#we've taken items from this list before
					if c<len(val):	#There might be more blanks than the list holds values for
						val=val[c]
						counters[co]=c+1
						adj=True
					else:
						val=''
						adj=True
				co=co+1
			if adj==False: #no prior match found
				keys.append(j)	#set new key
				counters.append(1) #How many we've found so far. This # is array # of next value!
				if len(val)>0:
					val=val[0]

		try:
			i.delete(0,END)
			i.insert(0,val)
		except:
			print ("problem 2 in loadValues",val)
		
def makeLabel(self,mast,text,row,col,exp=1,sticky=W):
	label = Label(mast,text=text)
	label.grid(row=row,column=col,columnspan=exp,sticky=sticky)

	
def makeCheckbox(self,mast,text,r,c,state='off',key='',special=''):
	#special is to save checkbutton pointers rather than stringVar pointers if special=='cbs'
	cv = StringVar()
	cb = Checkbutton(mast,text=text,variable=cv,onvalue='yes', offvalue='no')
	cb.grid(row=r,column=c,sticky=W)
	if state=='on': cb.select()
	if state=='off':cb.deselect()

	if special=='cbs':
		self.items.append((key,cb,cv))
	else:
		self.items.append((cv,key))  

def makeCheckBoxList(self,mast,alist,r,c,start='A'):
    #makes list of check boxes from a list.  Keys are A0,A1, etc.  #'s Will match iterators with incoming list
    #start is start of key
    
    for e,text in enumerate(alist):
        makeCheckbox(self,mast,text,r,c,state='off',key=start+str(e));r+=1
    return r    
       
def makeCheckButtonList(self,top,r,c,options,width=20,text='',key='',exp=1):
	#name=StringVar()
	mb=  Menubutton (top, text=text, relief=RAISED )
	mb.grid(row=r,column=c,sticky=W)
	mb.menu  =  Menu ( mb, tearoff = 0 )
	mb["menu"]  =  mb.menu
	
	for opt in options:
		iv=IntVar()
		mb.menu.add_checkbutton(label=opt,variable=iv)  
		self.items.append((iv,opt))
	return [mb,options]
    
def updateCheckButtonList(self,mblist,options):
	#mblist = [menubutton, oldoptions]
	mb,oldopts=mblist
	for oo in oldopts: mb.menu.delete(oo)
	#remove items from self.items.
	temp=[] 
	for stuff in self.items:
		copy=True
		for oo in oldopts: 
			if oo==stuff[0]: copy=False
		if copy==True: temp.append(stuff)
	self.items=temp[:]
	#add new stuff to menu
	#mb.menu  =  Menu ( mb, tearoff = 0 )
	for opt in options:
		iv=IntVar()
		mb.menu.add_checkbutton(label=opt,variable=iv)  
		self.items.append((iv,opt))
	return [mb,options]    
	
def makeCheckButton(self,mast,text,r,c,state='off',key='',special=''):
	#uses MyCheckButton so don't have to use variable anymore
	cv = StringVar()
	cb = MyCheckButton(mast,text=text,variable=cv,onvalue='yes', offvalue='no')
	cb.grid(row=r,column=c,sticky=W)
	if state=='on': cb.select()
	if state=='off':cb.deselect()
	self.items.append((cb,key))

def makeRadiobuttons(self,mast,MODES,setvar,row,col,key,dir='h'):	
	#dir=direction for radio buttons.  h=horizontal v=vertical
	#setvar is default value?
	#modes is [[label,key]]
	
	if not MODES: return []
	rblist=[]
	sv = StringVar()
	if setvar: sv.set(setvar) # initialize
	else: sv.set(MODES[0][1])
	
	co=col
	if dir=='v': #vertical
		co=row
	
	for text, mode in MODES:
		b = Radiobutton(mast, text=text,variable=sv, value=mode)
		if dir=='v':b.grid(row=co,column=col,sticky=W)
		if dir=='h':b.grid(row=row,column=co,sticky=W)
		
		if mode == sv.get(): b.select()
		else: b.deselect() ; #print('deselecting')
		
		rblist.append([b,text,mode])
		co=co+1

	self.items.append((sv,key))

	return rblist
	
def validateEntry(astr,type):
    #called from makeEntry
    #astr=%P which is value of the entry
    #action  = %d which is the type of action (1=insert,0=delete,-1 for rest)
    val = tonum(astr) #will convert to int, float, or string
    if type=='float': return isinstance(val,float)
    if type=='int': return isinstance(val,int)
    if type=='str': return isinstance(val,str)
    if type=='num':
        if isinstance(val,float)==True or isinstance(val,int)==True: return True
        
    return True
        
    
        
  
def makeEntry(self,mast,r,c,width=30,text="",key='',exp=1,type=''):
	#type can be 'float','int','str','num',or ''
	e1 = Entry(mast,bd=2,width=width,validate='key')
	e1.configure(validatecommand=(e1.register(validateEntry),'%P',type))
	e1.grid(row=r,column=c,sticky=W)
	e1.insert(0,text)

	self.items.append((e1,key))
	
def makeTextBox(self,mast,r,c,height=1,width=30,text='',key='',exp=1):
	e1 = Text(mast,bd=2,height=height,width=width)
	e1.grid(row=r,column=c,sticky=W)
	e1.insert(END,text)

	self.items.append((e1,key))
	
def makeButton(self,mast,text,command,r,c,sticky='W',columnspan=1):
	b1=Button(mast,text=text,command=command)
	b1.grid(row=r,column=c,sticky=sticky,padx=2,pady=2,columnspan=columnspan)

def makePicButton(self,mast,text,image,command,r,c,sticky='W'):
	
	b1=Button(mast,text=text,image=image,command=command)
	b1.grid(row=r,column=c,sticky=sticky,padx=2,pady=2)
	
def insertSep(self,mast,r,c,dir='h',exp=2):
	
	if dir=='h':
		separator = Frame(mast,height=2, bd=1, relief=SUNKEN,pady=5)
		separator.grid(row=r,column=c,columnspan=exp,sticky=W+E+S+N)
	if dir=='v':
		separator = Frame(mast,width=2, bd=1, relief=SUNKEN,pady=5)
		separator.grid(row=r,column=c,columnspan=exp,sticky=W+E+S+N)
		
def getKeyVal(items,key):	#for my wacky, backwards dictionary lists  [item,key]
	for i,k in items:
		if k==key:	return i
	
def browse(self,key,type='filein',pnt=False,initialdir=''):
	"""
		type options are filein, fileout, or dir.
		pnt = False if sending in key, if directly sending in a pointer in the key position = True
		eb = entry box associated with the browse button
	"""
	
	#print eb.get()
	import os
	eb=key
	filename=''
	if pnt==False:
		eb=getKeyVal(self.items,key)
	if pnt==True:	
		filename=eb.get()
		
	if filename=='' and initialdir!='':
		filename=os.path.join(initialdir,"lectinfile")
	if filename!='' and initialdir!='':
		filename = os.path.join(initialdir,filename)
		
	
	if type=='dir':
		try:
			dirin = filedialog.askdirectory(parent=self.root,initialdir=initialdir)
			if dirin!='':
				eb.delete(0,END)
				eb.insert(0,dirin)
		except:
			error("error: could not get directory name")
			return
	if type=='filein':
		#try:
			filein = filedialog.askopenfilename(parent=self.root,initialfile=filename)
			#print filein
			if filein!='':
				eb.delete(0,END)
				eb.insert(0,filein)		
		#except:
			#error(self,"Can't get filename")
	if type=='fileout':
		try:
			fileout = filedialog.asksaveasfilename(parent=self.root,initialfile=filename)

			if fileout!='':
				eb.delete(0,END)
				eb.insert(0,fileout)		
		except:
			error("Can't get filename")
			
def makeDropDownMenu(self,mast,OPTIONS,setvar,row,col,key,sticky='',color=False):
	def callback(name,index,mode):
		#name, index and mode are defaults apparently.
		value=v.get()
		b.config(bg=value)
	ddlist=[]
	v = StringVar()
	v.set(setvar) # initialize
	
	b = OptionMenu(*(mast,v) +tuple(OPTIONS))
	if sticky: b.grid(row=row,column=col,sticky=sticky)
	else: b.grid(row=row,column=col)
	if color==True:  #color the menuface with the setvar
		b.config(bg=setvar)
		v.trace_add('write',callback)
	self.items.append((v,key))

def makeZoombar(self,mast,r,c,label,start,end,orient,command,key):
    #orient='horizontal' or 'vertical'. start, end are numbers on bar
    makeLabel(self,mast,label,r,c); c+=1
    cv = DoubleVar()
    slider = Scale(mast,from_=start, to=end, variable=cv,orient=orient,command=command)
    slider.grid(row=r,column=c);
    self.items.append((cv,key))
    return
    
			

def error(message):
	try:	
		messagebox.showinfo("Error", message)
	except:
		return 0


def openFileDialog(self,type='in',initial=''):
	'''Get filename using filedialogs.  type= in, out, dir
		Make sure to enter initial as a file or directory as appropriate '''
	file=''
	try:
		if type=='in':
			file = filedialog.askopenfilename(parent=self.root,initialfile=initial)
		if type=='out':
			file = filedialog.asksaveasfilename(parent=self.root,initialfile=initial)
		if type=='dir':
			file = filedialog.askdirectory(parent=self.root,initialdir=initial)
		return file
	except:
		error("Can't get filename.")
		return

def getScreenParameters(ui,root):
    #added to make this work with Linux.  Gets DPI, width, and height when root called
    ui.dpi = root.winfo_fpixels('1i')
    ui.screenwidth = root.winfo_screenwidth()
    ui.screenheight = root.winfo_screenheight()
    
def getScreenSize():
    #only works with windows
    u32=ctypes.windll.user32
    return u32.GetSystemMetrics(0), u32.GetSystemMetrics(1)

def getDPI():
    #only works with windows
    u32=ctypes.windll.user32
    return u32.GetDpiForSystem()  #returns dots per inch.

def getTextDimensions_win(text, points, font):
    #only works for windows
    #input is ("text",size,"Font type")..("Hello world",12,"Times New Roman")
    #a pixel at 96dpi = 0.2645835mm or 0.75 points. 1 point=1/72 inches
    #returns tuple of xdim,ydim in points
    class SIZE(ctypes.Structure):
        _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

    hdc = ctypes.windll.user32.GetDC(0)
    hfont = ctypes.windll.gdi32.CreateFontA(points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
    hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)

    size = SIZE(0, 0)
    ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))

    ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
    ctypes.windll.gdi32.DeleteObject(hfont)
    ###optional method
    #u32=ctypes.windll.user32
    dpi=getDPI()#u32.GetDpiForSystem()  #returns dots per inch.
    width=len(text)*dpi*points*(1/72)*0.8
    if width>size.cx: return(width,size.cy)
    return (size.cx, size.cy)    
    
def getTextDimensions(text, points, font, dpi):
    #edited to work with everything
    #input is ("text",size,"Font type")..("Hello world",12,"Times New Roman")
    #a pixel at 96dpi = 0.2645835mm or 0.75 points. 1 point=1/72 inches
    #returns tuple of xdim,ydim in points
    try: return getTextDimensions_win(text,points,font)
    except: #guess.  Linux option
        #width was 0.75 of height, but 1.2 seems to work better.
        width=len(text)*points*1.2 #*dpi*points*(1/72)*0.8
        height = 1*points#*dpi*(1/72)
        return(width,height)
      
    
def getTextPlacement(labels,mX,mY,font,size,xr,yr):
    #For each label, look before and after. if can't adjust sideways, go up
    #xr,yr = ratio of dots to data. use to convert dots to data
    #not complete - still testing 02152022
    dpi = getDPI()
    fht = size*(1/72)*dpi*(1/xr) #converts font points to dots to data=font height..goes vertical so Xdim
    
    nuX=[];nuY=[];dr=fht;olly=0;lly=0
    for r in range(0,len(mX)):
        if r==len(mX)-1: nuX.append(mX[r]); nuY.append(mY[r]);break;  #saves last
        df = (mX[r+1]-mX[r])-fht #gap difference forward
        if r>0: 
            dr=(mX[r]-nuX[-1])-fht #gap difference reverse
            olly=lly
        test='Hex5HexNAc2'
        
        ntd=getTextDimensions(labels[r],size,font) #points
        lly=ntd[0]*(1/72)*dpi*(1/yr)*.66  #converts to length of label in datapoints..adjust by 2/3?
        if df>=0 and dr>=0: nuX.append(mX[r]); nuY.append(mY[r]);continue; #stay there. save
        rld1=nuY[-1]-(mY[r]+lly) #reverse label difference. bottom of rev-top of current
        rld2=mY[r]-(nuY[-1]+olly)#bottom of current - top of past
        fld1=mY[r+1]-(mY[r]+lly) #bottom of forward - top of current
        fld2=mY[r]-(mY[r+1]+lly) #bottom of current - top of forward #cheated-didn't calc correct length
        try:print ('472',labels[r],mY[r-1],mY[r],olly,lly)#rld1,rld2,fld1,fld2)
        except: pass
        if rld1>=0 or rld2>=0: nuX.append(mX[r]); nuY.append(mY[r]); print('here');continue
        if rld1>rld2: nuX.append(mX[r]); nuY[-1]-=rld1; nuY.append(mY[r]);print('backwards',nuY[-2]); continue
        if dr>0:
            if fld1>0 and fld2>0:nuX.append(mX[r]); nuY.append(mY[r]);continue;
            elif dr+df>0: nuX.append(mX[r]+df);nuY.append(mY[r]); continue;#df is negative. dr should be +. moves label backwards
        
        if df>0:
            if rld1>0:nuX.append(mX[r]); nuY.append(mY[r]);continue#reverse y no overlap so stay
            elif df+dr>0: nuX.append(mX[r]+dr);nuY.append(mY[r]); continue;#moves label forward
        
        #if all else fails, move the label up. add diff between top of prev and bott of current
        
        nuX.append(mX[r]); nuY.append(nuY[-1]+olly);#print('nuY',mY[r],nuY[-1],ntd,1/yr)
    return nuX,nuY
    
def getDotsToDataRatio(ax,yo=0):
    #need to know how many data points = one dot
    #get_xlim  returns current x-axis.
    x1,x2=ax.get_xlim(); y1,y2=ax.get_ylim()  #gets axis limits
    
    x1dc,y1dc=ax.transData.transform((x1,y1)) #converts to dots
    x2dc,y2dc=ax.transData.transform((x2,y2))
    
    if yo!=0: y2=yo  #sets biggest axis..to solve an issue with images
    xratio=(x2dc-x1dc)/(x2-x1) #dots/data
    yratio=(y2dc-y1dc)/(y2-y1)
    
    return xratio,yratio
    
#Added 06/01/2022
def makeSugImage(alist,size):
    #need to convert name to shape and then make and stick each shape together
    #alist = [['s','blue','12'],['o','green','5'],['X','purple','12']] #shape,color,text
    #size must be int
    white=(256,256,256,0) #transparent?
    ss = size#shapesize
    fnt = ImageFont.truetype("arial.ttf", int(ss*0.85), encoding="unic")
    
    img = Image.new(mode='RGBA',size=(ss,ss*len(alist)),color=white)
    draw = ImageDraw.Draw(img)
    x=0;y=0;co=0
    for sh in alist:
        y=(co*ss)
        fnt = ImageFont.truetype("arial.ttf", int(ss*0.85), encoding="unic")
        
        draw = makeSugShape(sh,x,y,ss,fnt,draw)
        co+=1
    
    return img  

def makeSugShape(shapel,x,y,ss,fnt,draw):
    #shapel = [shape,color,text],ss=shapesize
    b=(0,0,0) #black outline
    w = 1 #width of line
    s,c,t = shapel
    ao = 0
    if s=='s': draw.regular_polygon((x+ss/2,y+ss/2,ss/2),n_sides=4, rotation=0,outline=b,fill=c)#draw.rectangle(((x,y),(ss-1,y+ss-1)),outline=b,width=w,fill=c)
    elif s=='o': ss-=1;draw.ellipse(((x,y),(ss-1,y+ss-1)),outline=b,width=w,fill=c)
    elif s=='v': ss+=2;ao=ss/6;draw.regular_polygon((x+ss/2,y+ss/2-ao,ss/2),n_sides=3,rotation=180,outline=b,fill=c);
    elif s=='<': ss+=2;ao=ss/12;draw.regular_polygon((x+ss/2,y+ss/2-ao,ss/2),n_sides=3,rotation=-30,outline=b,fill=c);
    elif s=='>': ss+=2;ao=ss/12;draw.regular_polygon((x+ss/2,y+ss/2-ao,ss/2),n_sides=3,rotation=30,outline=b,fill=c);
    elif s=='D': draw.regular_polygon((x+ss/2,y+ss/2,ss/2),n_sides=4, rotation=45,outline=b,fill=c)
    elif s=='p': draw.regular_polygon((x+ss/2,y+ss/2,ss/2),n_sides=5, rotation=0,outline=b,fill=c)
    elif s=='H': draw.regular_polygon((x+ss/2,y+ss/2,ss/2),n_sides=6, rotation=0,outline=b,fill=c)
    else: 
        base=calcShape(ss,y,s);draw.polygon(base,outline=b,fill=c)
        if s=='^': ao=-ss/6
    tc=getContrastColor(c) #get text color
    
    draw.text((ss/2,y+ss/2-ao),str(t),font=fnt,fill=tc,anchor='mm')
    return draw    
    
def calcShape(ss,y,shape):
    #numbers in base based on ss=20
    base=[];val=20.0
    if shape=='*':
        base=[10.08,0,13.22,6.43,20,7.3,15.13,12.17,16.35,19.30,10.09,15.83,3.83,19.30,5.22,12.17,0,7.3,7.13,6.43]
    elif shape=='+': base = [16,0,56,0,56,16,72,16,72,56,56,56,56,72,16,72,16,56,0,56,0,16,16,16];val=72.0
    elif shape=='X': base = [29,0,41,12,51,1,80,29,69,40,81,52,52,81,40,69,29,80,1,51,12,41,0,29];val=81.0
    elif shape=='^': base = [36,0,72,65,0,65];val=71
    else: print('shape unknown '+s);return []
    nub=[];r=ss/val
    for b in base:
        nub.append(r*b)
    for r in range(1,len(nub),2): nub[r]+=y
    return nub
   
def getContrastColor(color):
    #color is (R,G,B,A)
    if isinstance(color,str): color = ImageColor.getrgb(color)
    R=color[0]; G=color[1]; B=color[2]; A=1
    if len(color)==4: A=color[3]
    
    ans = R*0.299+G*0.587+B*0.114+(1-A)*255
    if ans < 186: return (256,256,256)
    else: return (0,0,0)    
    
    
def getValues(items,ui):
	#filename is where previous values are stored.
	#items are pointers to stuff in window
	path=''
	if ui.lastdir:	path=getLastDir(ui.lastdir)
	else: path=getLastDir()  #try default filename
	nufile=os.path.join(path,ui.UIfile)
	try:
		fin=open(nufile,'r')
	except:
		#at least get last working directories if they exist
		print ("Could not get userinput from ui file.  No worries, not that important!\n",nufile)
		return
		
	uidict=vars(ui)
	for line in fin:
		line=line.strip('\n')
		parts=line.split('=')
			
		for i,it in enumerate(items): #counter,(value,key) - this would work better as a dict!
			key=it[1]
							
			if key==parts[0]: #key is from items
				try:	items[i][0].insert(0,parts[1])
				except: pass
				break
	fin.close()			
###previously under recall.py    
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
		
def saveDir(ui):
	#save so it's there next time.
	spath=os.path.dirname(os.path.realpath(sys.argv[0]))
	nufile = os.path.join(spath,ui.lastdir)
	fout = open(nufile,'w')
	fout.write(ui.inputdir)
	fout.close()
	
def saveValues(adic,afile):
	#adic = dictionary of values
	#afile = uifile
	#key = value
	fout = open(afile,'w')
	for k,v in adic.items():
		line = k +'='+str(v)+'\n'
		fout.write(line)
	fout.close()
	print ('values saved to', afile)