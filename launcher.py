#!/usr/bin/env python
import sys
import json
sys.path.append('../Python-Screen-Stack-Manager')
import platform
import os
if platform.machine() in ["x86","AMD64","i686","x86_64"]:
	device = "Emulator"
else:
	device = "Kobo"

import pssm


current_page = 0
apps_per_page=8
last_page_id= -1


def printPage(page=0):
	global current_page
	global last_page_id
	current_page = page
	number_of_items = min(apps_per_page,len(appsData["apps"][page*apps_per_page:(page+1)*apps_per_page]))
	list_items = []
	for i in range(number_of_items):
		app = appsData["apps"][page*apps_per_page+i]
		list_items.append({
			'text' : app["title"],
			'font_size' : 20,
			'onclickInside' : execCommand,
			'user_data' : app,
			'invertOnClick': True,
			'invertDuration': 0
		})
	# For technical reasons I prefer always to have 8 items in my list, so let's add some fake ones if there aren't 8 already
	for i in range(apps_per_page-number_of_items):
		list_items.append({
			'text' : "",
			'font_size' : 20,
			'invertOnClick': False,
			'outline_color':pssm.white
		})
	buttonList  = pssm.ButtonList(buttons=list_items, margins=[30,30,100,100], spacing=10)
	# Now for the other buttons
	button_welcome  = pssm.Button(text="Welcome to the PythonLauncher!",radius=20, background_color = 220, font=pssm.Merri_bold, font_size = 35, wrap_textOverflow = False)
	reboot_text     = "Page " + str(current_page) + '\r\n' + "Reboot"
	is_previousPage = current_page>0
	is_nextPage 	= len(appsData["apps"][page*8:])>8
	previous_color  = pssm.black if is_previousPage else pssm.light_gray
	next_color      = pssm.black if is_nextPage else pssm.light_gray
	button_reboot   = pssm.Button(reboot_text, onclickInside = reboot, invertOnClick	= True, invertDuration = 0)
	button_previous = pssm.Button("Previous",  onclickInside = previousPage, text_color = previous_color, user_data = is_previousPage, invertOnClick= True, invertDuration = 0)
	button_next     = pssm.Button("Next",      onclickInside = nextPage,     text_color = next_color    , user_data = is_nextPage, invertOnClick	= True, invertDuration = 0)
	menu = [
		[30                                                                                                             ],
		[130,            (None,80),                       (button_welcome,"?"),                    (None,80)            ],
		["?",                                               (buttonList,"?")                                            ],
		[100,(None,30), (button_previous,"?"), (None,30), (button_reboot,"?"), (None,30), (button_next,"?"), (None,30)  ],
		[30                                                                                                             ]
	]
	menuLayout = pssm.Layout(menu,screen.area)
	last_page_id = menuLayout.id
	screen.addElt(menuLayout)


def execCommand(elt,coords):
	print("ExecCommand executed")
	if elt.user_data["killKPLOnClick"]:
		#Closing this FBInk session
		screen.device.closePrintHandler()
		#Closing touch file
		screen.device.closeInteractionHandler()
	#executing the actual command
	os.system(elt.user_data["command"])

def previousPage(elt,coords):
	global current_page
	global last_page_id
	if elt.user_data:
		screen.removeElt(last_page_id,skipPrint=True)
		printPage(current_page-1)

def nextPage(elt,coords):
	global current_page
	global last_page_id
	if elt.user_data:
		screen.removeElt(last_page_id,skipPrint=True)
		printPage(current_page+1)

def reboot(elt,coords):
	os.system("reboot")


################################################################################
#Declare the Screen Stack Manager
screen = pssm.ScreenStackManager(device,'Main')
#Start Touch listener, as a separate thread
screen.startListenerThread(grabInput=True)
#Clear and refresh the screen
screen.clear()
screen.refresh()

with open('launcher.json') as json_file:
	appsData = json.load(json_file)

printPage(page=0)
