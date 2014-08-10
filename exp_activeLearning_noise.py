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
	
	xAxis = range(2000,11500,250)
	print len(xAxis)
	''' Create an iterative process and average results of active learning over
	2 iterations to begin with ''' 
	results1 = defaultdict(lambda: defaultdict(list))
	results2 = defaultdict(lambda: defaultdict(list))
	results3 = defaultdict(lambda: defaultdict(list))
	results4 = defaultdict(lambda: defaultdict(list))
	results5 = defaultdict(lambda: defaultdict(list))
	averageResults = defaultdict(lambda: defaultdict(float))
	averageResults2 = defaultdict(lambda: defaultdict(float))
	averageResults3 = defaultdict(lambda: defaultdict(float))
	averageResults4 = defaultdict(lambda: defaultdict(float))
	averageResults5 = defaultdict(lambda: defaultdict(float)) 

	for i in xrange(0,5):
		print 'Iteration '+str(i)
		random.shuffle(zippedTraining)
		''' Comparing different types of uncertainty measures '''
		ActLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'SVM','hyperplane',0.10,250)
		ActLearner.gettingClassifier()
		results = ActLearner.getMicroPRFAllIntervals()

		PerfectLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'SVM','hyperplane',0,250)
		PerfectLearner.gettingClassifier()
		results_perfectLearning = PerfectLearner.getMicroPRFAllIntervals()

		onePercent = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'SVM','hyperplane',0.01,250)
		onePercent.gettingClassifier()
		onePercentResults = onePercent.getMicroPRFAllIntervals()

		fivePercent = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'SVM','hyperplane',0.05,250)
		fivePercent.gettingClassifier()
		fivePercentResults = fivePercent.getMicroPRFAllIntervals()

		twentyPercent = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'SVM','hyperplane',0.20,250)
		twentyPercent.gettingClassifier()
		twentyPercentResults = twentyPercent.getMicroPRFAllIntervals()

		results1['Precision'][i].extend(results['Precision'])
		results1['Recall'][i].extend(results['Recall'])
		results1['FScore'][i].extend(results['FScore'])
		results2['Precision'][i].extend(results_perfectLearning['Precision'])
		results2['Recall'][i].extend(results_perfectLearning['Recall'])
		results2['FScore'][i].extend(results_perfectLearning['FScore'])
		results3['Precision'][i].extend(onePercentResults['Precision'])
		results3['Recall'][i].extend(onePercentResults['Recall'])
		results3['FScore'][i].extend(onePercentResults['FScore'])
		results4['Precision'][i].extend(fivePercentResults['Precision'])
		results4['Recall'][i].extend(fivePercentResults['Recall'])
		results4['FScore'][i].extend(fivePercentResults['FScore'])
		results5['Precision'][i].extend(twentyPercentResults['Precision'])
		results5['Recall'][i].extend(twentyPercentResults['Recall'])
		results5['FScore'][i].extend(twentyPercentResults['FScore'])

	for resultsMeasure in results1: 
		for i in xrange(0,len(results1[resultsMeasure][0])):
			for iteration,value in results1[resultsMeasure].iteritems():
				averageResults[resultsMeasure][i]+=results1[resultsMeasure][iteration][i]
			averageResults[resultsMeasure][i]=averageResults[resultsMeasure][i]/float(len(results1[resultsMeasure]))

	for resultsMeasure in results2: 
		for i in xrange(0,len(results2[resultsMeasure][0])):
			for iteration,value in results2[resultsMeasure].iteritems():
				averageResults2[resultsMeasure][i]+=results2[resultsMeasure][iteration][i]
			averageResults2[resultsMeasure][i]=averageResults2[resultsMeasure][i]/float(len(results2[resultsMeasure]))

	for resultsMeasure in results3: 
		for i in xrange(0,len(results3[resultsMeasure][0])):
			for iteration,value in results3[resultsMeasure].iteritems():
				averageResults3[resultsMeasure][i]+=results3[resultsMeasure][iteration][i]
			averageResults3[resultsMeasure][i]=averageResults3[resultsMeasure][i]/float(len(results3[resultsMeasure]))

	for resultsMeasure in results4: 
		for i in xrange(0,len(results4[resultsMeasure][0])):
			for iteration,value in results4[resultsMeasure].iteritems():
				averageResults4[resultsMeasure][i]+=results4[resultsMeasure][iteration][i]
			averageResults4[resultsMeasure][i]=averageResults4[resultsMeasure][i]/float(len(results4[resultsMeasure]))

	for resultsMeasure in results5: 
		for i in xrange(0,len(results5[resultsMeasure][0])):
			for iteration,value in results2[resultsMeasure].iteritems():
				averageResults5[resultsMeasure][i]+=results5[resultsMeasure][iteration][i]
			averageResults5[resultsMeasure][i]=averageResults5[resultsMeasure][i]/float(len(results5[resultsMeasure]))


	# print averageResults

	""" plot results time """
	plt.subplot(1,3,1)
	plt.plot(xAxis,averageResults['Precision'].values(),'b--',label='0.10 noise')
	plt.plot(xAxis,averageResults3['Precision'].values(),'k--',label='0.01 noise')
	plt.plot(xAxis,averageResults4['Precision'].values(),'g--',label='0.05 noise')
	plt.plot(xAxis,averageResults5['Precision'].values(),'c--',label='0.20 noise')
	plt.plot(xAxis,averageResults2['Precision'].values(),'r--',label='No noise')
	plt.ylabel('Precision')
	plt.legend(loc='lower right')
	plt.xlabel('# of Training Instances Used')
	plt.title('Comparison of Precision of Noisy v Perfect Annotation')

	plt.subplot(1,3,2)
	plt.plot(xAxis,averageResults['Recall'].values(),'b--',label='0.10 noise')
	plt.plot(xAxis,averageResults3['Recall'].values(),'k--',label='0.01 noise')
	plt.plot(xAxis,averageResults4['Recall'].values(),'g--',label='0.05 noise')
	plt.plot(xAxis,averageResults5['Recall'].values(),'c--',label='0.20 noise')
	plt.plot(xAxis,averageResults2['Recall'].values(),'r--',label='No noise')
	plt.legend(loc='lower right')
	plt.ylabel('Recall')
	plt.xlabel('# of Training Instances Used')
	plt.title('Comparison of Recall of Noisy v Perfect Annotation')

	plt.subplot(1,3,3)
	plt.plot(xAxis,averageResults['FScore'].values(),'b--',label='0.10 noise')
	plt.plot(xAxis,averageResults3['FScore'].values(),'k--',label='0.01 noise')
	plt.plot(xAxis,averageResults4['FScore'].values(),'g--',label='0.05 noise')
	plt.plot(xAxis,averageResults5['FScore'].values(),'c--',label='0.20 noise')
	plt.plot(xAxis,averageResults2['FScore'].values(),'r--',label='No noise')
	plt.legend(loc='lower right')
	plt.ylabel('F-Score')
	plt.xlabel('# of Training Instances Used')
	plt.title('Comparison of F-Score of Noisy v Perfect Annotation')

	plt.show()
