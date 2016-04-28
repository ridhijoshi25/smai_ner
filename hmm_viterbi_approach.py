#!usr/bin/python
from collections import defaultdict
import sys
import re

def convert(infilename, outfilename, showtag=True):
    fout = open(outfilename, 'wa+')
    fin=open(infilename,'r')
    lines=fin.readlines()
    for line in lines:
        fout.write('\n\n\n')
	#print "Hello"
        #line = line.strip()
        pairs = line.strip().split(' ')
        for pair in pairs:
	 #   print pair
            temp = pair.split('|')
            if len(temp) == 3:
	#	print "Word" 
                word = temp[0]
                tag = temp[2]
                if showtag == True:
                    fout.write(word+'\t'+tag+'\n')
                else:
                    fout.write(word+'\n')
    fout.close()

def evaluate(resultFile, keyFile):
    correct = 0
    n = 0
    fkey = open(keyFile,'r')
    for l in open(resultFile,'r'):
        n += 1
        if l.strip('\n') == fkey.readline().strip('\n'):
            correct += 1
    fkey.close()
    print (float(correct)/n )* 100

class HMM():

    def __init__(self, trainFileName, testFileName):
        self.ftrain = trainFileName
        self.ftest = testFileName

    def get_counts(self): # get counts for deriving parameters
        self.wordtag = defaultdict(int) # emission freqs
        self.unitag = defaultdict(int) # unigram freqs of tags
        self.bitag = defaultdict(int) # bigram freqs of tags
        self.tritag = defaultdict(int) # trigram freqs of tags
        
        tag_penult = ''
        tag_last = ''
        tag_current = ''
        
        for l in open(self.ftrain, 'r'):
            l = l.strip()
            if not l:
                tag_penult = tag_last
                tag_last = tag_current
                tag_current = ''
                # update sentence boundary case
                if tag_last != '' and tag_penult != '':
                    # update bitag freqs
                    self.bitag[(tag_last, tag_current)] += 1
                    # update tritag freqs
                    self.tritag[(tag_penult, tag_last, tag_current)] += 1
            else:
                word, tag = l.split('\t')
                tag_penult = tag_last
                tag_last = tag_current
                tag_current = tag
                # update emission freqs
                self.wordtag[(word,tag)] += 1
                # update unitag freqs
                self.unitag[tag] += 1
                # update bitag freqs
                self.bitag[(tag_last, tag_current)] += 1
                # update tritag freqs
                self.tritag[(tag_penult, tag_last, tag_current)] += 1
                # update starting bigrams
                if tag_last == '' and tag_penult == '':
                    self.bitag[('','')] += 1

    def get_e(self,word,tag):
        return float(self.wordtag[(word,tag)])/self.unitag[tag]

    def get_q(self,tag_penult, tag_last, tag_current):
        return float(self.tritag[(tag_penult, tag_last, tag_current)])/self.bitag[(tag_penult, tag_last)]

    def get_parameters(self, method='UNK'): # derive parameters from counts
        self.words = set([key[0] for key in self.wordtag.keys()])
        if method == 'UNK':
            self.UNK()
        self.words = set([key[0] for key in self.wordtag.keys()])
        self.tags = set(self.unitag.keys())
        self.E = defaultdict(int)
        self.Q = defaultdict(int)
        for (word,tag) in self.wordtag:
            self.E[(word,tag)] = self.get_e(word,tag)
        for (tag_penult, tag_last, tag_current) in self.tritag:
            self.Q[(tag_penult, tag_last, tag_current)] = self.get_q(tag_penult, tag_last, tag_current)

    def tagger(self, outFileName, method='UNK'):
        # train
        self.get_counts()
        self.get_parameters(method)
        # begin tagging
        self.sent = []
        fout = open(outFileName, 'w')
	count=0
	counter=0
	insidesent=0
	insidenotl=0
	elseinside=0
	outl=0
        for l in open(self.ftest, 'r'):
            l = l.strip()
	    count=count+1
            if not l:
		#print l
		insidenotl=insidenotl+1
                if self.sent:
           #         print "generate path for "+str(self.sent)+'\n'
		    insidesent=insidesent+len(self.sent)
                    path = self.viterbi(self.sent, method)
                 #   print path
                    for i in range(len(self.sent)):
			counter=counter+1
                        fout.write(self.sent[i]+'\t'+path[i]+'\n')
                    self.sent = []
		else:
			elseinside=elseinside+1
			#fout.write('word+tag\n')
                fout.write('\n')
            else:
		outl=outl+1
		#fout.write('word+tag\n')
                self.sent.append(l)
	print count,counter,insidenotl,insidesent,elseinside,outl
        fout.close()

    def viterbi(self,sent,method='UNK'):
	#print sent
        V = {}
        path = {}
        # init
        V[0,'',''] = 1
        path['',''] = []
        # run
        #sys.stderr.write("entering k loop\n")
        for k in range(1,len(sent)+1):
            temp_path = {}
            word = self.get_word(sent,k-1)
            ## handling unknown words in test set using low freq words in training set
            if word not in self.words:
             #   print word
                if method=='UNK':
                    word = '<UNK>'
            #sys.stderr.write("entering u loop "+str(k)+"\n")
            for u in self.get_possible_tags(k-1):
                #sys.stderr.write("entering v loop "+str(u)+"\n")
                for v in self.get_possible_tags(k):
                    V[k,u,v],prev_w = max([(V[k-1,w,u] * self.Q[w,u,v] * self.E[word,v],w) for w in self.get_possible_tags(k-2)])
                    temp_path[u,v] = path[prev_w,u] + [v]
            path = temp_path
        # last step
        prob,umax,vmax = max([(V[len(sent),u,v] * self.Q[u,v,''],u,v) for u in self.tags for v in self.tags])
        return path[umax,vmax]

    def get_possible_tags(self,k):
        if k == -1:
            return set([''])
        if k == 0:
            return set([''])
        else:
            return self.tags

    def get_word(self,sent,k):
        if k < 0:
            return ''
        else:
            return sent[k]

    def UNK(self):
        new = defaultdict(int)
        # change words with freq <5 into unknown words "<UNK>"
        for (word,tag) in self.wordtag:
            new[(word,tag)] = self.wordtag[(word,tag)]
            if self.wordtag[(word,tag)] < 5:
                new[('<UNK>',tag)] += self.wordtag[(word,tag)]
        self.wordtag = new


def main():
    convert('./ENGLISH.test', 'test_key')
    convert('./ENGLISH.test', 'test', False)
    convert('./ENGLISH.train', 'train')
    unk = HMM('train', 'test')
    unk.tagger('test_out_unk','UNK')
    evaluate('test_out_unk','test_key')

if __name__=="__main__":
        main()
