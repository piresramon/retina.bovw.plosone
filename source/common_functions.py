import os, sys
import numpy
import math


def specialName(name):
	return name.replace(" ","\ ").replace("(","\(").replace(")","\)")
	
def l1norm(featureVector):
	s = sum(featureVector)
	normalizedFeatureVector = [ f/float(s) for f in featureVector ]
	return normalizedFeatureVector
	

def convertTime(sec):
	# receive the time in seconds and return in the format 00:00:00
	sec = int(sec)
	h = sec/3600
	
	if h < 10: out = "0" + str(h) + ":"
	else: out = str(h) + ":"
     	
     	sec = sec - 3600*h
	m = sec/60
	
	if m < 10: out = out + "0" + str(m) + ":"
	else: out = out + str(m) + ":"
	
	sec = sec - 60*m
	s = int(sec)
	
	if s < 10: out = out + "0" + str(s)
	else: out = out + str(s)
	return out
	
def organizeFileSurfToDescriptor(nfile):
	arqin = open(nfile,"rb")
	tamanho = arqin.readline()
	tamanho = int(tamanho) - 1
	totalPontos = int(arqin.readline())
	linha = str(totalPontos) + " " + str(tamanho) + " \n"
	out = []
	out.append(linha)
	linhas = arqin.readlines()
	for i in linhas:
		lin = i
		lin = lin.split(" ")
		cont = 0
		posicao = ""
		descritor = ""
		for j in lin:
			if (cont < 5):
				posicao = posicao + str(j) + " "
			elif (cont == 6):
				posicao = posicao + "\n"
				descritor = descritor + " " + str(j)
			elif (cont > 6):
				descritor = descritor + " " + str(j)				
			cont = cont + 1
		out.append(posicao)
		out.append(descritor)
	arqin.close()
	nout = nfile
	arqout = open(nout,"wb")
	arqout.seek(0)
	for o in out:
		arqout.write(o)
	arqout.close()
	
def filterPoints(dataset, technique, image):
	# DR1 diametro = 570, raio = 285
	# DR2 diametro = 558, raio = 279

	if dataset == "DR1": radius = 285
	elif dataset == "DR2": radius = 279
	elif dataset == "MESSIDOR": radius = 270

	#if image[-3:] != "key": continue
	if dataset == "DR1": xx, yy = 640, 480
	elif dataset == "DR2": xx, yy = 857, 569
	#elif dataset == "MESSIDOR":
	#image = cv2.imread("datasets/" + dataset + "-images-by-lesions/" + lesion + "/" + im)
	#xx, yy = cv.GetSize(cv.fromarray(image))
	# this part is incomplete

	xx = xx/2
	yy = yy/2

	ArqPoIs = open("low-level/" + technique + "/" + dataset + "/" + image[:-3] + "key","rb")
	PoIs = ArqPoIs.readlines()

	points = []

	for point in range(1,len(PoIs),2):
		x, y, a, b, c = PoIs[point].split()
		x = float(x)
		y = float(y)

		distance = math.sqrt((x-xx)*(x-xx) + (y-yy)*(y-yy))
		#print distance
		if (distance <= radius - 20):
			points.append(PoIs[point])
			points.append(PoIs[point+1])

	ArqPoIsOut = open("low-level/" + technique + "/" + dataset + "/" + image[:-3] + "key","wb")
	ArqPoIsOut.write(str(len(points)/2) + " 128\n")

	for point in points:
		ArqPoIsOut.write(point)
	ArqPoIsOut.close()
		
		
