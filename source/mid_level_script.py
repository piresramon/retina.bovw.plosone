#coding:utf-8
import os, sys
import timeit
import numpy, math
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

# ShowOptions function
def showOptions():
	print "-h \t\t show options"
	print "-train \t\t define training dataset"
	print "-test \t\t define test dataset"
	print "-l \t\t define a specific DR-related lesion"
	print "-low \t\t define a specific low-level technique"
	print "-mid \t\t define a specific mid-level technique"
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
################################################


################################################
# create directories
################################################
directory = "mid-level/"
for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		for type in [train,test]:
			for lesion in lesions:
				if not os.path.exists(directory + techniqueLow + "/" + type + "/" + techniqueMid + "/" + lesion):
					os.makedirs(directory + techniqueLow + "/" + type + "/" + techniqueMid + "/" + lesion)
################################################



################################################
# HARD-SUM
################################################
def hardSum(ArqPoIs, ArqWords, ArqOut, numeroPalavras, label):
	ArqOut = open(ArqOut,"wb")
	ArqOut.write(label + " ")
	out = label + " "
	PoIsTemp = open(ArqPoIs, "rb").readlines()
	WordsTemp = open(ArqWords, "rb").readlines()
	histograma = [0 for i in range(numeroPalavras)]
	
	PoIs = []
	for i in range(2,len(PoIsTemp),2):
		l = PoIsTemp[i].split()
		line = []
		for ll in l:
			line.append(float(ll))
		PoIs.append(line)
		
	Words = []
	for w in WordsTemp[1:]:
		l = w.split()
		line = []
		for ll in l:
			line.append(float(ll))
		Words.append(line)
		
	for p in range(len(PoIs)):
		minimo = 100
		for i in range(len(Words)):
			dist = numpy.linalg.norm(numpy.array(Words[i])-numpy.array(PoIs[p]))
			if dist < minimo:
				minimo = dist
				ind = i
		histograma[ind] += 1

	histograma = common_functions.l1norm(histograma)	
	
	for h in histograma:
		ArqOut.write(str(h) + " ")
		out += str(h) + " "
	ArqOut.close()
			
	#print "DISTANCE = " + str(numpy.linalg.norm(numpy.array(Words[0])-numpy.array(PoIs[0])))
	return out
################################################



################################################
# SEMI-SOFT
################################################
def semiSoft(ArqPoIs, ArqWords, ArqOut, numeroPalavras, label):
	ArqOut = open(ArqOut,"wb")
	ArqOut.write(label + " ")
	out = label + " "
	PoIsTemp = open(ArqPoIs, "rb").readlines()
	WordsTemp = open(ArqWords, "rb").readlines()
	
	PoIs = []
	for i in range(2,len(PoIsTemp),2):
		l = PoIsTemp[i].split()
		line = []
		for ll in l:
			line.append(float(ll))
		PoIs.append(line)
		
	Words = []
	for w in WordsTemp[1:]:
		l = w.split()
		line = []
		for ll in l:
			line.append(float(ll))
		Words.append(line)
	
	distances = []
	for i in range(0,numeroPalavras):
		distances.append(0)
	
	for poi in PoIs:
		for i in range(len(Words)):
			dist = numpy.linalg.norm(numpy.array(Words[i])-numpy.array(poi))
			if dist == 0: continue
			if 1/dist > distances[i]:
				distances[i] = 1/dist
		
	distances = common_functions.l1norm(distances)
	
	for d in distances:
		ArqOut.write(str(d) + " ")
		out += str(d) + " "
	ArqOut.close()
				
	#print "DISTANCE = " + str(numpy.linalg.norm(numpy.array(Words[0])-numpy.array(PoIs[0])))
	return out
################################################



################################################
# SOFT-MAX
################################################
def gaussiankernel(sigma, x):
	return (1.0/(math.sqrt(sigma*2*math.pi)))*math.exp(-(x)**2/(2.0*sigma**2))
	

