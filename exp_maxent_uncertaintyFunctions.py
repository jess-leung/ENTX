from collections import defaultdict
from collections import Counter
import os
import random
import ActiveLearner 
import matplotlib.pyplot as plt
import PassiveLearner
from DataParser import createInstances, createLabels

if __name__ == "__main__":
	# Now create instances with gold lables and attributes 
	STOPWORDS = []

	for line in open('biomedical_stopwords.txt'):
		STOPWORDS.append(line.strip())

	createLabels('dataset/Training copy','dataset/Training',)
	createLabels('dataset/Development copy','dataset/Development')

	''' BEGIN RELATIONSHIP EXTRACTION ''' 
	TRAINING_INSTANCES = createInstances('Dataset/Training',STOPWORDS)[0]
	DEV = createInstances('Dataset/Development',STOPWORDS)

	DEV_INSTANCES = DEV[0]
	train_containsRel_trueLabels = [] 
	dev_containsRel_trueLabels = [] 
	train_relType_trueLabels = [] 
	dev_relType_trueLabels = []
	train_features = [] 
	dev_features = [] 
	label_list=['NoRel','Rel']
	rel_list = ['None','Protein-Component','Subunit-Complex']

	for inst in TRAINING_INSTANCES: 
		train_containsRel_trueLabels.append(inst.goldContainsRel)
		train_features.append(inst.attribs)
		train_relType_trueLabels.append(inst.goldRelType)

	for inst in DEV_INSTANCES:
		dev_containsRel_trueLabels.append(inst.goldContainsRel)
		dev_features.append(inst.attribs)
		dev_relType_trueLabels.append(inst.goldRelType)

	# Conduct passive learning 
	zippedTraining = zip(train_features,train_relType_trueLabels)
	zippedTesting = zip(dev_features,dev_relType_trueLabels)
	
	''' Create an iterative process and average results of active learning over
	2 iterations to begin with ''' 
	results1 = defaultdict(lambda: defaultdict(list))
	results2 = defaultdict(lambda: defaultdict(list))
	results3 = defaultdict(lambda: defaultdict(list))
	results4 = defaultdict(lambda: defaultdict(list))

	averageResults = defaultdict(lambda: defaultdict(float))
	averageResults2 = defaultdict(lambda: defaultdict(float))
	averageResults3 = defaultdict(lambda: defaultdict(float))
	averageResults4 = defaultdict(lambda: defaultdict(float))

	for i in xrange(0,5):
		print 'Iteration '+str(i)
		random.shuffle(zippedTraining)
		# ''' Comparing different types of uncertainty measures '''
		RandomLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','randomSampling',0,250)
		RandomLearner.gettingClassifier()
		results_random = RandomLearner.getMicroPRFAllIntervals()

		LCLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','leastConfident',0,250)
		LCLearner.gettingClassifier()
		results_LCLearning = LCLearner.getMicroPRFAllIntervals()

		maxMarginLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','smallestMargin',0,250)
		maxMarginLearner.gettingClassifier()
		results_maxMargin = maxMarginLearner.getMicroPRFAllIntervals()

		entropyLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','entropy',0,250)
		entropyLearner.gettingClassifier()
		results_entropy = entropyLearner.getMicroPRFAllIntervals()

		results1['Precision'][i].extend(results_random['Precision'])
		results1['Recall'][i].extend(results_random['Recall'])
		results1['FScore'][i].extend(results_random['FScore'])
		results1['Accuracy'][i].extend(results_random['Accuracy'])
		results2['Precision'][i].extend(results_LCLearning['Precision'])
		results2['Recall'][i].extend(results_LCLearning['Recall'])
		results2['FScore'][i].extend(results_LCLearning['FScore'])
		results2['Accuracy'][i].extend(results_LCLearning['Accuracy'])
		results3['Precision'][i].extend(results_maxMargin['Precision'])
		results3['Recall'][i].extend(results_maxMargin['Recall'])
		results3['FScore'][i].extend(results_maxMargin['FScore'])
		results3['Accuracy'][i].extend(results_maxMargin['Accuracy'])
		results4['Precision'][i].extend(results_entropy['Precision'])
		results4['Recall'][i].extend(results_entropy['Recall'])
		results4['FScore'][i].extend(results_entropy['FScore'])
		results4['Accuracy'][i].extend(results_entropy['Accuracy'])

	for resultsMeasure in results1: 
		for i in xrange(0,len(results1[resultsMeasure][0])):
			for iteration,value in results1[resultsMeasure].iteritems():
				averageResults[resultsMeasure][i]+=results1[resultsMeasure][iteration][i]
			averageResults[resultsMeasure][i]=averageResults[resultsMeasure][i]/float(len(results1[resultsMeasure]))*100

	for resultsMeasure in results2: 
		for i in xrange(0,len(results2[resultsMeasure][0])):
			for iteration,value in results2[resultsMeasure].iteritems():
				averageResults2[resultsMeasure][i]+=results2[resultsMeasure][iteration][i]
			averageResults2[resultsMeasure][i]=averageResults2[resultsMeasure][i]/float(len(results2[resultsMeasure]))*100

	for resultsMeasure in results3: 
		for i in xrange(0,len(results3[resultsMeasure][0])):
			for iteration,value in results3[resultsMeasure].iteritems():
				averageResults3[resultsMeasure][i]+=results3[resultsMeasure][iteration][i]
			averageResults3[resultsMeasure][i]=averageResults3[resultsMeasure][i]/float(len(results3[resultsMeasure]))*100

	for resultsMeasure in results4: 
		for i in xrange(0,len(results4[resultsMeasure][0])):
			for iteration,value in results4[resultsMeasure].iteritems():
				averageResults4[resultsMeasure][i]+=results4[resultsMeasure][iteration][i]
			averageResults4[resultsMeasure][i]=averageResults4[resultsMeasure][i]/float(len(results4[resultsMeasure]))*100
	print averageResults4

	allResults = [averageResults,averageResults2,averageResults3,averageResults4]
	xAxis = range(2000,11500,250)
	counter=0
	reCounter=0
	print 'CLASSIFICATION REPORT' 
	""" print exact results out for each point on the graph """ 
	for resultsItem in allResults:
		print 'Index ',reCounter
		print 'Sample size   Precision   Recall   F-Score   Accuracy'
		print '-----------------------------------------------------'
		for point in xAxis: 
			print '%d           %.2f      %.2f    %.2f    %.2f' %(point,resultsItem['Precision'][counter],resultsItem['Recall'][counter],resultsItem['FScore'][counter],resultsItem['Accuracy'][counter])
			counter+=1
		reCounter+=1
		counter=0

	""" plot results time """
	plt.subplot(1,3,1)
	plt.plot(xAxis,averageResults['Precision'].values(),'b--',label='Random Sampling')
	plt.plot(xAxis,averageResults2['Precision'].values(),'k--',label='Least Confident')
	plt.plot(xAxis,averageResults3['Precision'].values(),'r--',label='Smallest Margin')
	plt.plot(xAxis,averageResults4['Precision'].values(),'g--',label='Maximum Entropy')
	plt.ylabel('Precision')
	plt.legend(loc='lower right',prop={'size':6})
	plt.xlabel('# of Training Instances Used')
	plt.title('Comparison of Precision With \n Different Uncertainty Measures')

	plt.subplot(1,3,2)
	plt.plot(xAxis,averageResults['Recall'].values(),'b--',label='Random Sampling')
	plt.plot(xAxis,averageResults2['Recall'].values(),'k--',label='Least Confident')
	plt.plot(xAxis,averageResults3['Recall'].values(),'r--',label='Smallest Margin')
	plt.plot(xAxis,averageResults4['Recall'].values(),'g--',label='Maximum Entropy')
	plt.legend(loc='lower right',prop={'size':6})
	plt.ylabel('Recall')
	plt.xlabel('# of Training Instances Used')
	plt.title('Comparison of Recall With \n Different Uncertainty Measures')

	plt.subplot(1,3,3)
	plt.plot(xAxis,averageResults['FScore'].values(),'b--',label='Random Sampling')
	plt.plot(xAxis,averageResults2['FScore'].values(),'k--',label='Least Confident')
	plt.plot(xAxis,averageResults3['FScore'].values(),'r--',label='Smallest Margin')
	plt.plot(xAxis,averageResults4['FScore'].values(),'g--',label='Maximum Entropy')
	plt.legend(loc='lower right',prop={'size':6})
	plt.ylabel('F-Score')
	plt.xlabel('# of Training Instances Used')
	plt.title('Comparison of F-Score With \n Different Uncertainty Measures')

	plt.show()
