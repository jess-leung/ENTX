from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression 
from sklearn import metrics  
from sklearn.feature_extraction import DictVectorizer
from math import ceil,log
import numpy as np 
from collections import defaultdict
import random
import matplotlib.pyplot as plt
import math

class ActiveLearner:
	"""This class conducts active learning, rather than passive learning. 
	""" 
	def __init__(self,trainingInstances,testInstances,learnerType,samplingMeasure,noisePercentage,numberEachIteration):
		"""Constructor
			trainingInstances is a zipped list with trainingInstances[0] = feature instances and trainingInstances[1] = true labels of training instances 
			testInstances is a zipped list with testInstances[0] = feature instances and testInstances[1] = true labels of test instances 
			learnerType is a string containing the learner type e.g. SVM / LogisticRegression
			samplingMeasure is a string containing the uncertainty measure used e.g. hyperplane 
			noisePercentage is a float containing percentage noise in the whole labelling process e.g. 0.10 for 10% 
			numberEachIteration is an integer containing number of added instances in each round"""
		self.__learnerType = learnerType 
		self.__trainingInstances = trainingInstances
		self.__testInstances = [u[0] for u in testInstances] 
		self.__testTrueLabels = [u[1] for u in testInstances]
		self.__uncertaintyMeasure = samplingMeasure
		self.__prfAllIntervals = defaultdict(list)
		self.__numberEachIteration = numberEachIteration
		self.__noise = noisePercentage
		self.__uncertaintyHistory=[]

	def gettingClassifier(self):
		cutOffPoint = 2000
		numberOfInstances=0
		if self.__noise != 0:
			numberOfInstances = int(math.floor(len(self.__trainingInstances)*self.__noise))

		# Split training data into two groups - labelled and unlabelled
		labeled_training_feats = [u[0] for u in self.__trainingInstances[:cutOffPoint]]
		labeled_training_labels = [u[1] for u in self.__trainingInstances[:cutOffPoint]]
		unlabeled_training = self.__trainingInstances[cutOffPoint:]
		unlabeled_training_feats = [u[0] for u in unlabeled_training]
		unlabeled_training_labels = [u[1] for u in unlabeled_training]
		noisyInstances = random.sample(unlabeled_training_feats, numberOfInstances)

		# Classifier
		clf = None 
		# Obtain classifier using currently labeled training dataset 
		if self.__learnerType=='SVM':
			clf = LinearSVC()
		else:
			clf = LogisticRegression()

		# Dictionary Vectorizer 
		vec = DictVectorizer()

		# Fit and transform the labelled training set, labels and transform the unlabeled group and labels into np array 
		labeled_training_feat_fitted = vec.fit_transform(labeled_training_feats)
		labeled_training_labels_np = np.array(labeled_training_labels)
	
		# Fit the labelled data to the classifier 
		clf.fit(labeled_training_feat_fitted,labeled_training_labels)

		basePrediction = self.classifyInstances(clf,self.__testInstances,vec)
		self.microPRFAtEachInterval(self.__testTrueLabels,basePrediction)
		print len(labeled_training_feats)
		# While there are still instances in the unlabelled training set 
		while len(unlabeled_training_feats)>0: 	

			# Get most informative instances (i.e. closest to the hyperplane)
			mostInformativeInstances = self.getMostInformativeInstances(clf,unlabeled_training_feats,vec)

			for item in mostInformativeInstances:
				labeled_training_feats.append(item[0])
				index = unlabeled_training_feats.index(item[0])
				thisLabel = unlabeled_training_labels[index]
				# self.__uncertaintyHistory.append(item[1])
				if self.__noise != 0: 
					if item in noisyInstances:
						print 'noisy instance'
						thisLabel = random.choice(['None','Protein-Component','Subunit-Complex'])
				labeled_training_labels.append(thisLabel)
				unlabeled_training_feats.remove(item[0])
				unlabeled_training_labels.pop(index)
			if self.__learnerType=='SVM':
				clf = LinearSVC() 
			else:
				clf = LogisticRegression()
			# Retrain the classifier 
			labeled_training_feat_fitted = vec.fit_transform(labeled_training_feats)
			labeled_training_labels_np = np.array(labeled_training_labels)
			print len(labeled_training_feats)
			clf.fit(labeled_training_feat_fitted,labeled_training_labels_np)
			predicted = self.classifyInstances(clf,self.__testInstances,vec)
			self.microPRFAtEachInterval(self.__testTrueLabels,predicted)
		"""Plotting the uncertainties """
		# # print len(self.__uncertaintyHistory)
		# plt.title('Comparing uncertainties')
		# xVals = range(0,len(self.__uncertaintyHistory))
		# plt.ylabel('Confidence')
		# plt.xlabel('Number of Training Instances')
		# plt.plot(xVals,self.__uncertaintyHistory,'r--')
		# plt.show()
		return clf

	def determineUncertainty(self,row):
		uncertainties = [] 

		if self.__uncertaintyMeasure=="entropy":
			# H(x) = - sumof(p(x_i)*log2(p(x_i)))
			entropyValues = [-1*val*log(val,2) for val in row]
			entropy = sum(entropyValues)
			uncertainties.append(entropy)
		elif self.__uncertaintyMeasure=="smallestMargin":
			thisRowSorted = sorted(row)
			smallestMargin = thisRowSorted[len(thisRowSorted)-1] - thisRowSorted[len(thisRowSorted)-2] 
			uncertainties.append(smallestMargin)
		elif self.__uncertaintyMeasure=="leastConfident":
			thisRowSorted = sorted(row)
			leastConfident = 1 - thisRowSorted[len(thisRowSorted)-1]
			uncertainties.append(leastConfident)
		elif self.__uncertaintyMeasure=="hyperplane":
			negInstances = [] 
			posInstances = [] 
			# print row
			for item in row: 
				if item<0:
					negInstances.append(item)
				else:
					posInstances.append(item)
			minOfPositive=0
			maxOfNegative=0
			if len(posInstances)>0:
				minOfPositive = min(posInstances)
			if len(negInstances)>0:
				maxOfNegative = max(negInstances)
			separationMargin = minOfPositive-maxOfNegative
			uncertainties.append(separationMargin)
		return uncertainties

	def getMostInformativeInstances(self,classifier,unlabelledSet,vec):
		sorted_collated=[]
		if self.__uncertaintyMeasure=="randomSampling":
			# random sampling 
			if len(unlabelledSet)>=250:
				return random.sample(zip(unlabelledSet,unlabelledSet),self.__numberEachIteration)
			else:
				return zip(unlabelledSet,unlabelledSet)
		if self.__learnerType=="LogisticRegression":
			unlabelledSet_fitted = vec.transform(unlabelledSet)
			probs = classifier.predict_proba(unlabelledSet_fitted) 
			uncertainties = np.apply_along_axis( self.determineUncertainty, axis=1, arr=probs )

			collated = zip(unlabelledSet,uncertainties)
			if self.__uncertaintyMeasure=="entropy" or self.__uncertaintyMeasure=="leastConfident":
				sorted_collated = sorted(collated, key=lambda tup: tup[1], reverse=True)
			elif self.__uncertaintyMeasure=="smallestMargin":
				sorted_collated = sorted(collated, key=lambda tup: tup[1])
			return sorted_collated[:self.__numberEachIteration]
		elif self.__uncertaintyMeasure=="hyperplane":
			unlabelledSet_fitted = vec.transform(unlabelledSet)
			distances = classifier.decision_function(unlabelledSet_fitted) 
			uncertainties = np.apply_along_axis( self.determineUncertainty, axis=1, arr=distances )
			collated = zip(unlabelledSet,uncertainties)
			sorted_collated = sorted(collated, key=lambda tup: tup[1])
			return sorted_collated[:self.__numberEachIteration]

	def classifyInstances(self,classifier,x,vec):
		"""This method classifies x, given some classifier 
		"""
		x_transformed = vec.transform(x)
		# x_decisions = classifier.predict_proba(x_transformed)
		# uncertainties = np.apply_along_axis( self.determineUncertainty, axis=1, arr=x_decisions)
		# print np.mean(uncertainties)
		# self.__uncertaintyHistory.append(np.mean(uncertainties))
		prediction = classifier.predict(x_transformed)
		return prediction 

	def __getTrueAndFalsePosNegs(self,truelabels,predicted):
		zippedResults = zip(truelabels,predicted)
		counter = defaultdict(lambda:defaultdict(int))
		for result in zippedResults:
			if result[0]==result[1]:
				counter[result[0]]['TP']+=1
			elif result[0]!= result[1]:
				counter[result[0]]['FN']+=1 
				counter[result[1]]['FP']+=1
		return counter 

	def microPRFAtEachInterval(self,truelabels,predicted):
		thisIntervalResults = self.__getTrueAndFalsePosNegs(truelabels,predicted)
		thisMicroRecall = float(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP'])/(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['FN']+thisIntervalResults['Protein-Component']['FN'])
		thisMicroPrecision = float(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP'])/(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['FP']+thisIntervalResults['Protein-Component']['FP'])
		thisFScore = 2*thisMicroPrecision*thisMicroRecall/(thisMicroPrecision+thisMicroRecall)
		thisAccuracy = float(thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TN']+thisIntervalResults['Subunit-Complex']['TN']+thisIntervalResults['None']['TP']+thisIntervalResults['None']['TN'])/(thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TN']+thisIntervalResults['Subunit-Complex']['TN']+thisIntervalResults['Protein-Component']['FP']+thisIntervalResults['Subunit-Complex']['FP']+thisIntervalResults['Protein-Component']['FN']+thisIntervalResults['Subunit-Complex']['FN']+thisIntervalResults['None']['TP']+thisIntervalResults['None']['TN']+thisIntervalResults['None']['FP']+thisIntervalResults['None']['FN'])
		self.__prfAllIntervals['Recall'].append(thisMicroRecall)
		self.__prfAllIntervals['Precision'].append(thisMicroPrecision)
		self.__prfAllIntervals['FScore'].append(thisFScore)
		self.__prfAllIntervals['Accuracy'].append(thisAccuracy)

	def getMicroPRFAllIntervals(self):
		return self.__prfAllIntervals

	def getUncertaintHistory(self):
		return self.__uncertaintyHistory
