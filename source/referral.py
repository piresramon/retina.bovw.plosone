#coding:utf-8
import os, sys
import timeit
import numpy as np
import math
import matplotlib.pylab as pylab
from subprocess import *
import timeit
import common_functions


################################################
# Parameters 
################################################
# define the default parameters
image = "IM000243.pgm"
lesions = ["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares"]
techniquesLow = ["sparse","dense"]
techniquesMid = ["hard","semi","soft"]
plot = False
SVM = "./ext/svm/"

# ShowOptions function
def showOptions():
	print "-h : show options"
	print "-low technique : define a specific low-level technique (default [sparse, dense])\n\tsparse -- Sparse low-level feature extraction\n\tdense  -- Dense low-level feature extraction"
	print "-mid technique : define a specific mid-level technique (default [hard, semi, soft])\n\thard -- Hard-Sum coding/pooling\n\tsemi -- Semi-Soft-Sum coding/pooling\n\tsoft -- Soft-Max coding/pooling"
	print "-svm path : define the path to the svm algorithm (default ./ext/svm/)"
	print "-plot : use this parameter to plot the ROC curves (default False)"
	quit()

# take the parameters
if len(sys.argv) > 1:		
	for i in range(1, len(sys.argv),2):
		op = sys.argv[i]
		if op == "-h": showOptions()
		elif op == "-low": techniquesLow = [sys.argv[i+1]]
		elif op == "-mid": techniquesMid = [sys.argv[i+1]]
		elif op == "-plot": plot = True
		elif op == "-svm": SVM = sys.argv[i+1]
################################################



################################################
# Request Operating Points 
################################################
def requestOperatingPoints(techniqueLow, techniqueMid):
	# List to maintain the shifts defined by the user
	offsets = []
	for lesion in lesions:

		lesion_en = en[lesion]
					
		# Request the operating points for each lesion
		shiftsSensSpecs = open("classification/" + techniqueLow + "/" + techniqueMid + "/shifts-sens-spec-" + lesion + ".dat", "rb").readlines()
		i = 1
		print "Low-level: " + techniqueLow + "\t Mid-level: " + techniqueMid
		print "-----------------------------------------"
		print "|\t    " + lesion_en
		print "-----------------------------------------\n|   id\t|   Sensitivity\t|   Specificity\t|\n-----------------------------------------"
		for shiftSensSpec in shiftsSensSpecs:
			shift, sens, spec = shiftSensSpec.split()
			print "|   " + str(i) + "\t|   " + sens + "\t|   " + spec + "\t|"
			i = i+1
		print "-----------------------------------------"
	
		id_user = raw_input('Enter the desired pair sensitivity/specificity (id) for ' + lesion_en + ': ')
		offset_user = shiftsSensSpecs[int(id_user) - 1].split()[0]
	
		offsets.append(offset_user)
	return offsets
################################################



################################################
# Classify all images labeled as referable or non-referable
################################################
def classifyAllImages(listImagesPos, listImagesNeg, techniqueLow, techniqueMid, directory):
	l = listImagesPos + listImagesNeg
	for image in l:
		image = image.split('.')[0] + ".txt"
		
		for lesion in lesions:
			if not os.path.exists(directory + lesion + "/"):
				os.makedirs(directory + lesion + "/")
			if os.path.exists(directory + lesion + "/" + image) and os.path.getsize(directory + lesion + "/" + image) > 0: continue
			resultName = "result-" + techniqueLow + "-" + techniqueMid + "-" + lesion + "-" + image
			command  = "python classify_image.py -i " + image + " -l " + lesion + " -low " + techniqueLow + " -mid " + techniqueMid + " -o 0"
			os.system(command + "  > tmp/info-referral.txt 2> tmp/errors.txt")
			os.system("mv " + resultName + " " + directory + lesion + "/" + image)
################################################



