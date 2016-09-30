import os
import signal
import subprocess

# The os.setsid() is passed in the argument preexec_fn so
# it's run after the fork() and before  exec() to run the shell.
pro = subprocess.Popen('python /home/pi/Documents/pixel_show/sleeper.py', stdout=subprocess.PIPE, 
                       shell=True, preexec_fn=os.setsid) 
print 'Call finished'
