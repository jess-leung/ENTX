import os 
from collections import defaultdict 
import instance
""" This file contains some of the data parsing functions used. 
Taken out of the main file for readability """ 

def createLabels(dirFrom,dirTo):
	for f in os.listdir(dirFrom):
		if f.endswith('.txt'):
			baseFilename = f[:-4]
			# print baseFilename
			thisFile = open(dirFrom+'/'+f,'r')
			writeFile = open(dirTo+'/'+f,'r+')
			writeFile.truncate()
			content = thisFile.readlines()
			countIdx=0
			myEntityCount=0
			newContent=''
			previousLabel=''
			for idx,line in enumerate(content):
				line = line.split()
				thisLabel='O'
				thisTerm='O'
				if len(line)>0:
					thisTerm = line[0]
					thisLabel = line[1]
					newLine = thisTerm+'\t'+thisLabel+'\t'+line[1]+'\t'+line[2]+'\t'+line[3]+'\t'+line[4]+'\t'+line[5]+'\t'+line[6]+'\t'+line[7]+'\t'+line[8]+'\t'+line[9]+'\t'+line[10]+'\t'+line[11]
					newContent+=newLine+'\n'
				else:
					newContent+='\n'
			writeFile.write(newContent)
			writeFile.close()
			thisFile.close()

