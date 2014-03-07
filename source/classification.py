#coding:utf-8
import os, sys
import timeit
import numpy, math
import matplotlib.pylab as pylab
from subprocess import *
import timeit
import common_functions


################################################
# Parameters 
################################################
# define the default parameters
train = "DR1"
test = "DR2"
lesions = ["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares"]
techniquesLow = ["sparse","dense"]
techniquesMid = ["hard","semi","soft"]
plot = False
SVM = "./ext/svm/"

# ShowOptions function
def showOptions():
	print "-h \t\t show options"
	print "-train \t\t define training dataset"
	print "-test \t\t define test dataset"
	print "-l \t\t define a specific DR-related lesion"
	print "-low \t\t define a specific low-level technique"
	print "-mid \t\t define a specific mid-level technique"
	print "-plot \t\t use this parameter to plot the ROC curves"
	print "-svm \t define the path to SVM"
	quit()

# take the parameters
if len(sys.argv) > 1:		
	for i in range(1, len(sys.argv),2):
		op = sys.argv[i]
		if op == "-h": showOptions()
		elif op == "-train": train = sys.argv[i+1]
		elif op == "-test": test = sys.argv[i+1]
		elif op == "-l": lesions = [sys.argv[i+1]]
		elif op == "-low": techniquesLow = [sys.argv[i+1]]
		elif op == "-mid": techniquesMid = [sys.argv[i+1]]
		elif op == "-plot": plot = True
		elif op == "-svm": SVM = sys.argv[i+1]
################################################


################################################
# create directories
################################################
directory = "classification/"
for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		if not os.path.exists(directory + techniqueLow + "/" + techniqueMid + "/"):
			os.makedirs(directory + techniqueLow + "/" + techniqueMid + "/")
if not os.path.exists(directory + "plots/"):
	os.makedirs(directory + "plots/")
################################################


################################################
# Additional functions
################################################
def SVMformat(fileIn, fileOut):
	histogramsIn = open(fileIn).readlines()
	fileOut = open(fileOut,"wb")
	
	for histogram in histogramsIn:
		i = 1
		histogram = histogram.split()
		histogramOut = histogram[0] + " "
		for h in histogram[1:]:
			histogramOut += str(i) + ":" + h + " "
			i += 1
		fileOut.write(histogramOut + "\n")
	fileOut.close()
	
	
def plotRocCurves(lesion, lesion_en):
	file_legend = []
	for techniqueMid in techniquesMid:
		for techniqueLow in techniquesLow:
			file_legend.append((directory + techniqueLow + "/" + techniqueMid + "/operating-points-" + lesion + "-scale.dat", "Low-level: " + techniqueLow + ". Mid-level: " + techniqueMid + "."))
			
			pylab.clf()
			pylab.figure(1)
			pylab.xlabel('1 - Specificity', fontsize=12)
			pylab.ylabel('Sensitivity', fontsize=12)
			pylab.title(lesion_en)
			pylab.grid(True, which='both')
			pylab.xticks([i/10.0 for i in range(1,11)])
			pylab.yticks([i/10.0 for i in range(0,11)])
			#pylab.tick_params(axis="both", labelsize=15)
			
			for file, legend in file_legend:
				points = open(file,"rb").readlines()
				x = [float(p.split()[0]) for p in points]
				y = [float(p.split()[1]) for p in points]
				x.append(0.0)
				y.append(0.0)
				
				auc = numpy.trapz(y, x) * -100

				pylab.grid()
				pylab.plot(x, y, '-', linewidth = 1.5, label = legend + u" (AUC = {0:0.1f}%)".format(auc))

	pylab.legend(loc = 4, borderaxespad=0.4, prop={'size':12})
	pylab.savefig(directory + "plots/" + lesion + ".pdf", format='pdf')
	
	

