from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix

predicted_labels = []
actual_labels = []

#predicted_labels = tuple(open("test_out_baseline_UNK_app", 'r'))

with open("test_out_baseline_UNK_app", "r") as ins:
    for line in ins:
        predicted_labels.append(line.strip("\n"))
ins.close()

with open("test_key_app", "r") as ins:
    for line in ins:
        actual_labels.append(line.strip("\n"))
ins.close()

cm = confusion_matrix(actual_labels,predicted_labels,labels=["I-LOC", "B-ORG", "I-PER", "O", "I-MISC", "B-MISC","I-ORG", "B-LOC", "B-PER"])
print(cm)
