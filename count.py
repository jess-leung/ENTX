''' this program creates the annotation files for BRAT visualisation '''
from os.path import basename
import os 

count=0 
countDoc=0
docContainsRelFlag=0
countNumberOfDocs=0
for filename in os.listdir('DevData/rel'):
	if filename.endswith('.rel'):
		with open('DevData/rel/'+filename) as rel:
			docContainsRelFlag=False
			for line in rel:
				line = line.split()
				if line[0][:1] == "R":
					count+=1 
					docContainsRelFlag=True
			if docContainsRelFlag==True:
				countDoc+=1
			countNumberOfDocs+=1
print count 
print countDoc
print countNumberOfDocs