#!/usr/bin/env python
import sys
import os
# Load the wrapper module, it's linked against FBInk, so the dynamic loader will take care of pulling in the actual FBInk library
from _fbink import ffi, lib as FBInk
import json
# Load Pillow
from PIL import Image, ImageDraw, ImageFont
# My own librairies (Kobo-Input-Python, Kobo-Python-OSKandUtils)
sys.path.append('../Kobo-Input-Python')
sys.path.append('../Kobo-Python-OSKandUtils')
import KIP
import osk

# Setup
rect_color = 200
rect_outline = 50
white = 255
black = 0
gray = 128
screenWidth = 1080
screenHeight = 1440
touchPath = "/dev/input/event1"
small_font = ImageFont.truetype("fonts/Merriweather-Regular.ttf", 26)
small_font_bold = ImageFont.truetype("fonts/Merriweather-Bold.ttf", 26)

appsAreas=None
toolsAreas=[]
current_page = 0

with open('launcher.json') as json_file:
	appsData = json.load(json_file)

def printLauncher(page=current_page):
	"""
	Prints a laucher page
	"""
	# Init image
	global appsAreas
	img = Image.new('L', (screenWidth+1,screenHeight+1), color=white)
	bg = ImageDraw.Draw(img, 'L')
	border=10
	big_border=30
	appsAreas=[] #reset
	## Building the menu
	# Main title
	rectWidth=int(5*screenWidth/6)
	titleRectHeight=int(screenHeight/10)
	rectHeight = int(screenHeight/15)
	rect_x = int(screenWidth/12)
	bg.rectangle([(rect_x,big_border),(rect_x+rectWidth,big_border+titleRectHeight)],fill=rect_color,outline=rect_outline)
	title_w,title_h = bg.textsize("Welcome to the PythonLauncher!", font=small_font_bold)
	bg.text((rect_x+int(0.5*rectWidth-0.5*title_w),big_border+int(0.5*titleRectHeight-0.5*title_h)),"Welcome to the PythonLauncher!",font=small_font_bold,fill=0)
	# Page change and reboot button (tools)
	#TODO
	# Apps buttons
	for i in range(min(9,len(appsData["apps"][page*9:(page+1)*9]))):
		app = appsData["apps"][page*9+i]
		app_x=rect_x+2*big_border
		app_y=(i+2)*rectHeight + int(i*rectHeight/3)
		app_w=rectWidth-4*big_border
		app_h=rectHeight
		appsAreas.append([app_x,app_y,app_x+app_w,app_y+app_h])
		bg.rectangle([(app_x,app_y),(app_x+app_w,app_y+app_h)],fill=white,outline=rect_outline)
		app_text_w,app_text_h = bg.textsize("Welcome to the PythonLauncher!", font=small_font)
		bg.text((app_x+int(0.5*rectWidth-0.5*app_text_w),app_y+int(0.5*rectHeight-0.5*app_text_h)),app["title"],font=small_font,fill=0)
	# Saving background and displaying it
	raw_data=img.tobytes("raw")
	raw_len = len(raw_data)
	FBInk.fbink_print_raw_data(fbfd, raw_data, screenWidth+1, screenHeight+1, raw_len, 0, 0, fbink_cfg)
	return True


fbink_cfg = ffi.new("FBInkConfig *")
fbfd = FBInk.fbink_open()
FBInk.fbink_init(fbfd, fbink_cfg)
#Clear screen
FBInk.fbink_cls(fbfd, fbink_cfg)
# CLEAN REFRESH
fbink_cfg.is_flashing = True
FBInk.fbink_refresh(fbfd, 0, 0, 0, 0, FBInk.HWD_PASSTHROUGH, fbink_cfg)
fbink_cfg.is_flashing = False

#Print the main image:
printLauncher(0)

# INITIALIZING TOUCH
touchPath = "/dev/input/event1"
t = KIP.inputObject(touchPath, screenWidth, screenHeight)

while True:
	try:
		(x, y, err) = t.getInput()
	except:
		continue
	if t.debounceAllow(x,y):
		global appsAreas
		print("Hey you clicked")
		for i in range(min(9,len(appsData["apps"][current_page*8:(current_page+1)*9]))):
			if KIP.coordsInArea(x,y,appsAreas[i]):
				#Closing touch file
				t.close()
				#Touch indicator
				fbink_cfg.is_flashing = True
				fbink_cfg.is_nightmode = True
				FBInk.fbink_refresh(fbfd, appsAreas[i][1]+11, appsAreas[i][0], appsAreas[i][2]-appsAreas[i][0], appsAreas[i][3]-appsAreas[i][1], FBInk.HWD_PASSTHROUGH, fbink_cfg)
				#Closing this FBInk session
				FBInk.fbink_close(fbfd)
				os.system(appsData["apps"][current_page+i]["command"])