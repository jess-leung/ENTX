import os 

count = 0 
for f in os.listdir('Dataset/Training copy'):
	if f.endswith('.txt'):
		baseFilename = f[:-4]
		print baseFilename
		termIDS = []
		termsThatWeShouldHave = [] 
		for line in open('Dataset/Training copy/'+f):
			line = line.split()
			if len(line)>0:
				terms = line[0].split(',')
				for term in terms:
					if term != 'O':
						if int(term[1:]) not in termIDS:
							termIDS.append(int(term[1:]))


		for line in open('Dataset/Training/'+baseFilename+'.ann'):
			line = line.split()
			if line[0][0]=='T':
				termsThatWeShouldHave.append(int(line[0][1:]))


		for term in termsThatWeShouldHave:
			if term not in termIDS:
				print baseFilename
				print term
				count=count+1
print count