################################################
# Create the feature vectors: referral/histogram-negative.txt and referral/histogram-positive.txt
################################################
def createFeatureVectors(techniqueLow, techniqueMid, listImagesPos, listImagesNeg, offsets):
	posFile = open("referral/histogram-positive-" + techniqueLow + "-" + techniqueMid + ".txt","wb")
	negFile = open("referral/histogram-negative-" + techniqueLow + "-" + techniqueMid + ".txt","wb")

	for image in listImagesPos:
		image = image.split('.')[0] + ".txt"
		i = 0
		hist = "+1 "
		for lesion in lesions:
			#command  = "python classify_image.py -i " + image + " -l " + lesion + " -low " + techniqueLow + " -mid " + techniqueMid + " -o " + offsets[i]
			#os.system(command + "  > tmp/info-referral.txt 2> tmp/errors.txt")
			score = open("referral/scores/" + techniqueLow + "/" + techniqueMid + "/" + lesion + "/" + image,"rb").readline()
			hist = hist + str(i+1) + ":" + str(float(score) - float(offsets[i])) + " "
			i = i + 1
		posFile.write(hist + "\n")
	posFile.close()
		
	
	for image in listImagesNeg:
		image = image.split('.')[0] + ".txt"
		i = 0
		hist = "-1 "
		for lesion in lesions:
			#command  = "python classify_image.py -i " + image + " -l " + lesion + " -low " + techniqueLow + " -mid " + techniqueMid + " -o " + offsets[i]
			#os.system(command + "  > tmp/info-referral.txt 2> tmp/errors.txt")
			score = open("referral/scores/" + techniqueLow + "/" + techniqueMid + "/" + lesion + "/" + image,"rb").readline()
			hist = hist + str(i+1) + ":" + str(float(score) - float(offsets[i])) + " "
			i = i + 1
		negFile.write(hist + "\n")
	negFile.close()
################################################




################################################
# Classify for need for referral in one year
################################################
def classification(trainingName, positiveTestName, negativeTestName, cod, lenPositiveTraining, lenNegativeTraining, techniqueLow, techniqueMid):
	#AUCs = open("referral/AUCs.txt","wb")
	directory = "referral/" + techniqueLow + "/" + techniqueMid + "/classification/"
	start = timeit.default_timer()

	# define some variables
	
	resultFileTrain = directory + "/resultTrain.dat"
	scaledTraining = trainingName + ".scale"
	model = directory + "/referral-" + cod + ".model"
	scaledNegativeTest = negativeTestName + ".scale"
	scaledPositiveTest = positiveTestName + ".scale"
	resultFileNegative = directory + "/resultNegative" + cod + ".dat"
	resultFilePositive = directory + "/resultPositive" + cod + ".dat"
	rangeFile = directory + "/range-" + cod

	

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
	os.system(cmd + "  > tmp/info-referral-" + techniqueLow + "-" + techniqueMid + "-" + cod + ".txt 2> tmp/errors.txt")

	line = open("tmp/info-referral-" + techniqueLow + "-" + techniqueMid + "-" + cod + ".txt","rb").readlines()
	last_line = line[-1:][0]
	c,g,rate = map(float,last_line.split())


	print('Best c=%s, g=%s CV rate=%s' % (c,g,rate))

	wnormais = (float(lenPositiveTraining/float(lenPositiveTraining + lenNegativeTraining)) * 2.0)
	wdoentes = (2.0 - wnormais)


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

	# Record the offsets to allow a future choice of most adequate operating point
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

	arqout = open(directory + "/operating-points-" + cod + ".dat","wb")
	arqout.seek(0)
	for i in valuesOut:
		arqout.write(i)
	arqout.close()



	# Scale the operating points and calculate the area under the ROC curve (AUC)
	lines = open(directory + "/operating-points-" + cod + ".dat", "rb").readlines()

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
	operatingPointsFile = open(directory + "/operating-points-" + cod + "-scale.dat", "wb")
	shiftsSensSpec = []
	shiftsSensSpecFile = open(directory + "/shifts-sens-spec-" + cod + ".dat", "wb")
	indShifts = 0

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
			if xx <= 0.5 and yy > 0.5:
				shiftsSensSpec.append((str(shifts[indShifts]), " {0:0.1f}%".format(yy*100), " {0:0.1f}%".format((1-xx)*100)))
		indShifts += 1
	operatingPointsFile.close()


	sens_aux = ""
	(last_shift, last_sens, last_spec) = shiftsSensSpec[0]
	for (shift, sens, spec) in shiftsSensSpec[1:]:
		if sens != last_sens:
			shiftsSensSpecFile.write(last_shift + " " + last_sens + " " + last_spec + "\n")
			if spec == " 100.0%": break
		last_shift = shift
		last_sens = sens
		last_spec = spec
	shiftsSensSpecFile.write(shift + " " + sens + " " + spec + "\n")
	shiftsSensSpecFile.close()
	
	
	stop = timeit.default_timer()
	print "Model created in " + common_functions.convertTime(stop - start)

	auc = np.trapz(y, x) * -100
	print u"AUC = {0:0.1f}%\n\n".format(auc)
	#AUCs.write(u"\nAUC = {0:0.1f}%\n\n".format(auc))


	# Clear
	name = trainingName.split("/")[-1:][0]
	if os.path.exists(name + ".scale.png"):
		os.system("rm " + name + ".scale.png")
	if os.path.exists(name + ".scale.out"):
		os.system("rm " + name + ".scale.out")

		
	return u"\nAUC = {0:0.1f}%\n\n".format(auc)
