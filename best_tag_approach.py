#!usr/bin/python
from collections import defaultdict
import sys
import re

def convert(infilename, outfilename, showtag=True):
    fout = open(outfilename, 'wa+')
    fin=open(infilename,'r')
    lines=fin.readlines()
    for line in lines:
        #fout.write('\n\n\n')
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

    def UNK(self):
        new = defaultdict(int)
        # change words with freq <5 into unknown words "<UNK>"
        for (word,tag) in self.wordtag:
            new[(word,tag)] = self.wordtag[(word,tag)]
            if self.wordtag[(word,tag)] < 5:
                new[('<UNK>',tag)] += self.wordtag[(word,tag)]
        self.wordtag = new


## baseline model, choosing the tag that maximizes emission probability
class HMM_Baseline(HMM):

    def run_UNK(self):
        self.get_counts()
        self.get_parameters()
        fout = open('test_out_baseline_UNK', 'w')
        best = {}
        # best tag for "<UNK>"
        pivot = 0
        besttag = ''
        for (word,tag) in self.E:
            if word == '<UNK>':
                if self.E[(word,tag)] > pivot:
                    pivot = self.E[(word,tag)]
                    besttag = tag
        best['<UNK>'] = besttag
        #print '<UNK>',besttag
        i = 0 #counter, to visualize progress
        for l in open(self.ftest, 'r'):
            w = l.strip()
            if w:
                if w in best:
                    fout.write(w+'\t'+best[w]+'\n')
                else:
                    pivot = 0
                    besttag = ''
                    if w not in self.words:
                        fout.write(w+'\t'+best['<UNK>']+'\n')
                    else:
                        for (word,tag) in self.E:
                            if word == w:
                                if self.E[(word,tag)] > pivot:
                                    pivot = self.E[(word,tag)]
                                    besttag = tag
                        best[w] = besttag
                        fout.write(w+'\t'+besttag+'\n')
            else:
                fout.write('\n')
            i += 1
            #if i%10000 == 0: 
		#print i
        fout.close()

def main():
    convert('./ENGLISH.test', 'test_key')
    convert('./ENGLISH.test', 'test', False)
    convert('./ENGLISH.train', 'train')
    BL_UNK = HMM_Baseline('train','test')
    BL_UNK.run_UNK()
    evaluate('test_out_baseline_UNK','test_key')

if __name__=="__main__":
        main()
