#!/usr/bin/env python
import sys
import os
import threading
import json
from copy import deepcopy
# Load Pillow
from PIL import Image, ImageDraw, ImageFont
# My own librairies (Kobo-Input-Python, Kobo-Python-OSKandUtils)
sys.path.append('../Kobo-Input-Python')
sys.path.append('../Kobo-Python-OSKandUtils')
sys.path.append('../Python-Screen-Stack-Manager')
import pssm
import pssmObjectsLibrairy as POL
import pssm_kobo as pssm_device


# Setup
rect_color = 200
rect_outline = 50
white = 255
black = 0
gray = 128
light_gray = 230
Merri_regular = os.path.join("fonts", "Merriweather-Regular.ttf")
Merri_bold = os.path.join("fonts", "Merriweather-Bold.ttf")
small_font_size = int(pssm_device.screen_height/52)
title_font_size = int(pssm_device.screen_height/46)
small_font = ImageFont.truetype(Merri_regular, small_font_size)
small_font_bold = ImageFont.truetype(Merri_bold, small_font_size)
title_font = ImageFont.truetype(Merri_regular, title_font_size)
title_font_bold = ImageFont.truetype(Merri_bold, title_font_size)

current_page=0
apps_per_page = 8

border = 10
big_border = 3*border

with open('launcher.json') as json_file:
	appsData = json.load(json_file)


def printLauncher(page=0):
	global current_page
	current_page = page
	## Building the menu
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
		appObj.name = app["title"]  #Debug purpose
		appObj.data = app
		appObj.tags.add("page"+str(current_page))
		print("Creating object : " + str(appObj.name))
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
	previousObj.name = "previousPage"
	previousObj.onclickInside = previousPage
	previousObj.data = color == black
	previousObj.tags.add("page"+str(current_page))
	screen.addObj(previousObj)
	#Current and reboot
	pagebtn_x_temp += pagebtn_w + 2*big_border
	text="Page " + str(current_page) + '\r\n' + "Reboot"
	currentObj = POL.rectangle(pagebtn_x_temp,pagabtn_y,pagebtn_w,pagebtn_h,fill=white,outline=rect_outline)
	currentObj = POL.add_centeredText(currentObj,text,small_font,0)
	currentObj.name = "reboot"
	currentObj.onclickInside = reboot
	currentObj.tags.add("page"+str(current_page))
	screen.addObj(currentObj)
	#Next
	pagebtn_x_temp += pagebtn_w + 2*big_border
	text="Next"
	color = black if len(appsData["apps"][page*8:])>8 else light_gray
	nextObj = POL.rectangle(pagebtn_x_temp,pagabtn_y,pagebtn_w,pagebtn_h,fill=white,outline=rect_outline)
	nextObj = POL.add_centeredText(nextObj,text,small_font,color)
	nextObj.name = "nextPage"
	nextObj.onclickInside = nextPage
	nextObj.data = color == black
	nextObj.tags.add("page"+str(current_page))
	screen.addObj(nextObj)


def execCommand(objId,objData):
	print("ExecCommand executed")
	#Touch indicator
	obj=screen.findObjWithId(objId)
	screen.printInvertedObj(1,objId)
	if obj.data["killKPLOnClick"]:
		#Closing this FBInk session
		screen.device.closePrintHandler()
		#Closing touch file
		screen.device.closeInteractionHandler()
	#executing the actual command
	os.system(obj.data["command"])

def previousPage(objId,objData):
	global current_page
	# screen.printInvertedObj(1,obj)
	obj=screen.findObjWithId(objId)
	if obj.data:
		screen.removeAllWithTag("page"+str(current_page))
		printLauncher(current_page-1)


def nextPage(objId,objData):
	global current_page
	# screen.printInvertedObj(1,obj)
	obj=screen.findObjWithId(objId)
	if obj.data:
		screen.removeAllWithTag("page"+str(current_page))
		printLauncher(current_page+1)

def reboot(rebootObjId,objData):
	screen.printInvertedObj(1,rebootObjId)
	os.system("reboot")


def debug(objId,objData):
	for obj in screen.stack:
		print(obj, obj.name, obj.tags, obj.y, obj.id)


screen = pssm.ScreenStackManager(pssm_device,'Main Manager')
screenWidth = screen.width
screenHeight = screen.height
# screen.refresh()
screen.clear()
screen.createCanvas()
screen.refresh()
# Main title
rectWidth=int(5*screenWidth/6)
titleRectHeight=int(screenHeight/10)
rectHeight = int(screenHeight/(apps_per_page+7))
rect_x = int(screenWidth/12)
titleObj = POL.roundedRectangle(rect_x,big_border,rectWidth,titleRectHeight,fill=rect_color,outline=rect_outline)
titleObj = POL.add_centeredText(titleObj,"Welcome to the PythonLauncher!",title_font_bold)
titleObj.name = "TITLE"
titleObj.onclickInside=debug
screen.addObj(titleObj)
# Menu entries
printLauncher(page=0)

screen.startListenerThread()
#screen.listenForTouch() # No need for multithreading here
