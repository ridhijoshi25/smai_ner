import numpy as np
from sklearn import ensemble
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
import os,csv
import sys
import random

if __name__ == "__main__":

	traindata = np.genfromtxt("aij-wikiner-en-wp2_train.data", delimiter = ' ',skip_header=False)
	testdata = np.genfromtxt("aij-wikiner-en-wp2_test.data", delimiter = ' ',skip_header=False)
	print "Data Loading Completed :P"
	trainlabels = np.genfromtxt("aij-wikiner-en-wp2_train.labels", delimiter = ' ',skip_header=False)
	testlabels = np.genfromtxt("aij-wikiner-en-wp2_test.labels", delimiter = ' ',skip_header=False)
	print "Label Loading Completed :P"
	'''print labels
	print traindata
	f = open('aij-wikiner-en-wp2.data', 'r')
	lenflines = f.readlines()
	lenf = len(lenflines)'''
	lentest = len(testlabels)
	#print lentest
	
	#print traindata

	#print len(test)
	#print len(train)
	#print trainlabels
	#print testdata
	#print testlabels
	#print len(test_label_actual)
	#print "----------------------------------"
	train=[]
	for line in traindata:
		train.append(line)
	test=[]
	for line in testdata:
		test.append(line)

	trainLabels=[]
	for line in trainlabels:
		trainLabels.append(line)
	testLabels=[]
	for line in testlabels:
		testLabels.append(line)
	print "Loading Completed :)"

	clf = SVC(kernel='rbf', C = 1.0)
	clf.fit(train,trainLabels) 
	print "Classification Completed :)"
	
	test_label=[]
	test_label=clf.predict(testdata)
	print test_label	
	print len(test_label)
	print "Classification Completed :)"
	Labels=set(testLabels)
	Labs=[]
	for i in Labels:
		Labs.append(i)
	cm = confusion_matrix(testLabels, test_label, labels=Labs)
	np.set_printoptions(precision=2)
	
	print 'Confusion matrix'
	print(cm)
	'''for i in range(len(cm)):
		TP=0.0
		TN=0.0
		FP=0.0
		FN=0.0
		for j in range(len(cm)):
			for k in range(len(cm)):
				if(j == k and i == k):
					TP=TP+cm[j][k]
				elif(i == j):
					FP=FP+cm[j][k]
				elif(i == k):
					FN = FN+cm[j][k]
		acc= ((lentest-FP-FN)*100)/lentest;
		print "Accuracy of class",
		print labels[i],
		print acc
	print "Done :P"'''
	totCorrect=0
	for i in range(len(cm)):
		for j in range(len(cm)):
			if(i == j):
				totCorrect=totCorrect+cm[i][j]
	acc= (totCorrect*100)/lentest;
	print "Accuracy of class",acc