def filterPoints2(dataset, technique):
	# DR1 diametro = 570, raio = 285
	# DR2 diametro = 558, raio = 279

	if dataset == "DR1": radius = 285
	elif dataset == "DR2": radius = 279
	elif dataset == "MESSIDOR": radius = 270

	# Filter the PoIs of the dataset
	images = os.listdir("low-level/" + technique + "/" + dataset)
	for im in images:
		if im[-3:] != "key": continue
		if dataset == "DR1": xx, yy = 640, 480
		elif dataset == "DR2": xx, yy = 857, 569
		#elif dataset == "MESSIDOR":
		#image = cv2.imread("datasets/" + dataset + "-images-by-lesions/" + lesion + "/" + im)
		#xx, yy = cv.GetSize(cv.fromarray(image))
		# this part is incomplete

		xx = xx/2
		yy = yy/2

		ArqPoIs = open("low-level/" + technique + "/" + dataset + "/" + im,"rb")
		PoIs = ArqPoIs.readlines()

		points = []

		for point in range(1,len(PoIs),2):
			x, y, a, b, c = PoIs[point].split()
			x = float(x)
			y = float(y)

			distance = math.sqrt((x-xx)*(x-xx) + (y-yy)*(y-yy))
			#print distance
			if (distance <= radius - 20):
				points.append(PoIs[point])
				points.append(PoIs[point+1])

		ArqPoIsOut = open("low-level/" + technique + "/" + dataset + "/" + im,"wb")
		ArqPoIsOut.write(str(len(points)/2) + " 128\n")

		for point in points:
			ArqPoIsOut.write(point)
		ArqPoIsOut.close()
		
		
def insidearea(xpoint,ypoint,x,y):
	if float(xpoint) >= float(x[0]) and float(xpoint) <= float(x[1]):
		if float(ypoint) >= float(y[0]) and float(ypoint) <= float(y[1]):
			return True
		else:
			return False
	else :
		return False
		
		
def instersectionarea(xpoint, ypoint, radius, x, y, rectangleCoordinates, circleCoordinates):
	coordCircle = [ (u + math.floor(float(xpoint)), v + math.floor(float(ypoint))) for (u,v) in circleCoordinates ]
	coordCircle = set(coordCircle)
	rectangleCoordinates = set(rectangleCoordinates)
	
	inter = coordCircle.intersection(rectangleCoordinates)
	if (len(inter)/float(len(coordCircle)) >= 0.5) or (len(inter)/float(len(rectangleCoordinates)) >= 0.5):
		return True
	return False
	
	
def dist(X1,X2):
	#d = numpy.linalg.norm(numpy.array(X1)-numpy.array(X2))
	d = math.sqrt( (X1[0]-X2[0])*(X1[0]-X2[0]) + (X1[1]-X2[1])*(X1[1]-X2[1]) )
	return d
		
	
