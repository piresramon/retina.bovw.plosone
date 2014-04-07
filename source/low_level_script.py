import os, sys
import timeit
import common_functions


################################################
# Parameters 
################################################
# define the default parameters
train = "DR1"
test = "DR2"
lesions = ["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"]
t1 = 3500
t2 = 3500
techniques = ["sparse","dense"]
SURF = "./ext/surf/surf.ln"

# ShowOptions function
def showOptions():
	print "-h : show options"
	print "-train dataset : define the training dataset (default DR1)\n\tDR1 -- DR1 as the training dataset\n\tDR2 -- DR2 as the training dataset"
	print "-test dataset : define test dataset (default DR2)\n\tDR1 -- DR1 as the test dataset\n\tDR2 -- DR2 as the test dataset"
	print "-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares, imagem-normal])\n\texsudato-duro\t\t -- Hard Exudates\n\themorragia-superficial\t -- Superficial Hemorrhages\n\themorragia-profunda\t -- Deep Hemorrhages\n\tlesoes-vermelhas\t -- Red Lesions\n\tmancha-algodonosa\t -- Cotton-wool Spots\n\tdrusas-maculares\t -- Drusen\n\timagem-normal\t\t -- Normal Images"
	print "-low technique : define a specific low-level technique (default [sparse, dense])\n\tsparse -- Sparse low-level feature extraction\n\tdense  -- Dense low-level feature extraction"
	print "-t1 threshold : define the threshold for trainig dataset (default 3500)"
	print "-t2 threshold : define the threshold for test dataset (default 3500)"
	print "-surf path : define the path to the surf algorithm (default ./ext/surf/surf.ln)"
	quit()

# take the parameters
if len(sys.argv) > 1:		
	for i in range(1, len(sys.argv),2):
		op = sys.argv[i]
		if op == "-h": showOptions()
		elif op == "-train": train = sys.argv[i+1]
		elif op == "-test": test = sys.argv[i+1]
		elif op == "-l": lesions = [sys.argv[i+1]]
		elif op == "-low": techniques = [sys.argv[i+1]]
		elif op == "-t1": t1 = sys.argv[i+1]
		elif op == "-t2": t2 = sys.argv[i+1]
		elif op == "-surf": SURF = sys.argv[i+1]
################################################


################################################
# create directories
################################################
directory = "low-level/"
if not os.path.exists(directory + "sparse/" + train):
    os.makedirs(directory + "sparse/" + train)
if not os.path.exists(directory + "dense/" + train):
    os.makedirs(directory + "dense/" + train)
if not os.path.exists(directory + "sparse/" + test):
    os.makedirs(directory + "sparse/" + test)
if not os.path.exists(directory + "dense/" + test):
    os.makedirs(directory + "dense/" + test)
################################################


################################################
# Low-level feature extraction
################################################
en = dict(zip(["exsudato-duro","hemorragia-superficial","hemorragia-profunda","lesoes-vermelhas","mancha-algodonosa","drusas-maculares","imagem-normal"], ["Hard Exudates","Superficial Hemorrhages","Deep Hemorrhages","Red Lesions","Cotton-wool Spots","Drusen","Normal Images"]))

# Sparse extraction function
def sparseExtraction(im_special, technique, type, dirImage):
	os.system(SURF + " -i " + dirImage + "/" + im_special + " -o " + directory + technique + "/" + type + "/" + im_special[:-3] + "key -e -thres " + str(t1) + " -d 1> tmp/info.txt 2> tmp/errors.txt")
	
# Dense extraction function
def denseExtraction(im, im_special, technique, type, dirImage):
	finalLines = []
	count = 0
	for diametro in [12, 19, 31, 50, 80, 128]:
		radius = diametro/2.0
		os.system(SURF + " -i " + dirImage + "/" + im_special + " -p1 tmp/dense/points-region-" + str(radius) + "-" + type + ".txt -o " + directory + technique + "/" + type + "/" + im_special[:-4] + "-" + str(radius) + ".key -e 1> tmp/info.txt 2> tmp/errors.txt")
		lines = open(directory + technique + "/" + type + "/" + im[:-4] + "-" + str(radius) + ".key","rb").readlines()
		finalLines += lines[2:]
		count += int(lines[1])
		
		common_functions.organizeFileSurfToDescriptor(directory + technique + "/" + type + "/" + im[:-4] + "-" + str(radius) + ".key")
		
	out = open(directory + technique + "/" + type + "/" + im[:-3] + "key","wb")
	out.write("129\n" + str(count) + "\n")
	
	for line in finalLines:
		out.write(line)
	out.close()
	#os.system("rm " + im_special[:-3] + "key")
		

