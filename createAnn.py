''' this program creates the annotation files for BRAT visualisation '''
from os.path import basename
import os 

for filename in os.listdir('Dataset/GE-Training'):
	if filename.endswith('.txt'):
		baseFileName= os.path.splitext(filename)[0]
		a1File = 'Dataset/GE-Training/'+baseFileName+'.a1'
		relFile = 'Dataset/GE-Training/'+baseFileName+'.a2'
		newA1File = open('Dataset/GE-Training/'+baseFileName+'.ann','w')
		with open(a1File) as a1: 
			for line in a1:
				# print line
				newA1File.write(line)
		with open(relFile) as rel:
			for line in rel:
				newA1File.write(line)