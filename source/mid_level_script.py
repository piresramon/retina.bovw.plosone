#coding:utf-8
import os, sys
import timeit
import numpy, math
import scipy.spatial.distance as sp
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
image = ""

# ShowOptions function
def showOptions():
	print "-h : show options"
	print "-train dataset : define the training dataset (default DR1)\n\tDR1 -- DR1 as the training dataset\n\tDR2 -- DR2 as the training dataset"
	print "-test dataset : define test dataset (default DR2)\n\tDR1 -- DR1 as the test dataset\n\tDR2 -- DR2 as the test dataset"
	print "-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares)\n\texsudato-duro\t\t -- Hard Exudates\n\themorragia-superficial\t -- Superficial Hemorrhages\n\themorragia-profunda\t -- Deep Hemorrhages\n\tlesoes-vermelhas\t -- Red Lesions\n\tmancha-algodonosa\t -- Cotton-wool Spots\n\tdrusas-maculares\t -- Drusen"
	print "-low technique : define a specific low-level technique (default [sparse, dense])\n\tsparse -- Sparse low-level feature extraction\n\tdense  -- Dense low-level feature extraction"
	print "-mid technique : define a specific mid-level technique (default [hard, semi, soft])\n\thard -- Hard-Sum coding/pooling\n\tsemi -- Semi-Soft-Sum coding/pooling\n\tsoft -- Soft-Max coding/pooling"
	print "-i image : define the image name (used only for cases where we are interested in describing only one image)"
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
		elif op == "-i": image = sys.argv[i+1]
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
def hardSum(PoIs, Words, ArqOut, numeroPalavras, label):
	ArqOut = open(ArqOut,"wb")
	ArqOut.write(label + " ")
	histograma = [0 for i in range(numeroPalavras)]
	
	distMatrix = sp.cdist(PoIs, Words, 'euclidean')								# first points, after codewords. Return a len(PoIs) x len(Words) matrix of distances
	
	for i in range(len(PoIs)):
		minimum = min(distMatrix[i])
		ind = numpy.where(distMatrix[i]==minimum)[0][0]
		histograma[ind] += 1

	
	histograma = common_functions.l1norm(histograma)	
	
	for h in histograma:
		ArqOut.write(str(h) + " ")
	ArqOut.close()
################################################



################################################
# SEMI-SOFT
################################################
def semiSoft(PoIs, Words, ArqOut, numeroPalavras, label):
	ArqOut = open(ArqOut,"wb")
	ArqOut.write(label + " ")
	distances = numpy.zeros(numeroPalavras)
	
	distances = sp.cdist(Words, PoIs, 'euclidean')								# first codewords, after PoIs. Return a len(Words) x len(PoIs) matrix of distances
	distances = [ 1/min(d) for d in distances ]
		
	
	distances = common_functions.l1norm(distances)
	
	for d in distances:
		ArqOut.write(str(d) + " ")
	ArqOut.close()
################################################



################################################
# SOFT-MAX
################################################
def gaussiankernel(sigma, x):
	return (1.0/(math.sqrt(sigma*2*math.pi)))*math.exp(-(x)**2/(2.0*sigma**2))
	

def softMax(PoIs, Words, ArqOut, numeroPalavras, label):
	ArqOut = open(ArqOut,"wb")
	ArqOut.write(label + " ")
	
	# distances - Matriz n * V (número de pontos * número de palavras) que calculará apenas uma vez as distâncias
	distances = sp.cdist(PoIs, Words, 'euclidean')								# first points, after codewords. Return a len(PoIs) x len(Words) matrix of distances
	distances = [ gaussiankernel(45.0, dist) for dist in numpy.reshape(distances, (1,distances.size))[0] ]	# apply the gaussian kernel
	distances = numpy.reshape(distances, (len(PoIs), len(Words)))						# put again in the format len(PoIs) x len(Words)
	
	# distToAll - Vetor que armazenará para cada ponto o somatório das distâncias para todas as palavras
	distToAll = []
	for point in distances:
		distToAll.append(sum(point)) 
	distToAll = numpy.asarray(distToAll)
	
	features = []
	distances = numpy.transpose(distances)					# transpose. Format len(Words) x len(PoIs)
	division = numpy.divide(distances, distToAll)				# Equivalent to divide the distance of codeword i to PoI j by the summation of the distances of PoI j to all codewords
	features = [ max(dist) for dist in division ]				# get the maximum activation for each codeword
		
	
	features = common_functions.l1norm(features)
	
	for f in features:
		ArqOut.write(str(f) + " ")
	ArqOut.close()	
