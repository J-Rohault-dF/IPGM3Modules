from __future__ import annotations
import math
import xml.etree.ElementTree as etree
from ipgm.Candidacies import *
from ipgm.Div import *
from divsHandler import *
from mapdrawer.colors import *
from mapdrawer.seatsdrawer import *
from mapdrawer.keydrawer import *

def getWinningScore(d: dict[str, float]) -> tuple[str, float]:
	"""Returns the winning party and its score from a dict.
	
	Checks isCandidate() on the party, does not reweight the scores (outputs raw numbers as inputted).
	"""

	if d == None: return ('',0)

	#Get the highest-performing party, returns its name and score
	km = ''
	vm = 0
	for k,v in d.items():
		if isCandidate(k) and v > vm:
			vm = v
			km = k
		elif v == vm: km = ''
	return (km, vm)



def getWinningColorShade(color: Color, score: float) -> Color:
	"""Returns the shade of a color based on its score.
	
	The score has to be between 0 and 1, and can be multiplied beforehand.
	"""

	if score == 0: return Color('ffffff')
	return getShadeFromIndex(color, (math.floor(score*20)-2) )



def getWinningColorP(d: dict[str, float], candidaciesData: Candidacies) -> str:
	if d == None: return '000000'

	#k1, m = getProbsFromResDictDiff(d)
	k1, v1 = getProbsFromResDict(d)
	
	#if m > 0.9: indexInTable = 11
	#elif m > 0.6: indexInTable = 8
	#elif m > 0.3: indexInTable = 5
	if v1 > 0.95: indexInTable = 11 #Maybe change to 2/3, 7/8, and 39/40?
	elif v1 > 0.80: indexInTable = 8
	elif v1 > 0.65: indexInTable = 5
	else: return '000000'

	if candidaciesData.contains(k1):
		return getShadeFromIndex(candidaciesData.getShadeColor(k1), indexInTable).hex_l[1:]
	else:
		print('missing color for {0} ({1}%)'.format(k1, d[k1]))
		return '000000'





def mapColorerPercs(div: Div, candidaciesData: Candidacies, xmlR: etree.ElementTree, multiplier: float = 1):
	"""Colors a map based on the results.
	
	Args:
	div -- the master div of results
	candidaciesData -- stores data about the candidacies including colors
	xmlR -- the map xml object
	multiplier -- multiplier for the score shades (default 1)
	"""

	colorsUsed = {}

	for i in xmlR.getroot().find('{http://www.w3.org/2000/svg}g'):
		#If id is in the deps list, replace the fill
		if i.get('id') in [x.name for x in div.allSubDivs()]:
			
			winningParty, winningScore = getWinningScore(div.get(i.get('id')).result.toPercentages().removedAbs().results)
			
			try: #Gets the winning color, if not present print something and take a fallback color
				winningColor = candidaciesData.getShadeColor(winningParty)
			except:
				winningColor = Color('#ffffff')
				print('missing color for {0}'.format(winningParty))

			#Log color usage
			if winningParty not in colorsUsed: colorsUsed[winningParty] = [None] * 20
			colorsUsed[winningParty][math.floor(100*winningScore/5)] = winningColor

			winningShade = getWinningColorShade(winningColor, (winningScore*multiplier)).hex_l[1:]

			i.set('style', i.get('style').replace('000000', winningShade))
	print(colorsUsed)

def mapColorerProbs(probs: dict[str, dict[str, float]], candidaciesData: Candidacies, xmlR: etree.ElementTree):
	for i in xmlR.getroot().find('{http://www.w3.org/2000/svg}g'):
		#If id is in the deps list, replace the fill
		if i.get('id') in probs.keys():
			i.set('style', i.get('style').replace('000000', getWinningColorP(probs[i.get('id')], candidaciesData)))

def mapRinger(xmlL: etree.Element, xmlD: etree.Element, percs: dict[str, dict[str, float]], divsData: dict[str, dict[str, str|int]], outerRadius: float, innerRadius: float, candidaciesData: Candidacies):
	rings = etree.Element('{http://www.w3.org/2000/svg}g', attrib={'id': 'rings-{gid}'.format(gid=getRandomAlphanumeric(4))})

	for dk, dv in percs.items():
		if dk not in divsData.keys(): continue

		dd = divsData[dk]

		parties = list(dv.keys())
		scores = [(dv[x] if dv[x] > 0 else 0) for x in parties]
		colors = [candidaciesData.getCircleColor(x) for x in parties]

		rD, rR = drawPercRing((dd['cx'], dd['cy']), outerRadius, innerRadius, scores, colors)
		rBm, rB = drawPercRingBehind((dd['cx'], dd['cy']), innerRadius, outerRadius, (1/12))
		rR.insert(0, rB)

		rings.append(rR)
		xmlD.extend(rD)
		xmlD.extend(rBm)

	xmlL.append(rings)

