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
sys.path.append('../Kobo-Screen-Stack-Manager')
import KIP
import pssm
import pssmObjectsLibrairy as POL
import osk
import threading

# Setup
rect_color = 200
rect_outline = 50
white = 255
black = 0
gray = 128
light_gray = 230
small_font = ImageFont.truetype("fonts/Merriweather-Regular.ttf", 26)
small_font_bold = ImageFont.truetype("fonts/Merriweather-Bold.ttf", 26)
title_font = ImageFont.truetype("fonts/Merriweather-Regular.ttf", 30)
title_font_bold = ImageFont.truetype("fonts/Merriweather-Bold.ttf", 30)

current_page=0
apps_per_page = 8

with open('launcher.json') as json_file:
	appsData = json.load(json_file)


def printLauncher(page=current_page):
	current_page = page
	border = 10
	big_border = 3*border
	## Building the menu
	# Main title
	rectWidth=int(5*screenWidth/6)
	titleRectHeight=int(screenHeight/10)
	rectHeight = int(screenHeight/(apps_per_page+7))
	rect_x = int(screenWidth/12)
	titleObj = POL.roundedRectangle(rect_x,big_border,rectWidth,titleRectHeight,fill=rect_color,outline=rect_outline)
	titleObj = POL.add_centeredText(titleObj,"Welcome to the PythonLauncher!",title_font_bold)
	screen.addObj(titleObj)
	# Apps buttons
	appObjs = []
	for i in range(min(apps_per_page,len(appsData["apps"][page*apps_per_page:(page+1)*apps_per_page]))):
		app = appsData["apps"][page*apps_per_page+i]
		app_x=rect_x+2*big_border
		app_y=(i+2)*rectHeight + int(i*rectHeight/3)
		app_w=rectWidth-4*big_border
		app_h=rectHeight
		appObj = POL.rectangle(app_x,app_y,app_w,app_h,fill=white,outline=rect_outline)
		appObj = POL.add_centeredText(appObj,app["title"],small_font)
		appObj.onclickInside = execCommand
		appObj.data = app
		screen.addObj(appObj)	
	# Page change and reboot button (tools)
	pagebtn_x=rect_x+2*big_border
	pagabtn_y=(apps_per_page+2)*rectHeight + int(apps_per_page*rectHeight/3)
	pagebtn_w=int((rectWidth-apps_per_page*big_border)/3)
	pagebtn_h=rectHeight
	#Previous
	pagebtn_x_temp=rect_x+2*big_border
	text="Previous"
	color = black if current_page>0 else light_gray
	previousObj = POL.rectangle(pagebtn_x_temp,pagabtn_y,pagebtn_w,pagebtn_h,fill=white,outline=rect_outline)
	previousObj = POL.add_centeredText(previousObj,text,small_font,color)
	previousObj.onclickInside = previousPage
	previousObj.data = color == black
	screen.addObj(previousObj)
	#Current and reboot
	pagebtn_x_temp += pagebtn_w + 2*big_border
	text="Page " + str(current_page) + '\r\n' + "Reboot"
	currentObj = POL.rectangle(pagebtn_x_temp,pagabtn_y,pagebtn_w,pagebtn_h,fill=white,outline=rect_outline)
	currentObj = POL.add_centeredText(currentObj,text,small_font,0)
	previousObj.onclickInside = reboot
	screen.addObj(currentObj)
	#Next
	pagebtn_x_temp += pagebtn_w + 2*big_border
	text="Next"
	color = black if len(appsData["apps"][page*8:])>8 else light_gray
	nextObj = POL.rectangle(pagebtn_x_temp,pagabtn_y,pagebtn_w,pagebtn_h,fill=white,outline=rect_outline)
	nextObj = POL.add_centeredText(nextObj,text,small_font,color)
	previousObj.onclickInside = nextPage
	previousObj.data = color == black
	screen.addObj(nextObj)


def execCommand(obj):
	print("ExecCommand executed")
	#Touch indicator
	obj.invert(1)
	if obj.data["killKPLOnClick"]:
		#Closing this FBInk session
		pssm.FBInk.fbink_close(pssm.fbfd)
		#Closing touch file
		touch.close()
	#executing the actual command
	os.system(obj.data["command"])

def previousPage(obj):
	obj.invert(1)
	if obj.data:
		printLauncher(current_page-1) 


def nextPage(obj):
	obj.invert(1)
	if obj.data:
		printLauncher(current_page+1) 

def reboot(obj):
	obj.invert(0)
	os.system("reboot")


screenWidth = pssm.screen_width
screenHeight = pssm.screen_height

# INITIALIZING TOUCH
touchPath = "/dev/input/event1"
touch = KIP.inputObject(touchPath, screenWidth, screenHeight)

screen = pssm.ScreenStackManager(touch,'Main Manager')
# screen.refresh()
screen.createCanvas()
printLauncher(page=0)

# screen.startListenerThread()
screen.listenForTouch() # No need for multithreading here