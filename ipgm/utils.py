from __future__ import annotations
import random

def sumProductDict(a: dict, b: dict) -> float:
	allKeys = unionLists(list(a.keys()), list(b.keys()))
	c = 0
	for k in allKeys:
		if (k in a.keys()) and (k in b.keys()):
			c += float(a[k])*float(b[k])
	return c

def sumDict(d: dict) -> float:
	return sum(d.values())

def multiplyDict(d: dict, n: float) -> dict:
	return {k: v*n for k,v in d.items()}

#Multiplies all values in a 2d matrix by 0.01
def percentMatrix(m: list) -> list:
	for i in range(len(m)):
		m[i] = [x*0.01 for x in m[i]]
	return m

def mean(l: list) -> float:
	return sum(l)/len(l)

def mean(d: dict) -> float:
	return sum(d.values())/len(d)

#Unpacks divisions from otherCollectivites
def unpackDivisions(name: str, originalList: list, unpackingList: dict) -> list:
	#Recursive function, find name in unpackingList then call itself on each of its components until you find something on originalList

	if name in originalList: return [name]

	v = unpackingList[name]
	allDivs = [unpackDivisions(x, originalList, unpackingList) for x in v]
	allDivs = flattenList(allDivs)

	return allDivs

#Flattens a list, not recursive (only does 1 level), but apparently it's recursive (I just checked)
def flattenList(li: list) -> list:
	lf = []
	for l in li:
		if type(l) is list: lf += flattenList(l)
		else: lf.append(l)
	return lf

#Computes the union of elements of two lists
def unionLists(l1: list, l2: list) -> list:
	lf = list(l1)
	for e in list(l2):
		if e not in lf: lf.append(e)
	return lf

#Replaces every value with their share of the total list
def percentList(l: list) -> list:
	return [x/sum(l) for x in l]

#Replaces every value with their share of the total dict
def percentDict(d: dict) -> dict:
	return {k: v/sum(d.values()) for k,v in d.items()}

#Gets the args in a .vtm file
def getArgs(args: list, k: str) -> list:
	return [x[1:] for x in args if x[0] == k]

#Returns list with no doubles
def getSetList(*ll: list) -> list:
	lf = []
	for l in ll:
		for e in l:
			if e not in lf: lf.append(e)
	return lf

def formatPerc(n: float) -> str:
	n = str(round(float(n)*100, 1))
	if '.' not in n: n+='.0'
	return n+'%'

def averageList(l: list) -> float:
	return sum(l)/len(l)

def allEquals(l: list) -> bool:
	p = l[0]
	for i in l:
		if i != p: return False
	return True

def getProbsFromResDict(d: dict) -> tuple[str, float]:
	d = sortedDict(d, reverse=True)
	k1 = list(d.keys())[0]
	v1 = d[k1]
	return (k1, v1)

def getProbsFromResDictDiff(d: dict) -> tuple[str, float]:
	d = sortedDict(d, reverse=True)
	k1, k2 = list(d.keys())[0], list(d.keys())[1]
	m = d[k1] - d[k2]
	return (k1, m)

def getTopProbsFromDict(d: dict, f: float) -> list[str]:
	d = sortedDict(d, reverse=True)
	top = []
	summer = 0
	for k,v in d.items():
		if summer > f: break
		top.append(k)
		summer += v
	return top

def getRankInDict(d: dict, s: str):
	ls = [k for k in sorted(d.keys(), key=lambda x: d[x], reverse=True)]
	return ls.index(s)

def appendInDict(d: dict[str, list[any]], k: str, v: any):
	if k in d.keys(): d[k].append(v)
	else: d[k] = [v]

def addInDict(d: dict[str, int|float], k: str, v: int|float):
	if k in d.keys(): d[k] += v
	else: d[k] = v

def appendDictInDict(d: dict[str, dict], dk, k, v):
	if dk in d.keys(): d[dk][k] = v
	else: d[dk] = {k: v}

def unpackPairSets(s: set) -> list:
	l = []
	for k,v in s:
		l += [k]*int(v)
	return l

def getRandomAlphanumeric(k: int):
	return ''.join(random.choices(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'), k=k))

def toFloat(s: str) -> float:
	if s == '': return 0
	else: return float(s)

def toFloatOrStr(s: str) -> float|str:
	try: return toFloat(s)
	except: return s

def andMerge(l: list[str], doOxfordComma: bool = True) -> str:
	if len(l) == 2: return ' and '.join(l)
	return ', '.join(l[:-1]) + '{0} and '.format(',' if doOxfordComma else '') + l[-1]

def andMergeSorted(l: list[str], doOxfordComma: bool = True) -> str:
	l = sorted(l)
	return andMerge(l, doOxfordComma=doOxfordComma)

def cleanDict(d: dict) -> dict:
	return {k: v for k,v in d.items() if v != 0}

def sortedDict(d: dict, reverse: bool = False) -> dict:
    d = d = {k: v for k,v in sorted(d.items(), key=lambda item: item[1], reverse=reverse)}
    return d

def appendDict(d1: dict, d2: dict):
	for k,v in d2.items():
		d1[k] = v
	return d1

def allValuesEqual(l: list):
	for e in l[1:]:
		if e != l[0]: return False
	return True

def findLambda(l: list, a, f: function):
	for i in l:
		if f(i) == a:
			return i

def mergeSetLists(l1: list, l2: list) -> list:
	return l1 + [x for x in l2 if x not in l1]

def fold(l: list, f: function):
	if l == []: return None
	if len(l) == 1: return l[0]
	er = l[0]
	for e in l[1:]:
		er = f(er, e)
	return er

def isExpressed(c: str) -> bool:
	if len(c) == 0: return False;
	if c[0] == '@': return False;
	return True;

def hasNonExpressed(l: list) -> bool:
	for k in l:
		if not isExpressed(k): return True
	return False

def nonExpressed(d: dict[str, int|float]) -> int|float:
	return sum([v for k,v in d.items() if not isExpressed(k)])

def allNonExpressed(l: list) -> list[str]:
	return [x for x in l if not isExpressed(x)]

def isCandidate(c: str) -> bool:
	if len(c) == 0: return False;
	if c[0] == '@' or c[0] == '#': return False;
	return True;