AssignMALDI README file 22-July-2022

PREREQUISITES
 - Latest version of Python 3.x
 - python libraries: scipy and matplotlib

EASY INSTALL
1. Install latest Python 3.x version from Python.org in your C: drive (i.e. C:\\Python310. Using the default directory the Python installer suggests has caused issues)
2. Download and unzip the zip file
3. Click Run.py (this will automatically check for and install needed libraries)

MANUAL INSTALL
**Libraries can be installed using the pip install command.**
1. Open a command prompt. You can find this by entering 'command' in the windows search bar.
2. At the cursor type 
   pip install scipy

if that doesn't work, try calling pip using the python command first
   python -m pip install scipy

if that doesn't work you may need to use the full python path (your path may differ)
   C:\\python3x\\python -m pip install scipy

MANUAL EXECUTION
Double-click on AssignMALDI.py
>>IF the above doesn't work, it's likely the python installation isn't set up right.  Not a problem!
>>First test your python installation.
Open a command prompt. You can find this by entering command in the windows search bar.  On my computer it's a black window.
Type 'python' at the prompt in your command window.  
 (i) if you get a message stating the python version and then >>>, type exit() and continue on to 3b.
 (ii) if (i) doesn't happen, find your python executable.  It might be under c:\\python3x\\.  Try executing python by typing in the full path.
 (iii) if typing in the full path doesn't work, you may need to reinstall python.  Note, if there are spaces in your path, you have to put quotes around it.
3b. In the command window, 'cd' to the assignMALDI directory. 
 - 'cd' stands for change directory
 - you can go back a directory by typing cd .. and hitting enter
 - you can go forward a directory by typing cd dirofinterest and hitting enter
 - if you need to go to a different drive type the letter of that drive and a colon (ie. g:) and hit enter.
   After that you can cd forward to the assignMALDI directory
4b. type 'python' or the full path to your python executable (whatever worked above) and then 'AssignMALDI.py'
#########################################################################################

TEST RUN
1. In the main assignMALDI window, click the 'Make Glycan Database' button under ***INPUT***
2. in the dbMaker window that appears 
 under ***OPTIONS*** select
 - Preparation: Enzyme-Released
 - Modificaton: Permethylation 
 - Adduct: Na, Number: 1
 under ***GLYCAN INPUT***
 - Multiple entry file: Browse to and select 'shorthandlib.txt'
 - New Database file: Browse to any folder, enter and save a new file such as 'library_NaPM.txt' 
 - click 'Write Database'
 - close dbMaker window
3. Back under the AssignMaldi window, 
 under ***INPUT***
 - Browse to and select the 'RNaseB' directory in the AssignMALDI folder
 - Browse to and select the Glycan database file you made above
 under ***PROCESSING OPTIONS***
 - set z-score to 20 (this is high because the noise in the test spectra is very low)
 - DO NOT check the Check z-score button unless you want to see which peaks are selected prior to assignment.
 - set the error to 0.2
 - set 'Assignment must be found in ...' to 2
 under ***OUTPUT OPTIONS***
 - set limit m/z axis to 1000 to 2500.  Check the box to the left of 'Limit M/Z axis to:'
 - check 'use shapes'
 - under 'what assignments should be in output file', select 'Only Assigned'
 - press 'Assign'

RESULTS
 - The spectra window will pop up with the assigned spectra.  
 - MS-sum.txt will appear in the RNaseB directory with the averaged assignments
 - Not all the assignments are correct - You can clean up the spectra with the pick peak button and save it.  This will rewrite the MS-sum file.
TROUBLESHOOTING
 - If you get a window that shows only a spectra with red dots, uncheck the 'Check z-score' button in the main window and hit the 'Assign' button again.

FILE DESCRIPTIONS
AssignMALDI.py - runs program.  Contains code for GUI
AssignMALDI_fun.py - core AssignMALDI functions
common.py - basic functions shared by many programs
dbmaker.py - contains code for database maker.  Can be run standalone by calling testRun()
isotope_ed.py - code to calculate isotopic patterns
pickpk_lmp.py - code for peak picking
windowfeatures.py - basic GUI code shared by many programs

pkpkicon.png, savedata.png, zoomin.png, zoomout.png - icons for GUI

AssignMALDI_help.txt - detailed description of AssignMALDI.  Accessible from the program's help buttons
assignMaldi_defaults.txt - stores default values for drop-down menus in AssignMALDI. Can be edited by the user from the window
dbmaker_defaults.txt - stores default values for drop-down menus in the database maker. Can be edited by the user from the window
shorthandlib.txt - Example shorthandlibrary.  Good starting point for first-time use.

TROUBLESHOOTING
ERROR: NotFoundError: No module named 'PIL'
FIX:
>pip uninstall PIL
>python -m pip install --upgrade pip
>python -m pip install --upgrade Pillow

ERROR: New selected peaks don't have an area in the MSsum.txt file
FIX: Make sure your z-score is low enough that all the peaks in the isotopic window are being picked by using 'check z-score'.
     The peaks must be picked even if they aren't automatically assigned for the area to be calculated.

ERROR: Nothing happens to the open spectra when I choose options in the main window.
FIX: Options are only applied when a spectra window first opens.  If you want to 'show masses' for example or alter what 
     assignments should be in the output files, make your selections in the main window, then select 'Open Previous'.
     This will apply all your edits and your new options to the new window.  To rewrite the output files, save the 
     assignment changes ('save') in the new spectra window.  Multiple spectra windows can be open at once.

ERROR: Program locks and doesn't display spectra window.
FIX: It's most likely information overload.  
     First, make sure the z-score chosen is low enough to get all peaks but not so low you get all the noise peaks
     Second, turn off 'use shapes' and 'show masses'.  If it works with labels only, you can always add these after you 
       clean up the spectra and save it.  Just choose 'Open Previous' with 'use shapes' and/or 'use masses' selected.
