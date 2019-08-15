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
import threading

# Setup
rect_color = 200
rect_outline = 50
white = 255
black = 0
gray = 128
light_gray = 230
touchPath = "/dev/input/event1"
small_font = ImageFont.truetype("fonts/Merriweather-Regular.ttf", 26)
small_font_bold = ImageFont.truetype("fonts/Merriweather-Bold.ttf", 26)
title_font = ImageFont.truetype("fonts/Merriweather-Regular.ttf", 30)
title_font_bold = ImageFont.truetype("fonts/Merriweather-Bold.ttf", 30)

appsAreas=[]
toolsAreas=[]
current_page = 0
previousBtn=[]
rebootBtn=[]
nextBtn=[]

with open('launcher.json') as json_file:
	appsData = json.load(json_file)

def printLauncher(page=current_page):
	"""
	Prints a laucher page
	"""
	# Init image
	global appsAreas
	global previousBtn
	global nextBtn
	global rebootBtn
	global current_page
	current_page = page
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
	title_w,title_h = bg.textsize("Welcome to the PythonLauncher!", font=title_font_bold)
	bg.text((rect_x+int(0.5*rectWidth-0.5*title_w),big_border+int(0.5*titleRectHeight-0.5*title_h)),"Welcome to the PythonLauncher!",font=title_font_bold,fill=0)
	# Apps buttons
	for i in range(min(8,len(appsData["apps"][page*8:(page+1)*8]))):
		app = appsData["apps"][page*8+i]
		app_x=rect_x+2*big_border
		app_y=(i+2)*rectHeight + int(i*rectHeight/3)
		app_w=rectWidth-4*big_border
		app_h=rectHeight
		appsAreas.append([app_x,app_y,app_x+app_w,app_y+app_h])
		bg.rectangle([(app_x,app_y),(app_x+app_w,app_y+app_h)],fill=white,outline=rect_outline)
		app_text_w,app_text_h = bg.textsize(app["title"], font=small_font)
		bg.text((app_x+int(0.5*app_w-0.5*app_text_w),app_y+int(0.5*app_h-0.5*app_text_h)),app["title"],font=small_font,fill=0)
	# Page change and reboot button (tools)
	pagebtn_x=rect_x+2*big_border
	pagabtn_y=(8+2)*rectHeight + int(8*rectHeight/3)
	pagebtn_w=int((rectWidth-8*big_border)/3)
	pagebtn_h=rectHeight
	#Previous
	pagebtn_x_temp=rect_x+2*big_border
	text="Previous"
	color = black if current_page>0 else light_gray
	previousBtn=[pagebtn_x_temp,pagabtn_y,pagebtn_x_temp+pagebtn_w,pagabtn_y+pagebtn_h,color!=light_gray]
	bg.rectangle([(previousBtn[0],previousBtn[1]),(previousBtn[2],previousBtn[3])],fill=white,outline=rect_outline)
	page_text_w,page_text_h = bg.textsize(text, font=small_font_bold)
	bg.text((previousBtn[0]+int(0.5*pagebtn_w-0.5*page_text_w),previousBtn[1]+int(0.5*pagebtn_h-0.5*page_text_h)),text,font=small_font_bold,fill=color)
	#Current and reboot
	pagebtn_x_temp += pagebtn_w + 2*big_border
	text="Page " + str(current_page) + '\r\n' + "Reboot"
	rebootBtn =[pagebtn_x_temp,pagabtn_y,pagebtn_x_temp+pagebtn_w,pagabtn_y+pagebtn_h]
	bg.rectangle([(rebootBtn[0],rebootBtn[1]),(rebootBtn[2],rebootBtn[3])],fill=white,outline=rect_outline)
	page_text_w,page_text_h = bg.textsize(text, font=small_font_bold)
	bg.text((rebootBtn[0]+int(0.5*pagebtn_w-0.5*page_text_w),rebootBtn[1]+int(0.5*pagebtn_h-0.5*page_text_h)),text,font=small_font_bold,fill=0)
	#Next
	pagebtn_x_temp += pagebtn_w + 2*big_border
	text="Next"
	color = black if len(appsData["apps"][page*8:])>8 else light_gray
	nextBtn=[pagebtn_x_temp,pagabtn_y,pagebtn_x_temp+pagebtn_w,pagabtn_y+pagebtn_h,color!=light_gray]
	bg.rectangle([(nextBtn[0],nextBtn[1]),(nextBtn[2],nextBtn[3])],fill=white,outline=rect_outline)
	page_text_w,page_text_h = bg.textsize(text, font=small_font_bold)
	bg.text((nextBtn[0]+int(0.5*pagebtn_w-0.5*page_text_w),nextBtn[1]+int(0.5*pagebtn_h-0.5*page_text_h)),text,font=small_font_bold,fill=color)
	# Saving background and displaying it
	raw_data=img.tobytes("raw")
	raw_len = len(raw_data)
	FBInk.fbink_print_raw_data(fbfd, raw_data, screenWidth+1, screenHeight+1, raw_len, 0, 0, fbink_cfg)
	return True

def invertArea(area,isBlack=False):
	if isBlack:
		fbink_cfg.is_nightmode = False
	else:
		fbink_cfg.is_nightmode = True
	fbink_cfg.is_flashing = True
	FBInk.fbink_refresh(fbfd, area[1]+11, area[0], area[2]-area[0], area[3]-area[1], FBInk.HWD_PASSTHROUGH, fbink_cfg)
	fbink_cfg.is_nightmode = False
	fbink_cfg.is_flashing = False
	return True



fbink_cfg = ffi.new("FBInkConfig *")
fbfd = FBInk.fbink_open()
FBInk.fbink_init(fbfd, fbink_cfg)
#Get screen infos
state = ffi.new("FBInkState *")
FBInk.fbink_get_state(fbink_cfg, state)
screenWidth=state.screen_width
screenHeight=state.screen_height
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
		global previousBtn
		global nextBtn
		global rebootBtn
		global current_page
		for i in range(min(8,len(appsData["apps"][current_page*8:(current_page+1)*8]))):
			if KIP.coordsInArea(x,y,appsAreas[i]):
				#Touch indicator
				invertArea(appsAreas[i])
				if appsData["apps"][current_page+i]["killKPLOnClick"]:
					#Closing this FBInk session
					FBInk.fbink_close(fbfd)
					#Closing touch file
					t.close()
				else:
					#Removing touch indicator after touch
					
					threading.Timer(0.1,invertArea,[appsAreas[i],True]).start()
				#executing the actual command
				os.system(appsData["apps"][current_page+i]["command"])
		if KIP.coordsInArea(x,y,previousBtn) and previousBtn[4]:
			printLauncher(current_page-1) 
		elif KIP.coordsInArea(x,y,nextBtn) and nextBtn[4]:
			printLauncher(current_page+1)
		elif KIP.coordsInArea(x,y,rebootBtn):
			#Closing touch file
			t.close()
			#Touch indicator
			invertArea(rebootBtn)
			#Closing this FBInk session
			FBInk.fbink_close(fbfd)
			os.system("reboot")