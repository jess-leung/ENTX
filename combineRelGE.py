import os 
from collections import defaultdict 

""" This file combines the rel and GE event extraction annotation files and creates a .ann for brat visualisation as well."""

# countRelsInOrig = 0 

# for f in os.listdir('Dataset/Training'):
#     if f.endswith('.ann'):
#         thisFile = open('Dataset/Training/'+f,'r')
#         geniaFile = open('Dataset/GE-Training/'+ff+'.ann','r')

#         #parse genia file to generate offsets dictionary
#         dictOfOffsets = defaultdict() 
#         dictOfOffsetsR = defaultdict()
#         rels = defaultdict() 
#         entityDict = defaultdict()
#         relNo = 1
#         lastTerm = 0 

#         for line in geniaFile.readlines(): 
#             line = line.split()
#             if line[0][0]=='T': 
#                 dictOfOffsets[(line[2],line[3])]=line[0]
#                 lastTerm = int(line[0][1:])+1

#         for line in thisFile.readlines(): 
#             line = line.split()
#             print line
#             if line[0][0]=='T':
#                 dictOfOffsetsR[line[0]]=(line[2],line[3])
#                 entityDict[line[0]]=(line[1],line[2],line[3],line[4:])
#             elif line[0][0]=='R':
#                 rels[(line[2][5:],line[3][5:])]=line[1]
               
#         thisFile.close()
#         geniaFile.close()

#         thisFile = open('Dataset/Training/'+f,'a+')
#         geniaFile = open('Dataset/GE-Training/'+f,'a+')

#         firstWrite=True
#         for rel,t in rels.iteritems(): 
#             thisTerm = rel[1]
#             #lookup this term to get offset scores
#             thisOffset = dictOfOffsetsR[thisTerm]
#             if thisOffset in dictOfOffsets:
#                 actualTerm = dictOfOffsets[thisOffset]
#                 geniaFile.write('R'+str(relNo)+'\t'+t+' Arg1:'+rel[0]+' Arg2:'+actualTerm+'\n')
#                 relNo+=1
#                 countRelsInOrig+=1
#             else: 
#                 if firstWrite==True: 
#                     geniaFile.write('\n')
#                     firstWrite=False
#                 geniaFile.write('T'+str(lastTerm)+'\tEntity'+' '+entityDict[thisTerm][1]+' '+entityDict[thisTerm][2]+'\t'+' '.join(entityDict[thisTerm][3])+'\n')
#                 dictOfOffsets[(entityDict[thisTerm][1],entityDict[thisTerm][2])]='T'+str(lastTerm)
#                 geniaFile.write('R'+str(relNo)+'\t'+t+'  Arg1:'+rel[0]+' Arg2:T'+str(lastTerm)+'\n')
#                 relNo+=1
#                 lastTerm+=1
#                 countRelsInOrig+=1

#         thisFile.close()
#         geniaFile.close() 
# print countRelsInOrig
statistics = defaultdict(lambda: defaultdict(int))
total = 0
totalRels = 0
totalEvents = defaultdict(int)
for f in os.listdir('Dataset/GE-Training'):
    if f.endswith('.ann'):
        # TIME TO GET STATS! 
        thisFile = open('Dataset/GE-Training/'+f,'r')
        events = []
        rels = []
        # statistics dictionary 
        # { Binding: { 
        #       Subunit-complex:10, Protein-Component:1 
        #       }
        # }
        for line in thisFile: 
            line = line.split()
            eventPart = []
            theme1=''
            theme2=''
            relType=''
            arg1=''
            arg2=''
            # rels=[]
            if len(line)>0:
                if line[0][0]=='E':
                    eventPart = line[1].split(':')
                    theme1 = line[2].split(':')[1]
                    if len(line)>3: 
                        theme2 = line[3].split(':')[1]
                    events.append((theme1,theme2,eventPart[0]))
                if line[0][0]=='R':
                    relType=line[1].strip()
                    arg1=line[2].split(':')[1]
                    arg2=line[3].split(':')[1]
                    rels.append((arg1,arg2,relType))

        # totalRels+=len(rels)
        for rel in rels: 
            totalRels+=1
            for event in events: 
                # totalEvents[event[2]]+=1
                if rel[0]==event[0] or rel[0]==event[1]:
                    statistics[event[2]][rel[2]]+=1
                    total+=1

        for event in events: 
            totalEvents[event[2]]+=1
            
        thisFile.close()

print statistics
print totalEvents
print total
print totalRels