print "################################################"
print "# Low-level feature extraction"
print "################################################"
for type in [train,test]:
	if type == train: print "Training images -", type
	else: print "\n\nTest images -", type

	for lesion in lesions:
		if type == "DR2" and (lesion == "hemorragia-superficial" or lesion == "hemorragia-profunda"): continue
		lesion_en = en[lesion]
		print lesion_en
		listImages = os.listdir("datasets/" + type + "-images-by-lesions/" + lesion_en)
		
		start = timeit.default_timer()
		for im in listImages:
			sys.stdout.write(". ")
			sys.stdout.flush()
			im_special = common_functions.specialName(im)
			
			for technique in techniques:
				if os.path.exists(directory + technique + "/" + type + "/" + im[:-3] + "key"): continue
				fAux = open(directory + technique + "/" + type + "/" + im[:-3] + "key","wb")
								
				if technique == "sparse":
					sparseExtraction(im_special, technique, type, "datasets/" + type + "-images-by-lesions/" + common_functions.specialName(lesion_en))
					common_functions.organizeFileSurfToDescriptor(directory + technique + "/" + type + "/" + im[:-3] + "key")
					common_functions.filterPoints(type, technique, im)
				else:
					denseExtraction(im, im_special, technique, type, "datasets/" + type + "-images-by-lesions/" + common_functions.specialName(lesion_en))
					common_functions.organizeFileSurfToDescriptor(directory + technique + "/" + type + "/" + im[:-3] + "key")
			
		stop = timeit.default_timer()
		sys.stdout.write(common_functions.convertTime(stop - start) + "\n")
################################################



################################################
# Describe additional images
# (with marked regions but not labeled as normal or disease)
# Only when DR1 is defined as the training dataset
################################################

if train == "DR1":
	print "Low-level feature extraction for additional images (DR1) - used just because contain marked regions"
	start = timeit.default_timer()
	
	listImages = os.listdir("datasets/DR1-additional-marked-images/")
	for im in listImages:
		sys.stdout.write(". ")
		sys.stdout.flush()
		im_special = common_functions.specialName(im)
	
		for technique in techniques:
			if os.path.exists(directory + technique + "/DR1/" + im[:-3] + "key"): continue
			fAux = open(directory + technique + "/DR1/" + im[:-3] + "key","wb")
						
			if technique == "sparse":
				sparseExtraction(im_special, technique, "DR1", "datasets/DR1-additional-marked-images")
				common_functions.organizeFileSurfToDescriptor(directory + technique + "/DR1/" + im[:-3] + "key")
				common_functions.filterPoints("DR1", technique, im)
			else:
				denseExtraction(im, im_special, technique, "DR1", "datasets/DR1-additional-marked-images")
				common_functions.organizeFileSurfToDescriptor(directory + technique + "/DR1/" + im[:-3] + "key")
	
	stop = timeit.default_timer()
	sys.stdout.write(common_functions.convertTime(stop - start) + "\n")
	
	
	
	print "Low-level feature extraction for additional images (DR2) - images labeled according to referral, but not labeled with DR lesions"
	start = timeit.default_timer()
	
	listImages = os.listdir("datasets/DR2-images-by-referral/positive/")
	for im in listImages:
		sys.stdout.write(". ")
		sys.stdout.flush()
		im_special = common_functions.specialName(im)
	
		for technique in techniques:
			if os.path.exists(directory + technique + "/DR2/" + im[:-3] + "key"): continue
			fAux = open(directory + technique + "/DR2/" + im[:-3] + "key","wb")
						
			if technique == "sparse":
				sparseExtraction(im_special, technique, "DR2", "datasets/DR2-images-by-referral/positive")
				common_functions.organizeFileSurfToDescriptor(directory + technique + "/DR2/" + im[:-3] + "key")
				common_functions.filterPoints("DR2", technique, im)
			else:
				denseExtraction(im, im_special, technique, "DR2", "datasets/DR2-images-by-referral/positive")
				common_functions.organizeFileSurfToDescriptor(directory + technique + "/DR2/" + im[:-3] + "key")
	
	listImages = os.listdir("datasets/DR2-images-by-referral/negative/")
	for im in listImages:
		sys.stdout.write(". ")
		sys.stdout.flush()
		im_special = common_functions.specialName(im)
	
		for technique in techniques:
			if os.path.exists(directory + technique + "/DR2/" + im[:-3] + "key"): continue
			fAux = open(directory + technique + "/DR2/" + im[:-3] + "key","wb")
						
			if technique == "sparse":
				sparseExtraction(im_special, technique, "DR2", "datasets/DR2-images-by-referral/negative")
				common_functions.organizeFileSurfToDescriptor(directory + technique + "/DR2/" + im[:-3] + "key")
				common_functions.filterPoints("DR2", technique, im)
			else:
				denseExtraction(im, im_special, technique, "DR2", "datasets/DR2-images-by-referral/negative")
				common_functions.organizeFileSurfToDescriptor(directory + technique + "/DR2/" + im[:-3] + "key")
	
	stop = timeit.default_timer()
	sys.stdout.write(common_functions.convertTime(stop - start) + "\n")
################################################