def getCandidateRegions(lesion, train, technique):
	if not os.path.exists("codebooks/" + technique + "/candidates/"):
   		os.makedirs("codebooks/" + technique + "/candidates/")
   		
	markingFiles = os.listdir("markings/")
		
	if technique == "sparse":
		candidates = []
		candidatesFile = open("codebooks/" + technique + "/candidates/candidates-" + lesion + ".cand","wb")
		
		for markingFile in markingFiles:					# by each file
			markings = open("markings/" + markingFile,"rb").readlines()
		
			# this is necessary because we have marked images that were not labeled as disease
			if not os.path.exists("low-level/" + technique + "/" + train + "/" + markingFile[:-3] + "key"): continue
			points = open("low-level/" + technique + "/" + train + "/" + markingFile[:-3] + "key","rb").readlines()[1:]
			diseaseRegions = []
		
			for marking in markings:					# by each line
				marking = marking.split()
				if lesion in marking:
					diseaseRegions.append(marking)
		
			for region in diseaseRegions:
				xx = region[2:4]
				yy = region[4:6]
			
				for indPoint in range(0,len(points),2):
					x, y, a, b, c = points[indPoint].split()
				
					if insidearea(x,y,xx,yy): # and (cont < diseaseWords)):
						candidates.append(points[indPoint + 1])
		for candidate in candidates:
			candidatesFile.write(candidate)
		candidatesFile.close()
		
	if technique == "dense":
		for diametro in [12, 19, 31, 50, 80, 128]:
			radius = diametro/2.0
			candidates = []
			candidatesFile = open("codebooks/" + technique + "/candidates/candidates-" + lesion + "-" + str(radius) + ".cand","wb")
			
			# used in interesectionarea function
			circleCoordinates = []			
			for x in range(-1* int(radius), int(radius) + 1):
				for y in range(-1* int(radius), int(radius) + 1):
			        	if math.sqrt(x*x + y*y) <= radius:
			        		circleCoordinates.append((x,y))
	
			
			for markingFile in markingFiles:					# by each file
				markings = open("markings/" + markingFile,"rb").readlines()
		
				# this is necessary because we have marked images that were not labeled as disease
				if not os.path.exists("low-level/" + technique + "/" + train + "/" + markingFile[:-4] + "-" + str(radius) + ".key"): continue
				points = open("low-level/" + technique + "/" + train + "/" + markingFile[:-4] + "-" + str(radius) + ".key","rb").readlines()[1:]
				diseaseRegions = []
		
				for marking in markings:					# by each line
					marking = marking.split()
					if lesion in marking:
						diseaseRegions.append(marking)
		
				for region in diseaseRegions:
					xx = region[2:4]
					yy = region[4:6]
					
					# used in interesectionarea function
					a = numpy.arange(int(xx[0]), int(xx[1]) + 1, 1).tolist()
					b = numpy.arange(int(yy[0]), int(yy[1]) + 1, 1).tolist()
					rectangleCoordinates = [(aa,bb) for aa in a for bb in b]
			
					for indPoint in range(0,len(points),2):
						x, y, a, b, c = points[indPoint].split()
				
						# verify if the point is within the marked region
						if insidearea(x,y,xx,yy):
							candidates.append(points[indPoint + 1])
						elif dist([float(x),float(y)],[float(xx[0]),float(yy[0])]) < radius or dist([float(x),float(y)],[float(xx[0]),float(yy[1])]) < radius or dist([float(x),float(y)],[float(xx[1]),float(yy[0])]) < radius or dist([float(x),float(y)],[float(xx[1]),float(yy[1])]) < radius:
							# verify if the 50% of the circular region is within the marked region or vice-versa
							if instersectionarea(x,y,radius,xx,yy, rectangleCoordinates, circleCoordinates):
								candidates.append(points[indPoint + 1])

			for candidate in candidates:
				candidatesFile.write(candidate)
			candidatesFile.close()
	
	
def getCandidateRegions2(anomaly, train, technique):
	doctor_marker_files_path = 'markings' # COLOCAR A PASTA MEDICAL MARKERS DENTRO DA PASTA ONDE ESTAO OS KEYPOINTS
	allimages = os.listdir(doctor_marker_files_path)
	totalpontos = 0
	cont = 0	
	out = []

	line_interest = 0
	flag = 1
	candidates = []

	# Itera por todas as imagens restantes
	for name in allimages:
		try:		
			area_file = open(doctor_marker_files_path + "/" + name,"rb")
			area_lines = area_file.readlines()
			areas_disease = []

			# Itera por todas as regioes marcadas para a imagem atual
			for line in area_lines:
				temp = line.split("\t")	
				# Testa se a regiao e do mesmo tipo da doenca procurada				
				if (anomaly in temp):
					areas_disease.append(line)
				area_file.close()
			
			# Se alguma das areas marcadas e do tipo da anomalia procurada
			if (len(areas_disease) > 0):
				image_points = name[:-3] + "key" 
				try:
					point_file = open("low-level/" + technique + "/" + train + "/" + image_points,"rb")
					point_lines = point_file.readlines()[1:]
					point_file.close()			
					
					# Para todas as regioes encontradas com a referida anomalia
					for ad in areas_disease:
						interest_area = ad.split("\t")
						x = interest_area[2:4]
						y = interest_area[4:6]
						lin = 0

						#Itera por todos os keypoints da imagem atual
						while(lin < len(point_lines)):
							temp = point_lines[lin].split(" ")
							if ((insidearea(temp[0],temp[1],x,y))):
								candidates.append(point_lines[lin + 1])
							lin = lin + 2
				except:
					continue
		except:
			continue
	print len(candidates)
	points = 0
	pts = []
	namefile = anomaly + "-candidates.palavras"
	arqout = open(namefile,"wb")
	arqout.seek(0)
	for i in candidates:
		arqout.write(i)
	arqout.close()
	#os.system("mv " + anomaly + "-candidates.palavras candidatos")


	
	
