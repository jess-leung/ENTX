from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression 
from sklearn import metrics  
from sklearn.feature_extraction import DictVectorizer
import numpy as np 
from collections import defaultdict

class PassiveLearner:
	"""This class conducts active learning, rather than passive learning. 
	""" 
	def __init__(self,trainingInstances,trainingTrueLabels,learnerType,classes):
		"""Constructor
		"""
		self.__learnerType = learnerType 
		self.__trainingInstances = trainingInstances
		self.__trainingTrueLabels = trainingTrueLabels
		self.__results = defaultdict(float)
		self.__classResults = defaultdict(lambda: defaultdict(float))
		self.__classes = classes
		self.__vectorizer = DictVectorizer()
		self.__clf = None

	def trainClassifier(self):
		""" This method trains the classifier using training data """ 
		if self.__learnerType=='SVM':
			self.__clf=LinearSVC() 
		else: 
			self.__clf=LogisticRegression()

		train_features_fitted = self.__vectorizer.fit_transform(self.__trainingInstances)
		train_trueLabels_np = np.array(self.__trainingTrueLabels)
		self.__clf.fit(train_features_fitted,train_trueLabels_np)

	def classify(self,x):
		"""This method classifies x (in dictionary format), given some classifier 
		"""
		x_transformed = self.__vectorizer.transform(x)
		prediction = self.__clf.predict(x_transformed)
		return prediction 

	def classificationReport(self,trueLabels,predictedLabels):
		"""This method prints out the classification report"""
		self.__microPRF(trueLabels,predictedLabels)
		print '\nCLASSIFICATION REPORT'
		print 'Accuracy: ',self.__results['Accuracy']
		print 'Class                Precision  Recall  F-Score'
		print '-----------------------------------------------'
		for c in self.__classes:
			print c.ljust(20),'%.2f      %.2f   %.2f' %(self.__classResults[c]['Precision'],self.__classResults[c]['Recall'],self.__classResults[c]['FScore'])
		print 'Overall'.ljust(20),'%.2f      %.2f   %.2f' %(self.__results['Precision'],self.__results['Recall'],self.__results['FScore'])

	def __getTrueAndFalsePosNegs(self,truelabels,predictedLabels):
		"""This method gets the true and false positives and negatives number"""
		zippedResults = zip(truelabels,predictedLabels)
		counter = defaultdict(lambda:defaultdict(int))
		for result in zippedResults:
			if result[0]==result[1]:
				counter[result[0]]['TP']+=1
			elif result[0]!= result[1]:
				counter[result[0]]['FN']+=1 
				counter[result[1]]['FP']+=1
		return counter 

	def __microPRF(self,truelabels,predictedLabels):
		"""This method finds the PRF values"""
		thisIntervalResults = self.__getTrueAndFalsePosNegs(truelabels,predictedLabels)

		# get per class results 
		for c in self.__classes: 
			self.__classResults[c]['Precision'] = float(thisIntervalResults[c]['TP'])/(thisIntervalResults[c]['TP']+thisIntervalResults[c]['FP'])*100
			self.__classResults[c]['Recall'] = float(thisIntervalResults[c]['TP'])/(thisIntervalResults[c]['TP']+thisIntervalResults[c]['FN'])*100
			self.__classResults[c]['FScore'] = 2*self.__classResults[c]['Precision']*self.__classResults[c]['Recall']/(self.__classResults[c]['Precision']+self.__classResults[c]['Recall'])

		# get overall results 
		thisMicroRecall = float(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP'])/(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['FN']+thisIntervalResults['Protein-Component']['FN'])
		thisMicroPrecision = float(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP'])/(thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['FP']+thisIntervalResults['Protein-Component']['FP'])
		thisFScore = 2*thisMicroPrecision*thisMicroRecall/(thisMicroPrecision+thisMicroRecall)
		thisAccuracy = float(thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TN']+thisIntervalResults['Subunit-Complex']['TN']+thisIntervalResults['None']['TP']+thisIntervalResults['None']['TN'])/(thisIntervalResults['Protein-Component']['TP']+thisIntervalResults['Subunit-Complex']['TP']+thisIntervalResults['Protein-Component']['TN']+thisIntervalResults['Subunit-Complex']['TN']+thisIntervalResults['Protein-Component']['FP']+thisIntervalResults['Subunit-Complex']['FP']+thisIntervalResults['Protein-Component']['FN']+thisIntervalResults['Subunit-Complex']['FN']+thisIntervalResults['None']['TP']+thisIntervalResults['None']['TN']+thisIntervalResults['None']['FP']+thisIntervalResults['None']['FN'])

		self.__results['Recall'] = thisMicroRecall*100
		self.__results['Precision'] = thisMicroPrecision*100
		self.__results['FScore'] = thisFScore*100
		self.__results['Accuracy'] = thisAccuracy*100


	def confusionMatrix(self,trueLabels,predictedLabels):
		# pass
		print metrics.confusion_matrix(trueLabels, predictedLabels, labels=['None','Subunit-Complex','Protein-Component'])

	def writeResultsToFile(self,filename):
		pass 