################################################



################################################
# MAIN
################################################
en = dict(zip(["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"], ["Hard Exudates","Superficial Hemorrhages","Deep Hemorrhages","Red Lesions","Cotton-wool Spots","Drusen","Normal Images"]))

print "################################################"
print "# Mid-level feature extraction"
print "################################################"

for techniqueMid in techniquesMid:
	for techniqueLow in techniquesLow:
		if techniqueLow == "sparse": size = 500
		else: size = 1500
		for type in [train,test]:
			for lesion in lesions:
				print "Extracting features for " + en[lesion] + "\nLow-level: " + techniqueLow + "\nMid-level: " + techniqueMid
				start = timeit.default_timer()
				sys.stdout.write(". ")
				sys.stdout.flush()
				
				# get the codebook
				CodebookTemp = open("codebooks/" + techniqueLow + "/complete-codebook-" + lesion  + ".cb", "rb").readlines()
				Codebook = []
				for cb in CodebookTemp[1:]:
					Codebook.append([ float(c) for c in cb.split() ])
				Codebook = numpy.asarray(Codebook)
				
				# define the directory of the input file (points of interest)
				if image == "":
					PoIsDir = "low-level/" + techniqueLow + "/" + type + "/"
				else:
					PoIsDir = "low-level/" + techniqueLow + "/DR2/"
				
				# define the directory of the output file (histogram)
				if image == "":
					OutDir = "mid-level/" + techniqueLow + "/" + type + "/" + techniqueMid + "/" + lesion + "/"
				else:	# Interest in describing only one image
					if not os.path.exists("mid-level/" + techniqueLow + "/DR2/" + techniqueMid + "/additional/" + lesion):
						os.makedirs("mid-level/" + techniqueLow + "/DR2/" + techniqueMid + "/additional/" + lesion)
					OutDir = "mid-level/" + techniqueLow + "/DR2/" + techniqueMid + "/additional/" + lesion + "/"
				
				for label in ["+1","-1"]:
					# describe the normal images
					if label == "-1": lesion = "imagem-normal"
								
					lesion_en = en[lesion]
					if image == "":
						if type == "DR2" and (lesion == "hemorragia-superficial" or lesion == "hemorragia-profunda"):
							listImages = os.listdir("datasets/" + type + "-images-by-lesions/Red Lesions")
						else:
							listImages = os.listdir("datasets/" + type + "-images-by-lesions/" + lesion_en)
					else: listImages = [image]
				
					for im in listImages:
						im_special = common_functions.specialName(im)
						if os.path.exists(OutDir + im[:-3] + "hist"): continue
						
						# define the output file (histogram)
						OutFile = OutDir + im[:-3] + "hist"
						f = open(OutFile,"wb")
					
						# get the points of interest
						PoIsTemp = open(PoIsDir + im[:-3] + "key","rb").readlines()
						PoIs = []
						for i in range(2,len(PoIsTemp),2):
							PoIs.append([ float(p) for p in PoIsTemp[i].split() ])
						PoIs = numpy.asarray(PoIs)				
									
						sys.stdout.write(". ")
						sys.stdout.flush()
			
						if techniqueMid == "hard":
							hardSum(PoIs, Codebook, OutFile, size, label)
						elif techniqueMid == "soft":
							softMax(PoIs, Codebook, OutFile, size, label)
						else:				#if techniqueMid == "semi":
							semiSoft(PoIs, Codebook, OutFile, size, label)
						
				stop = timeit.default_timer()
				sys.stdout.write(" Done in " + common_functions.convertTime(stop - start) + "\n")
################################################