def adjustParametersKmeans(lesion, lenCodebook, technique):
	parameters = "  #stats tree\t# statistics output level\n  #show_assignments yes\t# show final cluster assignments\n  validate yes\t# validate assignments\n  dim 128\t# dimension\n\n  data_size 800000\t# number of data points\n  seed 1\t# random number seed\n"
	centroids = "  kcenters " + str(lenCodebook) + "\t# number of centers\n  max_tot_stage 200 0 0 0\t# number of stages\n\n  seed 5\t# use different seed\nrun_kmeans lloyd\t# run with this algorithm"
	
	if technique == "sparse":
		points = "read_data_pts codebooks/" + technique + "/candidates/candidates-" + lesion + ".cand\t # read data points \n\n"
	
		arqout = open("codebooks/" + technique + "/" + str(lenCodebook) + "-codewords-" + lesion + ".in","wb")
		arqout.write(parameters + points + centroids)
		arqout.close()
	else:
		for diametro in [12, 19, 31, 50, 80, 128]:
			radius = diametro/2.0
			points = "read_data_pts codebooks/" + technique + "/candidates/candidates-" + lesion + "-" + str(radius) + ".cand\t # read data points \n\n"
	
			arqout = open("codebooks/" + technique + "/" + str(lenCodebook) + "-codewords-" + lesion + "-" + str(radius) + ".in","wb")
			arqout.write(parameters + points + centroids)
			arqout.close()
	
def formatExitAdjust(arqin,arqout,numclusters):
	ain = open(arqin,"rb")
	ain.seek(0)
	lines = ain.readlines()
	ain.close()
	aout = open(arqout,"wb")
	aout.seek(0)
	flagcopia = 0
	cont = 1
	aout.write(str(numclusters) + " 128\n")
	for i in lines:
		if (flagcopia == 1):
			if (cont <= numclusters):
				line = i.split("\t")
				line = line[1]
				line = line.split("[")
				line = line[1]
				line = line.split("]")
				line = line[0]
				line = line.split(" ")
				lin = ""
				for i in line:
					if (str(i) != ''):
						lin = lin + " " + str(i)
				lin = lin + "\n"				
				aout.write(lin)
				cont = cont + 1
			else:
				flagcopia = 0				
		if (str(i) == "  (Final Center Points:\n"):
			flagcopia = 1
	aout.close()

def mergeCodebooks(lesion, size, technique):
	if technique == "sparse":
		diseaseFile = "codebooks/" + technique + "/codebook-" + lesion + ".cb"
		formatExitAdjust(diseaseFile,"diseaseFile.cb",size)
		disease = open("diseaseFile.cb","rb").readlines()
		os.system("rm diseaseFile.cb")
	
		normalFile = "codebooks/" + technique + "/codebook-imagem-normal.cb"
		formatExitAdjust(normalFile,"normalFile.cb",size)
		normal = open("normalFile.cb","rb").readlines()
		os.system("rm normalFile.cb")

		nameout = "codebooks/" + technique + "/complete-codebook-" + lesion + ".cb"
		aout = open(nameout,"wb")
		aout.write(str(2*size) + " 128\n")
		for i in disease[1:]:
			aout.write(i)
		for i in normal[1:]:
			aout.write(i)
		aout.close()
	
	else:
		nameout = "codebooks/" + technique + "/complete-codebook-" + lesion + ".cb"
		aout = open(nameout,"wb")
		aout.write(str(12*size) + " 128\n")
		for diametro in [12, 19, 31, 50, 80, 128]:
				radius = diametro/2.0
				diseaseFile = "codebooks/" + technique + "/codebook-" + lesion + "-" + str(radius) + ".cb"
				formatExitAdjust(diseaseFile, diseaseFile + ".temp",size)
				disease = open(diseaseFile + ".temp","rb").readlines()
				os.system("rm " + diseaseFile + ".temp")
	
				normalFile = "codebooks/" + technique + "/codebook-imagem-normal-" + str(radius) + ".cb"
				formatExitAdjust(normalFile, normalFile + ".temp", size)
				normal = open(normalFile + ".temp","rb").readlines()
				os.system("rm " + normalFile + ".temp")

				for i in disease[1:]:
					aout.write(i)
				for i in normal[1:]:
					aout.write(i)
		aout.close()