################################################



################################################
# Plot
################################################
def plotRocCurves(file_legend):
	pylab.clf()
	pylab.figure(1)
	pylab.xlabel('1 - Specificity', fontsize=12)
	pylab.ylabel('Sensitivity', fontsize=12)
	pylab.title("Need for Referral")
	pylab.grid(True, which='both')
	pylab.xticks([i/10.0 for i in range(1,11)])
	pylab.yticks([i/10.0 for i in range(0,11)])
	pylab.tick_params(axis="both", labelsize=15)

	for file, legend in file_legend:
		points = open(file,"rb").readlines()
		x = [float(p.split()[0]) for p in points]
		y = [float(p.split()[1]) for p in points]
		dev = [float(p.split()[2]) for p in points]
		x = [0.0] + x
		y = [0.0] + y
		dev = [0.0] + dev
	
		auc = np.trapz(y, x) * 100
		aucDev = np.trapz(dev, x) * 100

		pylab.grid()
		pylab.errorbar(x, y, yerr = dev, fmt='-')
		pylab.plot(x, y, '-', linewidth = 1.5, label = legend + u" (AUC = {0:0.1f}% \xb1 {1:0.1f}%)".format(auc,aucDev))

	pylab.legend(loc = 4, borderaxespad=0.4, prop={'size':12})
	pylab.savefig("referral/referral-curves.pdf", format='pdf')
################################################



################################################
# MAIN
################################################
en = dict(zip(["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"], ["Hard Exudates","Superficial Hemorrhages","Deep Hemorrhages","Red Lesions","Cotton-wool Spots","Drusen","Normal Images"]))

listImagesPos = os.listdir("datasets/DR2-images-by-referral/positive/")
listImagesNeg = os.listdir("datasets/DR2-images-by-referral/negative/")
		

# Request the operating points for each lesion
i = 0
offsets_list = []
for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		directory = "referral/" + techniqueLow + "/" + techniqueMid + "/classification/"
		if not os.path.exists(directory):
			os.makedirs(directory)
			
		if not os.path.exists("referral/histogram-negative-" + techniqueLow + "-" + techniqueMid + ".txt") and not os.path.exists("referral/histogram-positive-" + techniqueLow + "-" + techniqueMid + ".txt"):			
			offsets = requestOperatingPoints(techniqueLow, techniqueMid)
			offsets_list.append(offsets)
			i = i + 1



# Create two files with the feature vectors (positive and negative)
i = 0
for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		directory = "referral/scores/" + techniqueLow + "/" + techniqueMid + "/"
		if not os.path.exists(directory):
			os.makedirs(directory)
		classifyAllImages(listImagesPos, listImagesNeg, techniqueLow, techniqueMid, directory)
			
		if not os.path.exists("referral/histogram-negative-" + techniqueLow + "-" + techniqueMid + ".txt") and not os.path.exists("referral/histogram-positive-" + techniqueLow + "-" + techniqueMid + ".txt"):
			createFeatureVectors(techniqueLow, techniqueMid, listImagesPos, listImagesNeg, offsets_list[i])
			i = i + 1



