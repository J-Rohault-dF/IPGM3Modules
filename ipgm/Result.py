from ipgm.ResultPerc import *
from ipgm.utils import *
from ipgm.Candidacies import *
import copy

#Single line of results
Result = typing.TypeVar('Result')
class Result:
	results = {}

	def __init__(self, results: dict = {}):
		self.results = results

	@classmethod
	def fromLists(cls, candidates: list, results: list):
		return cls({k: toFloat(v) for k,v in zip(candidates, results) if v != ''})

	@classmethod
	def fromDict(cls, results: dict):
		return cls(results)
	
	@classmethod
	def createEmpty(cls):
		return cls({})

	def __repr__(self):
		return '<Results {0}>'.format(self.results)
	
	def getSumOfVotes(self, removeAbs: bool = True) -> float: #SHOULD REMOVE PARAMETER removeAbs
		if removeAbs:
			return sum([v for k,v in self.results.items() if isExpressed(k)])
		else:
			return sumDict(self.results)
	
	def getCandidates(self) -> list[str]:
		return list(self.results.keys())

	def getAdded(self, other: Result):
		newRes = copy.deepcopy(self)
		return newRes.add(other)

	def add(self, other: Result) -> Result:
		for k,v in other.results.items():
			if k not in self.results.keys():
				self.results[k] = 0
			self.results[k] += v
		return self
	
	def addDict(self, other: typing.Dict) -> Result:
		for k,v in other.items():
			if k not in self.results.keys():
				self.results[k] = 0
			self.results[k] += v
		return self

	def multiply(self, n: float) -> None:
		self.results = multiplyDict(self.results, n)

	def getMultiplied(self, n: float) -> Result:
		return Result(multiplyDict(self.results, n))
	
	def toPercentages(self, newName: str = '') -> ResultPerc:
		return ResultPerc.fromVotesDict(newName, self.results)
	
	@classmethod
	def fromPercentages(cls, percs: ResultPerc, totalVotes: float|None = None):
		if totalVotes is None:
			if percs.totalVotes is None:
				return cls({k: v for k,v in percs.results.items()})
			else:
				return cls({k: v*percs.totalVotes for k,v in percs.results.items()})
		else:
			return cls({k: v*totalVotes for k,v in percs.results.items()})
	
	def hasCandidate(self, cand: str) -> bool:
		return cand in self.getCandidates()
	
	def getWinner(self) -> str:
		s = ('', 0)
		for k,v in self.results.items():
			if v > s[1] and isCandidate(k):
				s = (k, v)
		return s[0]
	
	def getCleanResults(self) -> dict[str, int|float]:
		return {k: v for k,v in self.results.items() if isExpressed(k)}

	def renameCandidate(self, cand, renamedTo):
		if cand not in self.results.keys(): return self

		self.results[renamedTo] = self.results.pop(cand)
		return self
	
	def removeCandidate(self, cand: str):
		if cand not in self.results.keys(): return self
		
		del self.results[cand]
		return self.results

	def popCandidate(self, cand: str):
		if cand not in self.results.keys(): return 0
		return self.results.pop(cand)
	
	def selectCandidates(self, cands: list[str]):
		self.results = {k: v for k,v in self.results.items() if (k in cands)}
		return self.results

	def mergeCandidates(self, cand: str, mergedInto: str):
		if cand not in self.results.keys(): return self

		candVotes = self.results[cand]
		self.removeCandidate(cand)

		if mergedInto in self.results: self.results[mergedInto] += candVotes
		else: self.results[mergedInto] = candVotes
		return self
	
	def coalition(self, coalObj: dict[str, list[str]]) -> Result:
		"""
		Merges candidates in coalitions
		coalObj must be in the form {'coal1': ['list1', 'list2'],…}
		"""
		for coal in coalObj.keys():
			coalV = None

			for p in coalObj[coal]:

				if self.hasCandidate(p):
					if coalV is None: coalV = 0
					coalV += self.popCandidate(p)
			
			if coalV is not None:
				self.results[coal] = coalV
		
		return self




	
	def sortByVotes(self, doRandom: bool = False):
		import random
		ks = list(self.results.keys())
		if doRandom:
			random.shuffle(ks)
			self.results = {k: self.results[k] for k in ks}
		self.results = {k: v for k,v in sorted(self.results.items(), key=lambda x: x[1], reverse=True)}
	
	def getSubstractedDict(self, other: Result) -> dict[str, float]:
		candidates = getSetList(self.getCandidates(), other.getCandidates())
		return {k: (self.results[k] if k in self.results else 0)-(other.results[k] if k in other.results else 0) for k in candidates}



def averageResults(ress: list[Result]) -> Result:
	
	allCands = []
	for r in ress:
		allCands = unionLists(allCands, r.getCandidates())
	fRes = {}
	percentages = [r.toPercentages() for r in ress]

	for c in allCands:
		fRes[c] = averageList([p.get(c) if p.hasCandidate(c) else 0 for p in percentages])

	return Result.fromPercentages(ResultPerc('', fRes, averageList([x.totalVotes for x in percentages])))