def mapTexter(xmlL: etree.Element, texts: dict[str, str], divsData: dict[str, dict[str, str|int]], fontSize: float, font: str):
	group = etree.Element('{http://www.w3.org/2000/svg}g', attrib={'id': 'texts-{gid}'.format(gid=getRandomAlphanumeric(4))})

	for dk, dv in texts.items():
		if dk not in divsData.keys(): continue
		dd = divsData[dk]

		t = drawCenteredText(dv, dd['cx'], dd['cy'], fontSize, font, fillColor=Color('#ffffff'), strokeColor=Color('#000000'), strokeWidth=0.5, bold=True)
		group.append(t)
	
	xmlL.append(group)

def loadMap(mapSrc: str) -> etree.ElementTree:
	with open(mapSrc, 'r', encoding='utf8') as originalMap:
		return etree.parse(originalMap)



def exportMap(div: Div, mapSrc: str, mapTarget: str, candidaciesData: Candidacies, ringsData: None|dict[str, dict[str, str|int]] = None, outerRadius: float = 0, innerRadius: float = 0, scoreMultiplier: float = 1):
	"""Exports map based on all the data provided.

	Will draw rings if ringsData is provided (arguments needed are marked with *)
	
	Args:
	div -- the master Div of results
	mapSrc -- file path of the base map
	mapTarget -- file path of the target for the produced map
	candidaciesData -- Candidacies object
	doRings -- whether rings are drawn or not (default no)
	ringsData -- data for the rings (*)
	outerRadius -- outer radius for the rings (*)
	innerRadius -- inner radius for the rings (*)
	mapScaling -- scale multiplication of the map when automatically converting it to raster
	scoreMultiplier -- multiplication for the scores values
	"""

	mapTarget = 'exports/'+mapTarget
	xmlR = loadMap(mapSrc)
	
	mapColorerPercs(div, candidaciesData, xmlR, scoreMultiplier)

	if ringsData != None:
		mapRinger(xmlR.getroot().find('{http://www.w3.org/2000/svg}g'), xmlR.getroot().find('{http://www.w3.org/2000/svg}defs'), {x.name: x.result.toPercentages().removedAbs().results for x in div.allSubDivs()}, ringsData, outerRadius, innerRadius, candidaciesData)

	xmlR.write(mapTarget)



def exportMapProbs(probs: dict[str, dict[str, float]], mapSrc: str, mapTarget: str, allDivs: AllDivs, candidaciesData: Candidacies, doRings: bool = False, divsData: dict[str, dict[str, str|int]] = {}, outerRadius: float = 0, innerRadius: float = 0, doTexts: bool = False, texts: dict[str, str] = {}, fontSize: float = 8, fontUsed: str = ''):
	mapTarget = 'exports/'+mapTarget
	xmlR = loadMap(mapSrc)
	
	mapColorerProbs(probs, candidaciesData, xmlR)

	if doRings:
		mapRinger(xmlR.getroot().find('{http://www.w3.org/2000/svg}g'), xmlR.getroot().find('{http://www.w3.org/2000/svg}defs'), probs, divsData, outerRadius, innerRadius, candidaciesData)
	
	if doTexts:
		mapTexter(xmlR.getroot().find('{http://www.w3.org/2000/svg}g'), texts, divsData, fontSize, fontUsed)

	xmlR.write(mapTarget)



def exportSeatsMap(div: Div, seatsParties: dict[str, dict[str, int]], divsData: dict[str, dict[str, any]], mapSrc: str, mapTarget: str, allDivs: AllDivs, candidaciesData: Candidacies, seatsScale: float = 1, multiplier: float = 1):
	mapTarget = 'exports/'+mapTarget
	xmlR = loadMap(mapSrc)
	
	#Color in the map
	mapColorerPercs(div, candidaciesData, xmlR, multiplier)

	#Put the seats & color them - TODO: Put this into its own function
	group = etree.Element('{http://www.w3.org/2000/svg}g', attrib={'id': 'allSeats-{id}'.format(id=getRandomAlphanumeric(4))})
	for dn in seatsParties.keys():
		#If id is in the deps list, put the seats
		c = drawCircles(divsData[dn], dn.replace(' ','-'), 2.2777781*seatsScale, 0.569444*seatsScale, 5.52238*seatsScale)
		colorsSeats = [(candidaciesData.getCircleColor(k), v) for k,v in seatsParties[dn].items()]
		c = colorCircles(c, dn, colorsSeats)
		group.append(c)

	xmlR.getroot().find('{http://www.w3.org/2000/svg}g').append(group)
	
	xmlR.write(mapTarget)