def softMax(ArqPoIs, ArqWords, ArqOut, numeroPalavras, label):
	ArqOut = open(ArqOut,"wb")
	ArqOut.write(label + " ")
	out = label + " "
	PoIsTemp = open(ArqPoIs, "rb").readlines()
	WordsTemp = open(ArqWords, "rb").readlines()
	
	PoIs = []				#Coloca os pontos de interesse em um vetor
	for i in range(2,len(PoIsTemp),2):
		l = PoIsTemp[i].split()
		line = []
		for ll in l:
			line.append(float(ll))
		PoIs.append(line)
		
	Words = []				#Coloca as palavras visuais em um vetor
	for w in WordsTemp[1:]:
		l = w.split()
		line = []
		for ll in l:
			line.append(float(ll))
		Words.append(line)
	
	distances = []				#Matriz n * V (número de pontos * número de palavras) que calculará apenas uma vez as distâncias
	for i in range(0,numeroPalavras):
		line = []
		for j in range(0,len(PoIs)):
			dist = numpy.linalg.norm(numpy.array(Words[i])-numpy.array(PoIs[j]))
			dist = gaussiankernel(45.0, dist)
			line.append(dist)
		distances.append(line)
	
	distToAll = []				#Vetor que armazenará para cada ponto o somatório das distâncias para todas as palavras
	for i in range(0,len(PoIs)):	
		s = 0
		for j in range(0,numeroPalavras):
			s += distances[j][i]
		distToAll.append(s)
	
	features = []
	
	for i in range(0,numeroPalavras):	#Para cada palavra, calcula o Codeword uncertainty (Visual Word Ambiguity, Gemert et al.)
		maximo = 0			#Substituímos average pooling por max pooling
		for j in range(0,len(PoIs)):
			d = distances[i][j]/distToAll[j]
			if d > maximo: maximo = d
		features.append(maximo)
		#out += str(maximo) + " "
		
	features = common_functions.l1norm(features)
	
	for f in features:
		ArqOut.write(str(f) + " ")
		out += str(f) + " "
	ArqOut.close()
	
	#print out	
	return out
################################################



################################################
# MAIN
################################################
en = dict(zip(["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"], ["Hard Exudates","Superficial Hemorrhages","Deep Hemorrhages","Red Lesions","Cotton-wool Spots","Drusen","Normal Images"]))

print "################################################"
print "# Low-level feature extraction"
print "################################################"

for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		if techniqueLow == "sparse": size = 500
		else: size = 1500
		for type in [train,test]:
			for lesion in lesions:
				print "Extracting features for " + en[lesion] + "\nLow-level: " + techniqueLow + ".\nMid-level: " + techniqueMid
				start = timeit.default_timer()
				sys.stdout.write(". ")
				sys.stdout.flush()
				
				# define the codebook
				CodebookFile = "codebooks/" + techniqueLow + "/complete-codebook-" + lesion  + ".cb"
				
				# define the the directory of the input file (points of interest)
				PoIsDir = "low-level/" + techniqueLow + "/" + type + "/"
				
				# define the the directory of the output file (histogram)
				OutDir = "mid-level/" + techniqueLow + "/" + type + "/" + techniqueMid + "/" + lesion + "/"
				
				for label in ["+1","-1"]:
					# describe the normal images
					if label == "-1": lesion = "imagem-normal"
								
					lesion_en = en[lesion]
					if type == "DR2" and (lesion == "hemorragia-superficial" or lesion == "hemorragia-profunda"):
						listImages = os.listdir("datasets/" + type + "-images-by-lesions/Red Lesions")
					else:
						listImages = os.listdir("datasets/" + type + "-images-by-lesions/" + lesion_en)
				
					for im in listImages:
						im_special = common_functions.specialName(im)
						if os.path.exists(OutDir + im[:-3] + "hist"): continue
					
						# define the input file (points of interest)
						PoIsFile = PoIsDir + im[:-3] + "key"
					
						# define the output file (histogram)
						OutFile = OutDir + im[:-3] + "hist"
					
						sys.stdout.write(". ")
						sys.stdout.flush()
			
						if techniqueMid == "hard":
							hardSum(PoIsFile, CodebookFile, OutFile, size, label)
						elif techniqueMid == "soft":
							softMax(PoIsFile, CodebookFile, OutFile, size, label)
						else:				#if techniqueMid == "semi":
							semiSoft(PoIsFile, CodebookFile, OutFile, size, label)
				stop = timeit.default_timer()
				sys.stdout.write(" Done in " + common_functions.convertTime(stop - start) + "\n")
################################################