# Organize the feature vectors according to the 5x2-folds cross-validation protocol
for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		for i in range(1, 6):
			fold = np.arange(len(listImagesPos))
			np.random.shuffle(fold)
			fold1_pos = np.sort(fold[:len(listImagesPos)/2])
			fold2_pos = np.sort(fold[len(listImagesPos)/2:])
	
			fold = np.arange(len(listImagesNeg))
			np.random.shuffle(fold)
			fold1_neg = np.sort(fold[:len(listImagesNeg)/2])
			fold2_neg = np.sort(fold[len(listImagesNeg)/2:])
	
			# Load the feature vectors
			featureVectorPos = open("referral/histogram-positive-" + techniqueLow + "-" + techniqueMid + ".txt","rb").readlines()
			featureVectorNeg = open("referral/histogram-negative-" + techniqueLow + "-" + techniqueMid + ".txt","rb").readlines()
	
			# Create separated files for each fold
			fold1FilePos = open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-1.hist","wb")
			fold2FilePos = open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-2.hist","wb")
			fold1FileNeg = open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-negative-1.hist","wb")
			fold2FileNeg = open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-negative-2.hist","wb")
			fold1FilePosNeg = open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-negative-1.hist","wb")
			fold2FilePosNeg = open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-negative-2.hist","wb")
	
			for ind in fold1_pos:
				fold1FilePos.write(featureVectorPos[ind])
				fold1FilePosNeg.write(featureVectorPos[ind])
			for ind in fold1_neg:
				fold1FileNeg.write(featureVectorNeg[ind])
				fold1FilePosNeg.write(featureVectorNeg[ind])
			for ind in fold2_pos:
				fold2FilePos.write(featureVectorPos[ind])
				fold2FilePosNeg.write(featureVectorPos[ind])
			for ind in fold2_neg:
				fold2FileNeg.write(featureVectorNeg[ind])
				fold2FilePosNeg.write(featureVectorNeg[ind])
	
			fold1FilePos.close()
			fold2FilePos.close()
			fold1FileNeg.close()
			fold2FileNeg.close()
			fold1FilePosNeg.close()
			fold2FilePosNeg.close()
	
	

# Perform the classification
for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		AUCs = open("referral/" + techniqueLow + "/" + techniqueMid + "/AUCs.txt","wb")
		for i in range(1,6):
			trainingName = "referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-negative-1.hist"
			positiveTestName = "referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-2.hist"
			negativeTestName = "referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-negative-2.hist"
			lenPos = len(open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-1.hist","rb").readlines())
			lenNeg = len(open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-negative-1.hist","rb").readlines())
	
			# Classify
			auc = classification(trainingName, positiveTestName, negativeTestName, str(i) + "-1", lenPos, lenNeg, techniqueLow, techniqueMid)
			AUCs.write(auc + "\n")
	
	
			trainingName = "referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-negative-2.hist"
			positiveTestName = "referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-1.hist"
			negativeTestName = "referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-negative-1.hist"
			lenPos = len(open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-positive-2.hist","rb").readlines())
			lenNeg = len(open("referral/" + techniqueLow + "/" + techniqueMid + "/fold-" + str(i) + "-negative-2.hist","rb").readlines())
	
			# Classify
			auc = classification(trainingName, positiveTestName, negativeTestName, str(i) + "-2", lenPos, lenNeg, techniqueLow, techniqueMid)
			AUCs.write(auc + "\n")
		AUCs.close()

	
	
# Calculate mean and standard deviation of the AUC using interpolation
file_legend = []
for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		directory = "referral/" + techniqueLow + "/" + techniqueMid + "/classification/"
		soma = np.zeros(101).tolist()
		yCompleto = []
		
		for fold in range(1,6):
			for cod in [1,2]:
				linhas = open(directory + "/operating-points-" + str(fold) + "-" + str(cod) + "-scale.dat", "rb").readlines()
				x = []
				y = []
				xant = -1
				for linha in linhas:
					linha = linha.split("\t")
					if float(linha[0]) != xant:
						x.append(float(linha[0]))
						y.append(float(linha[1][:-1]))
						xant = float(linha[0])
						
				x.reverse()
				y.reverse()

				temp = []

				for i in range(0,101,1):
					interp = np.interp(i/100.0, x, y)
					soma[i] += interp
					temp.append(interp)

				yCompleto.append(temp)
				
				
		arqMeanDeviation = open(directory + "/operating-points-" + str(fold) + "-" + str(cod) + "-mean-deviation.key", "wb")
		for i in range(101):
			mean = soma[i]/10.0
			deviation = 0
			for j in range(10):
				deviation += (yCompleto[j][i] - mean)**2
			arqMeanDeviation.write(str(i/100.0) + "\t" + str(mean) + "\t" + str(math.sqrt(deviation/10.0)) + "\n")
		arqMeanDeviation.close()
		
		
		file_legend.append((directory + "/operating-points-" + str(fold) + "-" + str(cod) + "-mean-deviation.key", "Low-level: " + techniqueLow + ". Mid-level: " + techniqueMid + "."))
			

if plot:
	plotRocCurves(file_legend)
		

