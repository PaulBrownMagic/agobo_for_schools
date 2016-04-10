#agobo_for_schools
Updates to the agobo base class and an additional program that make Agobo robots from 4tronix more KS3 school friendly.

.on_start.py is a program I call at the end of .profile (add ./.on_start.py as the last line). I've included the .profile file here to show you how. .profile lives in the home directory. There are correct ways to make a program start on boot for the Pi, then there's this dirty little hack that actually works and starts the program when you want it started. 

.on_start.py makes the red line-follow led flash while the Pi is still obtaining an ip address, it'll flash between red and green if there's a licencing issue, if it can self-solve it, then it'll flash green while it starts vncserver :1, finally staying solid green for a while to let pupils know it is ready for connecting. In this way it is easier to debug why a pupil can't connect to the robot, if you're using vncviewer, if not, it still tells you when you're online. It will briefly do each flash even if it is not required so that your pupils get used to the routine and know what to look for.

refresh.sh will overwrite pupil's work for that session with copies of the same files stored in a .agobo hidden directory. Useful when doing back-to-back classes. You will need to mkdir .agobo and then copy the files in there.

agobo.py has been changed to make it more KS3 friendly. Pupils just call simple function names with a time, such as forward(1), which goes forward for 1 second. Other functions are: left, right, backward, stop. They follow a simple naming convention to make them easier to follow. agobo.py follows the Python PEP8 naming conventions whereever pupils may interface with it. It also provides a running() function, which is used with a while loop in the programs. running() makes it so that once pupils have started the program they have to press the mode button on the robot to actually start their code, this avoid accidentally driving it off a table. Pupils then press the mode button again to end their code.

motor.py, line_follow.py etc are all template programs for pupils to use. The .desktop files put icons onto the desktop that open up that program in IDLE with permissions to access the GPIO pins, they need to go into a Desktop directory. This way the pupils can run the programs in IDLE.
