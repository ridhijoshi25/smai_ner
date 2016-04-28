#!/usr/bin/python
import sys
import re
from gensim import utils
from gensim.models.doc2vec import LabeledSentence
from gensim.models import word2vec

name_tag_list=[]
name_tag_set=[]	
name_tag_dict={}
#fo = open("foo.txt", "rw+")
word_numeric_list=[]

model = word2vec.Word2Vec('/home/anamika/GoogleNews-vectors-negative300.bin', size=300)

model = word2vec.Word2Vec.load_word2vec_format('/home/anamika/GoogleNews-vectors-negative300.bin', binary=True)

for line in open("aij-wikiner-en-wp2","r").readlines():
	strs = re.sub(r'\s', ' ', line).split(' ')
	for values in strs:
		if(values.strip() == ''):
			continue
		word,pos_tag,name_entity_tag=values.split('|')
		#print word,
		temp =[]
		'''print pos_tag,
		print name_entity_tag'''
		if word not in model:
			for i in range(300):
    				temp.append(0)
		else:
			temp=model[word]
		word_numeric_list.append(temp)
		name_tag_list.append(name_entity_tag)
		#print len(temp)

name_tag_set=set(name_tag_list)
print name_tag_set
print len(word_numeric_list[0])
i=0
for tag in name_tag_set:
	name_tag_dict[tag]=i
	i=i+1
#--------------------Write Feature Matrix--------------------
fout=open('aij-wikiner-en-wp2.data','w')
for f in word_numeric_list:
	line=""
	for i in range(len(f)-1):
		line=line+str(f[i])+" "
	line=line+str(f[i])
	fout.write(line+"\n")
fout.close()

#--------------------Write Labels--------------------
fout=open('aij-wikiner-en-wp2.labels','w')
for f in name_tag_list:
	line=str(name_tag_dict[f])
	fout.write(line+"\n")
fout.close()
