import os 
from collections import defaultdict 
from collections import Counter
# T91	Entity 1333 1367	amino-terminal proline-rich region
# T92	Entity 1529 1550	leucine zipper domain

entityWords = defaultdict(int)
for f in os.listdir('genia'):
	if f.endswith('.a2'):
		for line in open('genia/'+f):
			line = line.split()
			if line[1]=='Entity':
				entityW = line[4].split()
				for word in entityW: 
					entityWords[word.lower()]+=1

geniaF = open('geniaEntityWords.txt','w')
for word in entityWords:
	geniaF.write(word+'\n')