import os, sys
import timeit
import common_functions


################################################
# Parameters 
################################################
# define the default parameters
train = "DR1"
lesions = ["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"]
techniques = ["sparse","dense"]
sizeFlag = False			# change to True if a size be passed
KMEANS = "./ext/kmeans/kmltest"

# ShowOptions function
def showOptions():
	print "-h \t\t show options"
	print "-train \t\t define training dataset"
	print "-l \t\t define a specific DR-related lesion"
	print "-low \t\t define a specific low-level technique"
	print "-size \t\t length of the codebook (per class)"
	print "-kmeans \t define the path to k-means"
	quit()

# take the parameters
if len(sys.argv) > 1:		
	for i in range(1, len(sys.argv),2):
		op = sys.argv[i]
		if op == "-h": showOptions()
		elif op == "-train": train = sys.argv[i+1]
		elif op == "-l": lesions = [sys.argv[i+1]]
		elif op == "-low": techniques = [sys.argv[i+1]]
		elif op == "-size": 
			size = sys.argv[i+1]
			sizeFlag = True
		elif op == "-kmeans": KMEANS = sys.argv[i+1]
################################################


################################################
# Create codebooks
################################################
en = dict(zip(["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"], ["Hard Exudates","Superficial Hemorrhages","Deep Hemorrhages","Red Lesions","Cotton-wool Spots","Drusen","Normal Images"]))


for lesion in lesions:
	for technique in techniques:
		if not os.path.exists("codebooks/" + technique):
	   		os.makedirs("codebooks/" + technique)
	   	
	   	if not sizeFlag:	# if the used did not pass a size, use the default
	   		if technique == "sparse": size = 250	# 250 * 2 (normal and disease) = 500
	   		else: size = 125			# 125 * 2 (normal and disease) * 6 (#scales) = 1500
	   		
		lesion_en = en[lesion]
		sys.stdout.write("Extracting codebooks for " + lesion_en + " in " + technique + " technique")
		sys.stdout.flush()
	
		# filter the points into marked regions
		if lesion == "lesoes-vermelhas":
			if technique == "sparse":
				if not os.path.exists("codebooks/" + technique + "/candidates/candidates-hemorragia-superficial.cand"):
					common_functions.getCandidateRegions("hemorragia-superficial", train, technique)
				if not os.path.exists("codebooks/" + technique + "/candidates/candidates-hemorragia-profunda.cand"):
					common_functions.getCandidateRegions("hemorragia-profunda", train, technique)
				candidatesFile = open("codebooks/" + technique + "/candidates/candidates-" + lesion + ".cand","wb")
				profunda = open("codebooks/" + technique + "/candidates/candidates-hemorragia-profunda.cand","rb").readlines()
				superficial = open("codebooks/" + technique + "/candidates/candidates-hemorragia-superficial.cand","rb").readlines()
				for cand in profunda: candidatesFile.write(cand)
				for cand in superficial: candidatesFile.write(cand)
				candidatesFile.close()
			else:
				for diametro in [12, 19, 31, 50, 80, 128]:
					radius = diametro/2.0
					if not os.path.exists("codebooks/" + technique + "/candidates/candidates-hemorragia-superficial-" + str(radius) + ".cand"):
						common_functions.getCandidateRegions("hemorragia-superficial", train, technique)
					if not os.path.exists("codebooks/" + technique + "/candidates/candidates-hemorragia-profunda-" + str(radius) + ".cand"):
						common_functions.getCandidateRegions("hemorragia-profunda", train, technique)
					candidatesFile = open("codebooks/" + technique + "/candidates/candidates-" + lesion + "-" + str(radius) + ".cand","wb")
					profunda = open("codebooks/" + technique + "/candidates/candidates-hemorragia-profunda-" + str(radius) + ".cand","rb").readlines()
					superficial = open("codebooks/" + technique + "/candidates/candidates-hemorragia-superficial-" + str(radius) + ".cand","rb").readlines()
					for cand in profunda: candidatesFile.write(cand)
					for cand in superficial: candidatesFile.write(cand)
					candidatesFile.close()
		else:	common_functions.getCandidateRegions(lesion, train, technique)
		
		# define the parameters of k-means
		common_functions.adjustParametersKmeans(lesion, size, technique)
		
		# run k-means
		start = timeit.default_timer()
		if technique == "sparse":
			os.system(KMEANS + " -i codebooks/" + technique + "/" + str(size) + "-codewords-" + lesion + ".in -o codebooks/" + technique + "/codebook-" + lesion + ".cb")
		else:
			for diametro in [12, 19, 31, 50, 80, 128]:
				radius = diametro/2.0
				os.system(KMEANS + " -i codebooks/" + technique + "/" + str(size) + "-codewords-" + lesion + "-" + str(radius) + ".in -o codebooks/" + technique + "/codebook-" + lesion + "-" + str(radius) + ".cb")
		stop = timeit.default_timer()
		sys.stdout.write(" - codebook created in " + common_functions.convertTime(stop - start) + "\n") 
		sys.stdout.flush()
	

for lesion in lesions:
	if lesion == "imagem-normal": continue
	sys.stdout.write("Concatenating the codebooks")
	sys.stdout.flush()
	start = timeit.default_timer()
	for technique in techniques:
		if not sizeFlag:	# if the used did not pass a size, use the default
	   		if technique == "sparse": size = 250	# 250 * 2 (normal and disease) = 500
	   		else: size = 125			# 125 * 2 (normal and disease) * 6 (scales) = 1500
			common_functions.mergeCodebooks(lesion, size, technique)
	stop = timeit.default_timer()
	sys.stdout.write(" - done in " + common_functions.convertTime(stop - start) + "\n") 
	sys.stdout.flush()
################################################
