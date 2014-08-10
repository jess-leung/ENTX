from collections import defaultdict
import re 

class Instance(object):

	i=0

	def __init__(self, document, protein, entity, idxP, idxE, sentence, relType, containsRel, stopwords):
		self.document = document
		self.attribs = self.getFeatures(protein,entity,idxP, idxE, sentence, stopwords)
		self.goldRelType = relType
		self.goldContainsRel = containsRel
		self.protein = protein
		self.entity = entity
		

	def getFeatures(self,protein,entity,idxP,idxE,sentence,stopwords):
		''' Current list of features: 
			1. Bag of words for protein and entity and the words in between protein and entity 
			2. Word before/after protein/entity 
			3. The gene/gene-product 
			4. Stem of protein and entity
			5. NER tag of the protein and entity 
			6. POS tag of protein and entity
			7. POS tag before/after protein/entity 
			8. Chunking tag of protein and entity
			9. Distance (# words) between protein and entity
			10. Sequence of POS tags between protein and entity
			11. Bigrams of (sequential) words
			12. Head word of protein and entity 
			13. Dependency path between protein and entity 
			14. If token is digit 
			15. GENIA Event corpus --> has annotated entities 
			16. Number of named entities between the protein and entity 
			17. Parse tree features  
			18. Whether the protein is embedded in the entity 
		'''
		protein = protein.replace('-',' - ')
		protein = protein.replace('/',' / ')
		protein = protein.replace('(',' ( ')
		protein = protein.replace(')',' ) ')
		entity = entity.replace("'"," ' ")
		entity = entity.replace('-',' - ')
		entity = entity.replace('/',' / ')
		entity = entity.replace('(',' ( ')
		entity = entity.replace(')',' ) ')
		entity = entity.replace("'"," ' ")

		featureSet, dependencyPath = defaultdict(), defaultdict()
		chunkingFeature, posSequence, chunkingBTFeature = "", "", ""
		distance, proteinCheck, entityCheck, distanceFlag, sentenceLength, numberOfNamedEntities,numberNERBetween = 0, 0, 0, 0, 0, 0,0
		proteinHead,entityHead='','' 
		proteinWords,entityWords=protein.split(), entity.split()
		root=''
		idxEEnd = int(idxE)+len(entityWords)-1
		idxPEnd = int(idxP)+len(proteinWords)-1
		entityList = []

		for line in open("entity-list.txt"): 
			entityList.append(line.strip())

		if idxP>=idxE and idxPEnd<=idxEEnd: 
			featureSet[(protein,'embeddedProtein')]=1

		for idx, word in enumerate(sentence):
			sentenceLength+=1
			thisDepParent = sentence[int(word[4])-1][1]
			thisDep = word[5]
			dependencyPath[word[0]]=(thisDepParent,thisDep)
			featureSet[(word[0],'bagOfWords')]=1

			if word[6][0]=='B':
				numberOfNamedEntities+=1

			# Check if this word is a part of the protein word 
			if idx >= idxP and idx<=idxPEnd: 
				if word[0] not in stopwords:
					featureSet[(word[0],'bagOfWordsProtein')]=1
					featureSet[(word[1],'lemmaProtein')]=1
				featureSet[(word[2],'posProtein')]=1
				if word[6][0]=='B':
					featureSet[(word[6][2:],'NERProtein')]=1
				featureSet[(word[3],'ChunkProtein')]=1
				if word[0].isdigit():
					featureSet['containsDig']=1
				featureSet[(word[5],'DependencyPro')]=1

			if idx >= idxE and idx <= idxEEnd:
				featureSet[(word[0],'bagOfWordsEntity')]=1
				featureSet[(word[1],'lemmaEntity')]=1
				featureSet[(word[2],'posEntity')]=1
				if word[6][0]=='B':
					featureSet[(word[6][2:],'NEREntity')]=1
				if word[0].isdigit():
					featureSet['containsDig']=1
				featureSet[(word[3],'ChunkEntity')]=1
				featureSet[(word[5],'DependencyEnt')]=1
				if word[0] in entityList: 
					featureSet[(word[0],'inEntityList')]=1

			if word[5]=="ROOT":
				root = word[6] 

			''' Get words in between '''
			# Scenario where protein comes before entity in sentence 
			if idxEEnd > idxPEnd: 
				if idx > idxPEnd and idx < idxEEnd: 
					distance+=1
					featureSet[(word[0],'wordInBetween')]=1
					featureSet[(word[2],'posInBetween')]=1
					# featureSet[('before','proteinPosition')]=1
					featureSet[(word[3],'ChunkInBetween')]=1
					# if word[6][0]=='B':
					# 	featureSet[(word[6][2:],'NEREntity')]=1
					# featureSet[(word[1],'wordStemInBetween')]=1
					if word[6]!='O':
						numberNERBetween+=1
						# featureSet[(word[6],'NERInBetween')]=1

				# elif idx < idxP or idx > idxEEnd:
				# 	featureSet[(word[0],'otherWords')]=1
			# Scenario where entity comes before protein in sentence 
			elif idxPEnd > idxEEnd: 
				if idx > idxEEnd and idx < idxPEnd: 
					distance+=1
					featureSet[(word[0],'wordInBetween')]=1
					featureSet[(word[2],'posInBetween')]=1
					# featureSet[('after','proteinPosition')]=1
					featureSet[(word[3],'ChunkInBetween')]=1
					# if word[6][0]=='B':
					# 	featureSet[(word[6][2:],'NEREntity')]=1
					# featureSet[(word[1],'wordStemInBetween')]=1
					if word[6]!='O':
						numberNERBetween+=1
						# featureSet[(word[6],'NERInBetween')]=1
				# elif idx < idxE or idx > idxPEnd: 
				# 	featureSet[(word[0],'otherWords')]=1

			''' 
			Words before and after entity and protein 
			'''
			if idxE != 0 and idx == idxE-1:
			# Check if word before entity 
				featureSet[(sentence[idx][0],'wordBeforeEntity')]=1
				featureSet[(sentence[idx][2],'posBeforeEntity')]=1
			elif idxE == 0:  
				featureSet[('NULL','wordBeforeEntity')]=1
				featureSet[('NULL','posBeforeEntity')]=1
			# Check if word before protein 
			if idxP > 0 and idx == idxP-1:
				featureSet[(sentence[idx][0],'wordBeforeProtein')]=1
				featureSet[(sentence[idx][2],'posBeforeProtein')]=1
			elif idxP == 0: 
				featureSet[('NULL','wordBeforeProtein')]=1
				featureSet[('NULL','posBeforeProtein')]=1
			# Check word after protein 
			if idxP < len(sentence)-1 and idx == idxP+1: 
				featureSet[(sentence[idx][0],'wordAfterProtein')]=1 
				featureSet[(sentence[idx][2],'posAfterProtein')]=1
			elif idxP == len(sentence)-1:
				featureSet[('NULL','wordAfterProtein')]=1
				featureSet[('NULL','posAfterProtein')]=1
			# Check word after entity 
			if idxE < len(sentence)-1 and idx == idxE+1: 
				featureSet[(sentence[idx][0],'wordAfterEntity')]=1
				featureSet[(sentence[idx][2],'posAfterEntity')]=1
			elif idxE == len(sentence)-1:
				featureSet[('NULL','wordAfterEntity')]=1
				featureSet[('NULL','posAfterEntity')]=1

			if word[3][0]=='B':
				chunkingFeature+=word[3][2:]

			''' Bigrams and trigrams '''
			if idx < len(sentence)-1:
				featureSet[(word[0]+sentence[idx+1][0],'bigram')]=1

			if idx < len(sentence)-2: 
				featureSet[(word[0]+sentence[idx+1][0]+sentence[idx+2][0],'trigram')]=1
		# print dependencyPath
		# print proteinWords
		# for p in proteinWords:
		# 	if p in dependencyPath.keys():
		# 	#print 'Check:',dependencyPath[protein][0]
		# 	if dependencyPath[p][0] not in proteinWords: 
		# 		proteinHead=p 
		# 		break
				

		# for e in entityWords:
		# 	if dependencyPath[e][0] not in entityWords: 
		# 		entityHead=e
		# 		break

		# featureSet[ (entityHead, 'entityHead') ]=1
		featureSet[ (root, 'root') ]=1
		# featureSet[ (numberNERBetween, 'numberNERBetween') ]=1
		featureSet[ (proteinHead, 'proteinHead') ]=1 
		featureSet[ (protein,'GGP') ]=1
		featureSet[ (entity, 'entity') ]=1
		featureSet[ (sentenceLength,'sentenceLength') ]=1
		featureSet[ (distance,'distance') ]=1
		featureSet[ (chunkingFeature,'chunking') ]=1
		featureSet[ (posSequence,'posSequence') ]=1
		# featureSet[ (numberOfNamedEntities, 'no.NER') ]=1

		return featureSet
