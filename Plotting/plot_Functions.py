import pickle,pygame,sys,time,matplotlib,pylab,math
from button import *
from plot_Functions import *
from textrect import render_textrect
from pygame.locals import *
import matplotlib.backends.backend_agg as agg
import tkSimpleDialog

def load_data(infile,figure,axis,HEIGHT_IN_METERS):
	xCoord = []
	yCoord = []
	timing = []
	data = pickle.load(open(infile,'rb'))
	length = len(data)
	for i in range(length):
		temp = data[i]
		coord = temp[0]
		xCoord.append(coord[0])
		yCoord.append(coord[1])
		timing.append(temp[1])
	pxPerM = (max(yCoord)-min(yCoord))/HEIGHT_IN_METERS
	for i in range(len(yCoord)):
		yCoord[i] = round((max(yCoord)-yCoord[i]-min(yCoord))/pxPerM,3)
	figure = pylab.figure(figsize=[6, 6],dpi=75,facecolor="0.1")
	axis = figure.gca(axisbg="0.0")
	axis = style_axis(axis,HEIGHT_IN_METERS)
	axis.plot(timing,yCoord,'b',label='Data',linewidth=2)
	axis.legend()
	
	return xCoord, yCoord, timing, pxPerM, figure, axis
	
def create_graph(figure,plot_size):
	canvas = agg.FigureCanvasAgg(figure)
	canvas.draw()
	renderer = canvas.get_renderer()
	raw_data = renderer.tostring_rgb()
	graph = pygame.image.fromstring(raw_data, plot_size, "RGB")
	return graph
	
def fit_data_basic(yCoord,timing,HEIGHT_IN_METERS,figure,axis):
	gTmp = 7.0
	viTemp = -0.50
	g = 0; vi = 0; diff = 0
	fitGraph = []; idealGraph = []; yFit = []; temp = []
	
	while gTmp < 12.0:
		while viTemp < 0.50:
			for i in range(len(timing)):
				temp.append(HEIGHT_IN_METERS -(float(gTmp)*(timing[i]**2)/2) - viTemp*timing[i])
				diff += (yCoord[i]-temp[i])**2
			yFit.append(diff)
			if round(gTmp,1) == 9.8 and round(viTemp,2) == 0.00:
				idealGraph = temp
			if diff == min(yFit):
				fitGraph = []
				yFit = []
				yFit.append(diff)
				g = gTmp
				vi = viTemp
				fitGraph = temp
			temp = []
			diff = 0
			viTemp = round(viTemp+0.05,2)
		viTemp = -0.50
		gTmp += 0.01
	axis = figure.gca(axisbg="0.0")
	axis = style_axis(axis,HEIGHT_IN_METERS)
	axis.plot(timing,yCoord,'b',label='Data',linewidth=2)
	axis.plot(timing,fitGraph,'g',label='Fit',linewidth=2) 
	axis.plot(timing,idealGraph,'r',label='Ideal',linewidth=2)
	axis.legend()
	return g, vi, figure, axis
	
def fit_data_advanced(yCoord,timing,pxPerM,mass,csArea,airD,HEIGHT_IN_METERS,figure,axis):
	gTemp = 9.0
	viTemp = -0.50
	CdTemp = 0.3
	g = 0; vi = 0; diff = 0; Cd = 0
	fitGraph = []; idealGraph = []; yFit = []; temp = []
	idealTemp = 0
	
	while gTemp < 10.5:
		while viTemp < 0.50:
			while CdTemp < .8:
				for i in range(len(timing)):
					a = math.sqrt(2*mass*gTemp/(airD*csArea*CdTemp))
					b = math.sqrt(gTemp*airD*CdTemp*csArea/(2*mass))
					temp.append(HEIGHT_IN_METERS - (a*math.log(math.cosh(b*timing[i])))/b - viTemp*timing[i])
					diff += (yCoord[i]-temp[i])**2
				yFit.append(diff)
				if round(CdTemp,2) == 0.47 and round(gTemp,1) == 9.8 and round(viTemp,2) == 0.00:
					idealGraph = temp
					idealTemp = diff
				if diff == min(yFit):
					yFit = []
					yFit.append(diff)
					g = gTemp
					vi = viTemp
					fitGraph = temp
					Cd = CdTemp
				temp = []
				diff = 0
				CdTemp += .01
			CdTemp = 0.3
			viTemp += 0.05
		viTemp = -0.50
		gTemp += 0.01
	axis = figure.gca(axisbg="0.0")
	axis = style_axis(axis,HEIGHT_IN_METERS)
	axis.plot(timing,yCoord,'b',label='Data',linewidth=2)
	axis.plot(timing,fitGraph,'g',label='Fit',linewidth=2) 
	axis.plot(timing,idealGraph,'r',label='Ideal',linewidth=2)
	axis.legend()
	return round(g,2), round(vi,2), round(Cd,2), figure, axis

