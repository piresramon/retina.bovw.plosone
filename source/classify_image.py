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
image = "IM000243.pgm"
lesions = ["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares"]
offset_user = ""
techniquesLow = ["sparse","dense"]
techniquesMid = ["hard","semi","soft"]
SVM = "./ext/svm/"

# ShowOptions function
def showOptions():
	print "-h : show options"
	print "-i image : define the name of the image (from DR2 dataset, e.g.: IM000243.pgm)"
	print "-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares, imagem-normal])\n\texsudato-duro\t\t -- Hard Exudates\n\themorragia-superficial\t -- Superficial Hemorrhages\n\themorragia-profunda\t -- Deep Hemorrhages\n\tlesoes-vermelhas\t -- Red Lesions\n\tmancha-algodonosa\t -- Cotton-wool Spots\n\tdrusas-maculares\t -- Drusen"
	print "-low technique : define a specific low-level technique (default [sparse, dense])\n\tsparse -- Sparse low-level feature extraction\n\tdense  -- Dense low-level feature extraction"
	print "-mid technique : define a specific mid-level technique (default [hard, semi, soft])\n\thard -- Hard-Sum coding/pooling\n\tsemi -- Semi-Soft-Sum coding/pooling\n\tsoft -- Soft-Max coding/pooling"
	print "-o offset: define a specific offset of the hyperplane (use only when select a specific DR-related lesion)"
	print "-svm path : define the path to the svm algorithm (default ./ext/svm/)"
	quit()

# take the parameters
if len(sys.argv) > 1:		
	for i in range(1, len(sys.argv),2):
		op = sys.argv[i]
		if op == "-h": showOptions()
		elif op == "-i": image = sys.argv[i+1]
		elif op == "-l": lesions = [sys.argv[i+1]]
		elif op == "-o": offset_user = sys.argv[i+1]
		elif op == "-low": techniquesLow = [sys.argv[i+1]]
		elif op == "-mid": techniquesMid = [sys.argv[i+1]]
		elif op == "-svm": SVM = sys.argv[i+1]
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
################################################




################################################
# MAIN
################################################
en = dict(zip(["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"], ["Hard Exudates","Superficial Hemorrhages","Deep Hemorrhages","Red Lesions","Cotton-wool Spots","Drusen","Normal Images"]))

for lesion in lesions:
	lesion_en = en[lesion]
	for techniqueMid in techniquesMid:
		for techniqueLow in techniquesLow:
		
			print "Classifying the image " + image + " for " + lesion_en + "\nLow-level: " + techniqueLow + "\nMid-level: " + techniqueMid
			
			imageName = image.split(".")[0] + ".hist"
			imagePath = "mid-level/" + techniqueLow + "/DR2/" + techniqueMid + "/" + lesion + "/" + imageName
			scaledTest = image.split(".")[0] + "-scale.hist"
			imagePath_add = "mid-level/" + techniqueLow + "/DR2/" + techniqueMid + "/additional/" + lesion + "/" + imageName
			
			if os.path.exists(imagePath) and os.path.getsize(imagePath) == 0:
				os.remove(imagePath)
			if os.path.exists(imagePath_add) and os.path.getsize(imagePath_add) == 0:
				os.remove(imagePath_add)
			if not os.path.exists(imagePath):
				# Describe the unique image
				command = "python mid_level_script.py -l " + lesion + " -low " + techniqueLow + " -mid " + techniqueMid + " -i " + image
				os.system(command + "  > tmp/info-classify_image.txt 2> tmp/errors.txt")				
				imagePath = imagePath_add
			
			
			# SVM format
			if techniqueMid == "soft":
				os.system("cp " + imagePath + " " + imageName + ".temp")
				SVMformat(imageName + ".temp", imageName)
				os.remove(imageName + ".temp")
			else:
				command = SVM + "convert " + imagePath + " > " + imageName
				os.system(command)
				
				
			# Classification
			resultName = "result-" + techniqueLow + "-" + techniqueMid + "-" + lesion + "-" + image.split(".")[0] + ".txt"
			model = "classification/" + techniqueLow + "/" + techniqueMid + "/" + lesion + ".model"
			rangeFile = "classification/" + techniqueLow + "/" + techniqueMid + "/range-" + lesion
			command = SVM + "svm-scale -r " + rangeFile + " " + imageName + " > " + scaledTest
			os.system(command)
			command = SVM + "svm-predict " + scaledTest + " " + model + " " + resultName
			os.system(command + "  > tmp/info.txt 2> tmp/errors.txt")
			
			
			
			# Request the operating point
			if offset_user == "":
				shiftsSensSpecs = open("classification/" + techniqueLow + "/" + techniqueMid + "/shifts-sens-spec-" + lesion + ".dat", "rb").readlines()
				i = 1
				print "-----------------------------------------\n|   id\t|   Sensitivity\t|   Specificity\t|\n-----------------------------------------"
				for shiftSensSpec in shiftsSensSpecs:
					shift, sens, spec = shiftSensSpec.split()
					print "|   " + str(i) + "\t|   " + sens + "\t|   " + spec + "\t|"
					i = i+1
				print "-----------------------------------------"
			
				id_user = raw_input('Enter the desired pair sensitivity/specificity (id): ')
				offset_user = shiftsSensSpecs[int(id_user) - 1].split()[0]
						
			
			score = open(resultName,"rb").readline()
			score = float(score) - float(offset_user)		# subtracts the offset from the original score
			if score > 0: label = "SICK"
			else: label = "NORMAL"
			
			print "The image " + image + " was classified as " + label + "\nScore: " + str(score) + "\n"
			
			# Clean
			os.system("rm " + imageName + " " + scaledTest)



