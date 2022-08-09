###AssignMALDI Installation Script
##Checks to make sure packages are installed
##Python must be installed first - that's easy - just download from python.org and follow instructions
import sys
import subprocess
try:
    subprocess.check_call([sys.executable,'AssignMALDI.py'])
except:
    print('SOME LIBRARIES MAY BE MISSING. INSTALLING...')
    subprocess.check_call([sys.executable, '-m','pip','install','--upgrade','pip'])
    for lib in ['scipy','matplotlib','Pillow']:
        subprocess.check_call([sys.executable, '-m','pip','install',lib])
    print('TRYING the PROGRAM AGAIN.')
    try:
        subprocess.check_call([sys.executable,'assignMALDI.py'])
    except:
        print('EXECUTION failed.  Send a Screenshot of the command prompt to the software developer.')