def style_axis(axis,HEIGHT_IN_METERS):
	axis.set_xlabel('Time(s)')
	axis.set_ylabel('Height(m)')
	axis.xaxis.label.set_color('white')
	axis.yaxis.label.set_color('white')
	axis.tick_params(axis='x', colors='white')
	axis.tick_params(axis='y', colors='white')
	pylab.ylim([0,math.ceil(HEIGHT_IN_METERS)])
	for i in axis.get_children():
		if isinstance(i, matplotlib.spines.Spine):
			i.set_color('#000000')
	return axis
	
def get_constants():
	mass = None
	csArea = None
	airD = None
	data = pickle.load(open("constants.p", "rb"))
	pNames = [str(i[0]) for i in data]
	preset = tkSimpleDialog.askstring("Load Preset", "Please type a preset name or new")
	if preset == 'new':
		mass = tkSimpleDialog.askstring("Mass", "Type value of the object's mass(kg)")
		if mass != None:
			csArea = tkSimpleDialog.askstring("Cross-Sectional Area", "Type value of the object's cross-sectional area(m^2)")
			if csArea != None:
				airD = tkSimpleDialog.askstring("Air Density", "Type value of the room's Air Density(kg/m^3)")
				if airD != None:
					try:
						mass = float(mass)
						csArea = float(csArea)
						airD = float(airD)
						name = tkSimpleDialog.askstring("Name New Preset", "What would you like to name the new preset?")
						if name == None:
							name = "Temp"
						if name in pNames:
							temp = pNames.index(name)
							data.pop(temp)
						data.append((name,[mass,csArea,airD]))
						pickle.dump(data, open("constants.p", "wb"))
					except ValueError:
						mass = None
						print "Values entered invalid"
	else:
		if preset in pNames:
			temp = data[pNames.index(preset)]
			temp2 = temp[1]
			mass = temp2[0]
			csArea = temp2[1]
			airD = temp2[2]
		else:
			print preset,"has not been defined as a preset"
	return mass, csArea, airD

def load_results(screen, fitResults, font, data_rect, g, vi, Cd, state):
	if state == 0:
		fitResults[0] = render_textrect("", font, data_rect, (255,0,0), (0,0,0), justification=1)
		screen.blit(fitResults[0],(15,210))
		screen.blit(fitResults[0],(15,240))
		screen.blit(fitResults[0],(15,270))
	elif state in [1,2]:
		fitResults[0] = render_textrect("g = "+str(g)+" m/s^2", font, data_rect, (255,0,0), (0,0,0), justification=1)
		fitResults[1] = render_textrect("vi = "+str(vi)+" m/s", font, data_rect, (255,0,0), (0,0,0), justification=1)
		fitResults[2] = render_textrect("", font, data_rect, (255,0,0), (0,0,0), justification=1)
		screen.blit(fitResults[0],(15,210))
		screen.blit(fitResults[1],(15,240))
		screen.blit(fitResults[2],(15,270))
	if state == 2:
		fitResults[2] = render_textrect("Cd = "+str(Cd), font, data_rect, (255,0,0), (0,0,0), justification=1)
		screen.blit(fitResults[2],(15,270))
	
	return screen, fitResults