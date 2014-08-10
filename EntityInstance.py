from collections import defaultdict
import string 

class Instance(object):
	def __init__(self, document, index, sentence, label, commonEntities, geniaWords):
		# print document
		self.attribs = self.getFeatures(index,sentence,commonEntities, geniaWords)
		self.word = sentence[index][4]
		self.gold = label
		self.document = document

	def getFeatures(self,index,sentence,commonEntities, geniaWords):
		''' Current list of features: 
		'''
		featureSet = defaultdict()
		currentWord = sentence[index]
		nextWord='__NULL__'
		previousWord='__NULL__'

		if index < len(sentence)-1:
			nextWord = sentence[index+1]
		if index > 0:
			previousWord = sentence[index-1]

		featureSet[(currentWord[5].lower(),'stemmedword')]=1
		featureSet[(currentWord[4].lower(),'lowerword')]=1
		featureSet[(currentWord[4],'word')]=1
		featureSet[(currentWord[7],'postag')]=1
		featureSet[(currentWord[6],'chunk')]=1
		featureSet[(1/len(currentWord[4]),'lengthOfWord')]=1
		featureSet[(currentWord[8],'ner')]=1
		featureSet[(index,'positionInSentence')]=1

		if currentWord[4].lower() in commonEntities:
			featureSet[(currentWord[4].lower(),'commonentities')]=1
		if currentWord[4].lower() in geniaWords:
			featureSet[(currentWord[4].lower(),'geniaentities')]=1

		if currentWord[4] == '-':
			featureSet[('ishyphen')]=1

		if currentWord[4] in string.punctuation: 
			featureSet[(currentWord[4],'punctuation')]=1

		if any(char.isdigit() for char in currentWord[4]):
			featureSet[('hasDigit')]=1

		if currentWord[4].isdigit():
			featureSet[('alldigit')]=1

		if currentWord[4].islower():
			featureSet[('lowercase')]=1
		elif currentWord[4].isupper():
			featureSet[('uppercase')]=1
		else:
			featureSet[('mixedcase')]=1

		if currentWord[4][0].isupper():
			featureSet[('capitalised')]=1

		if nextWord != '__NULL__':
			# print nextWord
			# featureSet[(nextWord[4],'nextword')]=1
			featureSet[(nextWord[5],'stemmednextword')]=1
			featureSet[(nextWord[8],'nextner')]=1
			featureSet[(nextWord[7],'nextpostag')]=1
			if nextWord[4].lower() in commonEntities:
				featureSet[(nextWord[4].lower(),'nextcommonentities')]=1
			if nextWord[4].lower() in geniaWords:
				featureSet[(nextWord[4].lower(),'nextGeniaWord')]=1
		else:
			# featureSet[(nextWord,'nextword')]=1
			featureSet[(nextWord,'nextner')]=1
			featureSet[(nextWord,'stemmednextword')]=1
			featureSet[(nextWord,'nextpostag')]=1

		if previousWord != '__NULL__':
			featureSet[(previousWord[4],'previousword')]=1
			featureSet[(previousWord[8],'previousner')]=1
			featureSet[(previousWord[5],'stemmedpreviousword')]=1
			featureSet[(previousWord[7],'previouspostag')]=1
			featureSet[(previousWord[1],'previousTag')]=1
		else:
			featureSet[(previousWord,'previousword')]=1
			featureSet[(previousWord,'previousner')]=1
			featureSet[(previousWord,'stemmedpreviousword')]=1
			featureSet[(previousWord,'previouspostag')]=1

		return featureSet