def createInstances(dirPath,STOPWORDS): 
	INSTANCES = []
	MISSED=[]
	totalRel=0
	relStatus=defaultdict(lambda: defaultdict(int))
	print 'Creating Instances...'
	for f in os.listdir(dirPath):
		if f.endswith('.txt'):
			baseFilename = f[:-4]
			# print baseFilename
			sentenceCount=0
			proteins, entities, thisSentence, entitiesID, proteinsID = [], [], [], [], []
			termsMapping, equivMapping, proteinsMapping, entitiesMapping, rels, idxMapping, extraMapping = defaultdict(), defaultdict(), defaultdict(), defaultdict(), defaultdict(), defaultdict(), defaultdict()
			thisEntity, thisProtein = '',''
			idxProteinStart, idxEntityStart, idxCount, idxMyEnt = 0,0,0,0
			MISSED_ENTITIES=[]
			EXTRA_ENTITIES=[]

			# open the file with rels and parse it 
			relFile = open(dirPath+'/'+baseFilename+'.ann')
			for line in relFile: 
				line = line.split()
				if line[0][0]=='R':
					arg1 = line[2][5:]
					arg2 = line[3][5:]
					# Appending (Protein, Entity, Rel Type) to rels
					rels[(arg1,arg2)]=line[1]

				elif line[0][0]!='*': 
					termsMapping[line[0]]=' '.join(line[4:])
			
				elif line[0][0]=='*':
					equivMapping[line[2]]=line[3]
					equivMapping[line[3]]=line[2]

			for rel in rels.keys(): 
				if rel[0] in equivMapping: 
					rels[(equivMapping[rel[0]],rel[1])]=rels[rel]
				if rel[1] in equivMapping:
					rels[(rel[0],equivMapping[rel[1]])]=rels[rel]
			# totalRel+=len(rels)
			relStatus[baseFilename] = dict.fromkeys(rels.keys(),0)

			fileWithStuff = open(dirPath+'/'+f).readlines()
			# loop through the file containing all the stuff! 
			for idx,line in enumerate(fileWithStuff):
				line = line.split()  
				if len(line)==0:
					# Check every combination of protein+entity and create an Instance (i.e. feature extract and get gold labels)
					MISSED_ENTITIES = [u for u in MISSED_ENTITIES if u not in entities]
					
					for protein in proteins:
						for entity in entities: 
							thisRelationship='None'
							containsRel='NoRel'
							if (protein,entity) in rels: 
								thisRelationship=rels[(protein,entity)]
								containsRel='Rel'
								relStatus[baseFilename][(protein,entity)]=1
							INSTANCES.append(instance.Instance(baseFilename,termsMapping[protein],termsMapping[entity],idxMapping[protein],idxMapping[entity],thisSentence,thisRelationship,containsRel,STOPWORDS))

						for entity in MISSED_ENTITIES:
							thisRelationship='None'
							if (protein,entity) in rels:
								thisRelationship=rels[(protein,entity)]	

							MISSED.append(('None',thisRelationship))

						for entity in EXTRA_ENTITIES:
							INSTANCES.append(instance.Instance(baseFilename,termsMapping[protein],extraMapping[entity],idxMapping[protein],idxMapping[entity],thisSentence,'None','NoRel',STOPWORDS))

					entities, proteins, thisSentence = [], [], []
					sentenceCount+=1 
					idxEntityStart, idxProteinStart, idxCount=0,0,0
					MISSED_ENTITIES,EXTRA_ENTITIES=[],[]

				else: # on the same sentence
					# Check if our label matches gold label (approx span match)
					
					theseTerms = line[0].split(',')
					theseRealEntLabels = line[2].split(',')
					theseMyEntLabels = line[1].split(',')

					for idx, label in enumerate(theseMyEntLabels):
						# Check for proteins (gold)
						if "B-Protein" in theseMyEntLabels or "I-Protein" in theseMyEntLabels:
							if theseTerms[idx] not in proteins:
								proteins.append(theseTerms[idx])
								idxMapping[theseTerms[idx]]=idxCount

						elif (label=='B-Entity' or label=="I-Entity"):
							if 'B-Entity' in theseRealEntLabels or 'I-Entity' in theseRealEntLabels:
								if theseTerms[idx] not in entities: 
									entities.append(theseTerms[idx])
									idxMapping[theseTerms[idx]]=idxCount

						# Check for gold is entity but ours is O 
						elif theseMyEntLabels[0] =='O' and ("B-Entity" in theseRealEntLabels or "I-Entity" in theseRealEntLabels):
								MISSED_ENTITIES.extend(theseTerms)

						# Check for things we labelled as entities but are actually nothing 
						elif (line[0][0]=='E'): 
							if idx>0: 
								if  'B-Entity' not in fileWithStuff[idx-1][0] and 'I-Entity' not in fileWithStuff[idx-1][0] and 'B-Entity' not in fileWithStuff[idx+1][0] and 'I-Entity' not in fileWithStuff[idx+1][0]:
									EXTRA_ENTITIES.append(line[0])
									extraMapping[line[0]]=line[5]
									idxMapping[line[0]]=idxCount
							else: 
								if fileWithStuff[idx+1][0] == 'O':
									EXTRA_ENTITIES.append(line[0])
									extraMapping[line[0]]=line[5]
									idxMapping[line[0]]=idxCount

					idxCount+=1
					# Append [word, lemma, pos, chunk, no, dep, NER]
					thisSentence.append([line[5],line[6],line[8],line[7],line[10],line[11],line[12]])

			MISSED_ENTITIES = [u for u in MISSED_ENTITIES if u not in entities]

			for protein in proteins:
				for entity in entities: 
					thisRelationship='None'
					containsRel='NoRel'
					if (protein,entity) in rels: 
						thisRelationship=rels[(protein,entity)]	
						containsRel='Rel'
					INSTANCES.append(instance.Instance(baseFilename,termsMapping[protein],termsMapping[entity],idxMapping[protein],idxMapping[entity],thisSentence,thisRelationship,containsRel,STOPWORDS))

				for entity in MISSED_ENTITIES:
					thisRelationship='None'
					if (protein,entity) in rels:
						thisRelationship=rels[(protein,entity)]	
					MISSED.append(('None',thisRelationship))

				for entity in EXTRA_ENTITIES:
					INSTANCES.append(instance.Instance(baseFilename,termsMapping[protein],extraMapping[entity],idxMapping[protein],idxMapping[entity],thisSentence,'None','NoRel',STOPWORDS))

			entities, proteins, thisSentence = [], [], []
			sentenceCount+=1 
			idxEntityStart, idxProteinStart, idxCount=0,0,0
			MISSED_ENTITIES,EXTRA_ENTITIES=[],[]

	return [INSTANCES, MISSED] 