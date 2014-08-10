import os
import nltk 
from collections import defaultdict
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize import SpaceTokenizer 

if __name__ == "__main__":
	#DOCUMENTS=[]
	instances=[]
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	parseFile = open('trainingData.txt','w')
	print 'Reading documents...'

	# Loop through files in DevData
	for filename in os.listdir('TrainingData'):
		# Check if text file 
		if filename.endswith('.txt'):
			baseFilename = os.path.splitext(filename)[0]

			# Open file to write to and annotation file 
			data = open('TrainingData/'+filename).read()
			annotationFile = open('TrainingData/ann/'+baseFilename+'.ann')

			# Tokenize into sentences 
			thisDocument=tokenizer.tokenize(data)

			# Header for new document 
			parseFile.write('DOCSTART '+baseFilename+'\n\n')
			offset = 0 

			ANNOTATIONS = [] 
			STARTINGOFFSETS = [] 

			# loop through annotation file 
			for line in annotationFile:
				line = line.split() 
				ANNOTATIONS.append(line)
				STARTINGOFFSETS.append(line[2])
			# print STARTINGOFFSETS
			# Loop through sentences in document 
			for sentence in thisDocument:
				words = SpaceTokenizer().tokenize(sentence)
				sentenceOffsets = list(WhitespaceTokenizer().span_tokenize(sentence))
				trueOffsets=[]  

				for o in sentenceOffsets:
					trueOffsets.append((o[0]+offset,o[1]+offset))

				if offset==0:
					offset=1
				offset+=len(sentence)+1

				for idx, word in enumerate(words):
					postag = nltk.pos_tag([word])
					try: 
						start = STARTINGOFFSETS.index(str(trueOffsets[idx][0]))
						parseFile.write(ANNOTATIONS[start][0]+' '+ANNOTATIONS[start][1]+' '+postag[0][1]+' '+str(trueOffsets[idx][0])+' '+str(trueOffsets[idx][1])+' '+word+'\n')
					except: 
						parseFile.write('O O'+' '+postag[0][1]+' '+str(trueOffsets[idx][0])+' '+str(trueOffsets[idx][1])+' '+word+'\n')
				parseFile.write('\n')
			#DOCUMENTS.append((baseFilename,thisDocumentWithOffsets))

	# for document in DOCUMENTS: 
	# 	for sentence in document[1]:
	# 		if document[0]=="PMID-10089566":
	# 			print sentence
	# 		containsSR=True
	# 		instances.append(Instance(document,sentence,containsSR))