def checkSensSpec(shift, d):
	neg = open(d + "resultNegative-" + lesion + ".dat","rb").readlines()
	pos = open(d + "resultPositive-" + lesion + ".dat","rb").readlines()
	neg = [ float(d[:-1]) for d in neg ]
	pos = [ float(d[:-1]) for d in pos ]
	acertosPos = 0
	acertosNeg = 0
	for p in pos:
		if p - shift >= 0:
     			acertosPos += 1
     		#print p, p - shift
	for n in neg:
		if n - shift < 0:
			acertosNeg += 1
		#print n, n - shift
	sens = acertosPos/float(len(pos))
	spec = acertosNeg/float(len(neg))
	return "Sensitivity = {0:0.1f}%".format(sens*100) + "\n" + "Specificity = {0:0.1f}%".format(spec*100)	
################################################



################################################
# MAIN
################################################
en = dict(zip(["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"], ["Hard Exudates","Superficial Hemorrhages","Deep Hemorrhages","Red Lesions","Cotton-wool Spots","Drusen","Normal Images"]))

AUCs = open(directory + "AUC.txt","wb")

for lesion in lesions:
	lesion_en = en[lesion]
	for techniqueMid in techniquesMid:
		for techniqueLow in techniquesLow:
		
			start = timeit.default_timer()
			print "Learning a classifier for " + lesion_en + "\nLow-level: " + techniqueLow + "\nMid-level: " + techniqueMid
			AUCs.write("Learning a classifier for " + lesion_en + "\nLow-level: " + techniqueLow + "\nMid-level: " + techniqueMid)
			
			# prepare the positive training images
			if train == "DR2" and (lesion == "hemorragia-superficial" or lesion == "hemorragia-profunda"):
				positiveTrainingList = os.listdir("datasets/" + train + "-images-by-lesions/Red Lesions")
			else:
				positiveTrainingList = os.listdir("datasets/" + train + "-images-by-lesions/" + lesion_en)
			positiveTraining = [ open("mid-level/" + techniqueLow + "/" + train + "/" + techniqueMid + "/" + lesion + "/" + histogram[:-3] + "hist","rb").readline() for histogram in positiveTrainingList ]
						
			# prepare the negative training images
			negativeTrainingList = os.listdir("datasets/" + train + "-images-by-lesions/Normal Images")
			negativeTraining = [ open("mid-level/" + techniqueLow + "/" + train + "/" + techniqueMid + "/" + lesion + "/" + histogram[:-3] + "hist","rb").readline() for histogram in negativeTrainingList ]
						
			# prepare the positive test images
			if test == "DR2" and (lesion == "hemorragia-superficial" or lesion == "hemorragia-profunda"):
				positiveTestList = os.listdir("datasets/" + test + "-images-by-lesions/Red Lesions")
			else:
				positiveTestList = os.listdir("datasets/" + test + "-images-by-lesions/" + lesion_en)
			positiveTest = [ open("mid-level/" + techniqueLow + "/" + test + "/" + techniqueMid + "/" + lesion + "/" + histogram[:-3] + "hist","rb").readline() for histogram in positiveTestList ]
			positiveTestName = directory + techniqueLow + "/" + techniqueMid + "/" + lesion + "-positive-test.hist"
			outFile = open(positiveTestName[:-5] + "-temp.hist","wb")
			for pt in positiveTest:
				outFile.write(pt + "\n")
			outFile.close()
			if techniqueMid == "soft":
				SVMformat(positiveTestName[:-5] + "-temp.hist", positiveTestName)
			else:
				os.system(SVM + "convert " + positiveTestName[:-5] + "-temp.hist > " + positiveTestName)
			
			
			# prepare the negative test images
			negativeTestList = os.listdir("datasets/" + test + "-images-by-lesions/Normal Images")
			negativeTest = [ open("mid-level/" + techniqueLow + "/" + test + "/" + techniqueMid + "/" + lesion + "/" + histogram[:-3] + "hist","rb").readline() for histogram in negativeTestList ]
			negativeTestName = directory + techniqueLow + "/" + techniqueMid + "/" + lesion + "-negative-test.hist"
			outFile = open(negativeTestName[:-5] + "-temp.hist","wb")
			for nt in negativeTest:
				outFile.write(nt + "\n")
			outFile.close()
			if techniqueMid == "soft":
				SVMformat(negativeTestName[:-5] + "-temp.hist", negativeTestName)
			else:
				os.system(SVM + "convert " + negativeTestName[:-5] + "-temp.hist > " + negativeTestName)
			
			
			# concatenate positive and negative training images
			trainingName = directory + techniqueLow + "/" + techniqueMid + "/" + lesion + "-training.hist"
			training = open(trainingName[:-5] + "-temp.hist","wb")
			for nt in negativeTraining: training.write(nt + "\n")
			for pt in positiveTraining: training.write(pt + "\n")
			training.close()
			if techniqueMid == "soft":
				SVMformat(trainingName[:-5] + "-temp.hist", trainingName)
			else:
				os.system(SVM + "convert " + trainingName[:-5] + "-temp.hist > " + trainingName)
			
			
			# define some variables
			resultFileTrain = directory + techniqueLow + "/" + techniqueMid + "/resultTrain-" + lesion + ".dat"
			scaledTraining = trainingName + ".scale"
			model = directory + techniqueLow + "/" + techniqueMid + "/" + lesion + ".model"
			scaledNegativeTest = negativeTestName + ".scale"
			scaledPositiveTest = positiveTestName + ".scale"
			resultFileNegative = directory + techniqueLow + "/" + techniqueMid + "/resultNegative-" + lesion + ".dat"
			resultFilePositive = directory + techniqueLow + "/" + techniqueMid + "/resultPositive-" + lesion + ".dat"
			rangeFile = directory + techniqueLow + "/" + techniqueMid + "/range-" + lesion
			
						
			
			# Scale the training data
			command = SVM + "svm-scale -l -1 -u +1 -s " + rangeFile + " " + trainingName + " > " + scaledTraining
			os.system(command)

			# Escala os dados de teste das normais
			command = SVM + "svm-scale -r " + rangeFile + " " + negativeTestName + " > " + scaledNegativeTest
			os.system(command)
	
			# Escala os dados de teste das doentes
			command = SVM + "svm-scale -r " + rangeFile + " " + positiveTestName + " > " + scaledPositiveTest
			os.system(command)
			
			
			# Run the grid-search
			print('Cross validation...')			
			cmd = '%s -svmtrain "%s" -gnuplot "%s" "%s"' % (SVM + "grid.py", SVM + "svm-train", "/usr/bin/gnuplot", scaledTraining)
			os.system(cmd + "  > tmp/info.txt 2> tmp/errors.txt")
			
			line = open("tmp/info.txt","rb").readlines()
			last_line = line[-1:][0]
			c,g,rate = map(float,last_line.split())
			
			"""
			f = Popen(cmd, shell = True, stdout = PIPE).stdout
			line = ''
			while True:
				last_line = line
				line = f.readline()
				if not line: break
			c,g,rate = map(float,last_line.split())
			"""
			print('Best c=%s, g=%s CV rate=%s' % (c,g,rate))
	
			wnormais = (float(len(positiveTraining)/float(len(positiveTraining) + len(negativeTraining))) * 2.0)
			wdoentes = (2.0 - wnormais)
			#print "negative samples = " + str(len(negativeTraining))
			#print "positive samples = " + str(len(positiveTraining))
			#print "wnormais = " + str(wnormais)
			#print "wdoentes = " + str(wdoentes)

			# Train the classifier
			command = SVM + "svm-train -t 2 -c " + str(c) + " -g " + str(g) + " -w1 " + str(wdoentes) + " -w-1 " + str(wnormais) + " " + scaledTraining + " " + model
			os.system(command + "  > tmp/info.txt 2> tmp/errors.txt")

			# Classify the training images
			command = SVM + "svm-predict " + scaledTraining + " " + model + " " + resultFileTrain
			os.system(command + "  > tmp/info.txt 2> tmp/errors.txt")

			# Classify the negative test images
			command = SVM + "svm-predict " + scaledNegativeTest + " " + model + " " + resultFileNegative
			os.system(command + "  > tmp/info.txt 2> tmp/errors.txt")

			# Classify the positive test images
			command = SVM + "svm-predict " + scaledPositiveTest + " " + model + " " + resultFilePositive
			os.system(command + "  > tmp/info.txt 2> tmp/errors.txt")
			

			
			# Shift the hyperplan
			numberOfPoints = 500
			
			# Record the shifts to allow a future choice of most adequate operating point
			shifts = []
			
			result = open(resultFileTrain,"rb").readlines()
			upperBound = -9999999999
			lowerBound = 9999999999
			for i in result:
				temp = i.split("\n")
				res = float(temp[0])
				if res > upperBound:	upperBound = res
				if res < lowerBound:	lowerBound = res
			interval = upperBound - lowerBound
			variationFactor = interval/numberOfPoints
			limiar = lowerBound
			
			negativeResults = open(resultFileNegative,"rb").readlines()
			positiveResults = open(resultFilePositive,"rb").readlines()
			
			valuesOut = []
			numero_tics = 0
			while ((limiar <= upperBound) and (numero_tics < numberOfPoints)):
				numero_tics = numero_tics + 1
				acertosNormais = 0
				acertosDoentes = 0
				for i in negativeResults:
					temp = i.split("\n")
					res = float(temp[0])
					if res <= limiar:	acertosNormais = acertosNormais + 1
				for i in positiveResults:
					temp = i.split("\n")
					res = float(temp[0])
					if res > limiar:	acertosDoentes = acertosDoentes + 1
				shifts.append(limiar)
				line = str(acertosNormais) + "\t" + str(acertosDoentes) + "\t\n"
				valuesOut.append(line)
				limiar = limiar + variationFactor
				
			arqout = open(directory + techniqueLow + "/" + techniqueMid + "/operating-points-" + lesion + ".dat","wb")
			arqout.seek(0)
			for i in valuesOut:
				arqout.write(i)
			arqout.close()
			
			
			
			# Scale the operating points and calculate the area under the ROC curve (AUC)
			lines = open(directory + techniqueLow + "/" + techniqueMid + "/operating-points-" + lesion + ".dat", "rb").readlines()

			max_x = -9999999999.0
			max_y = -9999999999.0

			for line in lines:
				line = line.split()
				x = float(line[0])
				y = float(line[1])
				if (x > max_x):	max_x = x
				if (y > max_y):	max_y = y
		
			x = []
			y = []
			last_x = -1
			last_y = -1
			operatingPointsFile = open(directory + techniqueLow + "/" + techniqueMid + "/operating-points-" + lesion + "-scale.dat", "wb")
			finalShifts = []
			indShifts = 0
			sensitivitySpecicificity = []
			
			for line in lines:
				line = line.split()
				xx = 1 - float(line[0])/float(max_x)
				yy = float(line[1])/float(max_y)
				if xx != last_x or yy != last_y:
					x.append(xx)
					y.append(yy)
					last_x = xx
					last_y = yy
					operatingPointsFile.write(str(xx) + "\t" + str(yy) + "\n")
					finalShifts.append(shifts[indShifts])
					sensitivitySpecicificity.append(("{0:0.1f}%".format(yy*100), "{0:0.1f}%".format((1-xx)*100)))
				indShifts += 1
					
					
			#for i in range(len(finalShifts)):
			#	print finalShifts[i], "\t(" + sensitivitySpecicificity[i][0] + ", " + sensitivitySpecicificity[i][1] + ")"
			#shift_user = raw_input('Enter the desired shift!: ')
			#print "You have the following results: \n" + checkSensSpec(float(shift_user))
				
							
			#if last_x != 0.0 and last_y != 0.0:
			#	operatingPointsFile.write("0.0\t0.0\n")
			operatingPointsFile.close()
			
			stop = timeit.default_timer()
			print "Model created in " + common_functions.convertTime(stop - start)
			
			auc = numpy.trapz(y, x) * -100
			print u"AUC = {0:0.1f}%\n\n".format(auc)
			AUCs.write(u"\nAUC = {0:0.1f}%\n\n".format(auc))
			
			
			# Clear
			os.system("rm " + lesion + "-training.hist.scale.png " + lesion + "-training.hist.scale.out")
			
			
	# Plot the ROC curves
	if plot:
		plotRocCurves(lesion, lesion_en)
			
AUCs.close()
################################################
