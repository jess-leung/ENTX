from collections import defaultdict
from collections import Counter
import os
import random
import ActiveLearner 
import matplotlib.pyplot as plt
import PassiveLearner
from DataParser import createInstances, createLabels

if __name__ == "__main__":
	classifier_input = raw_input('Choose classifier 1) Linear SVM or 2) Max Ent: ')
	learntype_input = raw_input('Choose learning 1) Passive 2) Active: ')
	results_input = raw_input('Output results to text file (Y/N): ')

	# Now create instances with gold lables and attributes 
	STOPWORDS, genia_entity_words = [], []

	for line in open('biomedical_stopwords.txt'):
		STOPWORDS.append(line.strip())

	createLabels('dataset/Training copy','dataset/Training',)
	createLabels('dataset/Development copy','dataset/Development')

	''' BEGIN RELATIONSHIP EXTRACTION ''' 
	TRAINING_INSTANCES = createInstances('Dataset/Training',STOPWORDS)[0]
	DEV = createInstances('Dataset/Development',STOPWORDS)

	DEV_INSTANCES = DEV[0]
	# print len([d for d in DEV_INSTANCES if d.goldRelType!='None'])

	MISSED_ENTITIES = DEV[1]
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

	# Sort out which classifier 
	learner_type=None 
	if classifier_input == '1':
		learner_type = 'SVM'
	else: 
		learner_type = 'LogisticRegression'

	# Conduct passive learning 
	if learntype_input == '1':	
		passiveLearner = PassiveLearner.PassiveLearner(train_features,train_relType_trueLabels,learner_type,['Protein-Component','Subunit-Complex'])
		clf = passiveLearner.trainClassifier()
		predictedClasses = passiveLearner.classify(dev_features)
		passiveLearner.classificationReport(dev_relType_trueLabels,predictedClasses)

		# if results_input == "Y":
		# 	writeFile = open('results.txt','r+')
		# 	for idx,item in enumerate(predictedClass):
		# 		if item != 'None':
		# 			writeFile.write(TRAINING_INSTANCES[idx].document+' '+str(item)+' '+TRAINING_INSTANCES[idx].protein+' '+TRAINING_INSTANCES[idx].entity+'\n')
	# Else conduct active learning 
	else: 
		zippedTraining = zip(train_features,train_relType_trueLabels)
		zippedTesting = zip(dev_features,dev_relType_trueLabels)
		random.shuffle(zippedTraining)

		yAxis = range(2760,11260,250)
		# yAxis50 = range(2760,11060,50)
		# print len(yAxis50)
		''' Comparing 50 in each interval to 250 in each interval ''' 
		# svmLearner1 = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'SVM','hyperplane',False,50)
		# svmLearner2 = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'SVM','hyperplane',False,250)
		# print 'Getting 50 classifier'
		# svmLearner1.gettingClassifier()
		# print 'Getting 250 classifier'
		# svmLearner2.gettingClassifier()
		# results50 = svmLearner1.getMicroPRFAllIntervals()
		# print len(results50['FScore'])
		# results250 = svmLearner2.getMicroPRFAllIntervals()
		# plt.figure(1)
		# plt.title('Comparing number in each iteration')
		# plt.ylabel('F-Score')
		# plt.xlabel('Number of Training Instances')
		# plt.plot(yAxis50,results50['FScore'],'r--')
		# plt.plot(yAxis,results250['FScore'],'b--')
		# plt.show()

		''' Comparing different types of uncertainty measures '''
		EntropyLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','entropy',False,250)
		RandomLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','randomSampling',False,250)
		SMLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','smallestMargin',False,250)

		clfAct = EntropyLearner.gettingClassifier()
		cldRan = RandomLearner.gettingClassifier()
		# lcRan = LCLearner.gettingClassifier()
		smRan = SMLearner.gettingClassifier()

		results2 = RandomLearner.getMicroPRFAllIntervals()
		results = EntropyLearner.getMicroPRFAllIntervals()
		# results4 = LCLearner.getMicroPRFAllIntervals()
		results5 = SMLearner.getMicroPRFAllIntervals()

		# Plotting results 
		plt.figure(2)
		# F-SCORE 
		plt.subplot(1,3,3)
		plt.title('F-Score with different uncertainty measures')
		plt.ylabel('F-Score')
		plt.xlabel('Number of Training Instances')
		plt.plot(yAxis,results['FScore'],'r--',label='Entropy')
		plt.plot(yAxis,results2['FScore'],'g--',label='Random Sampling')
		# plt.plot(yAxis,results4['FScore'],'b--',label='Least Confidence')
		plt.plot(yAxis,results5['FScore'],'k--',label='Smallest Margin')
		plt.legend(loc='lower right')

		# # Precision 
		plt.subplot(1,3,1)
		plt.title('Precision with different uncertainty measures')
		plt.ylabel('Precision')
		plt.xlabel('Number of Training Instances')
		plt.plot(yAxis,results['Precision'],'r--',label='Entropy-based')
		plt.plot(yAxis,results2['Precision'],'g--',label='Random Sampling')
		# plt.plot(yAxis,results4['Precision'],'b--',label='Least Confidence')
		plt.plot(yAxis,results5['Precision'],'k--',label='Smallest Margin')
		plt.legend(loc='lower right')

		# # Recall 
		plt.subplot(1,3,2)
		plt.title('Recall with different uncertainty measures')
		plt.ylabel('Recall')
		plt.xlabel('Number of Training Instances')
		plt.plot(yAxis,results['Recall'],'r--',label='Entropy-based')
		plt.plot(yAxis,results2['Recall'],'g--',label='Random Sampling')
		# plt.plot(yAxis,results4['Recall'],'b--',label='Least Confidence')
		plt.plot(yAxis,results5['Recall'],'k--',label='Smallest Margin')
		plt.legend(loc='lower right')

		plt.show()

		###
		### COMPARE PERFECT WITH NOISY LABELLING ### 
		### 
		NoisyLearner = ActiveLearner.ActiveLearner(zippedTraining,zippedTesting,'LogisticRegression','entropy',True,250)
		clfNoise = NoisyLearner.gettingClassifier()
		results3 = NoisyLearner.getMicroPRFAllIntervals()
		# Plotting
		plt.figure(3)
		plt.subplot(1,3,1)
		plt.plot(yAxis,results3['Precision'],'b--',label='Noisy')
		plt.plot(yAxis,results['Precision'],'r--',label='Perfect')
		plt.ylabel('Precision')
		plt.legend(loc='lower right')
		plt.xlabel('# of Training Instances Used')
		plt.title('Comparison of Precision of Noisy v Perfect Annotation \n using Entropy-based Encertainty Measure')

		plt.subplot(1,3,2)
		plt.plot(yAxis,results3['Recall'],'b--',label='Noisy')
		plt.plot(yAxis,results['Recall'],'r--',label='Perfect')
		plt.legend(loc='lower right')
		plt.ylabel('Recall')
		plt.xlabel('# of Training Instances Used')
		plt.title('Comparison of Recall of Noisy v Perfect Annotation \n using Entropy-based Encertainty Measure')

		plt.subplot(1,3,3)
		plt.plot(yAxis,results3['FScore'],'b--',label='Noisy')
		plt.plot(yAxis,results['FScore'],'r--',label='Perfect')
		plt.legend(loc='lower right')
		plt.ylabel('F-Score')
		plt.xlabel('# of Training Instances Used')
		plt.title('Comparison of F-Score of Noisy v Perfect Annotation \n using Entropy-based Encertainty Measure')

		plt.show()
		