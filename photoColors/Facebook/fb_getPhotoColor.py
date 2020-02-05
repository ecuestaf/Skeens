import os
import struct
import sys
import json 
import math
import pandas as pd 
from pandas.io.json import json_normalize
from os import listdir
from os.path import isfile, join
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster# Puramente estetico

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'





# MACROS TOTALMENTE TOCABLES

# La verdad que no me he parado a entender las funciones por debajo (ni falta que hace)
# Seguramente a mas clusteres mas precision a costa de mas coste computacional, no queremos tampoco demasiada precision I guess.
NUM_CLUSTERS = 3

# LADO DEL CUADRADO
SQUARE_SIDE = 10




# MEJOR NO TOCAR

IMAGES_PATH = "/images"

# Crea una imagen auxiliar con el color que se le proporciona.
# La llama como su segundo argumento.
# En el proceso automatico estas imagenes auxiliares se borran despues.
def createSingleSquareImage(colourTuple, outputName):
	pick, colour = colourTuple

	new_im = Image.new('RGB', (SQUARE_SIDE, SQUARE_SIDE))

	colTuple = (int(pick[0]),int(pick[1]), int(pick[2]))
	new_im.paste(colTuple, [0,0,new_im.size[0],new_im.size[1]])

	new_im.save(outputName)


# Crea varios ficheros con cuadrado de colores
def createAllSquares(listOfColors):
	
	basestr = 'aux.jpg'	
	i = 1
	nameList = []

	for col in listOfColors:
		name = str(i) + basestr
		print(name)
		createSingleSquareImage(col, name)
		nameList.append(name)		
		i += 1 

	return nameList


def deleteAuxImages(nameList):
	
	for name in nameList:
		
		os.remove(name)

def createWholeImage(listOfColors):


	# creacion las subimagenes (cuadrados con sus colores pertinentes)

	imageList = createAllSquares(listOfColors)

	# podemos asumir que todas van a tener el mismo tamaño de ancho y largo, eso simplifica los calculos siguientes
	print(imageList)
	images = list(map(Image.open, imageList))

	width, height = images[0].size

	num_squares = len(listOfColors)
	IMAGESPERFILE = math.ceil(math.sqrt((16/27)*num_squares))

	total_width = width*IMAGESPERFILE
	total_height = math.ceil(len(imageList)/IMAGESPERFILE)*height
	
	print(total_width)
	print(total_height)
	
	new_im = Image.new('RGB', (total_width, total_height))

	count = 0
	x_offset = 0
	y_offset = 0
	for im in images:
	  new_im.paste(im, (x_offset,y_offset))
	  x_offset += im.size[0]
	  count += 1  
	  if count % IMAGESPERFILE == 0 and count != 0:
	    
	    y_offset += im.size[1]
	    x_offset = 0
	  

	new_im.save('resss.jpg')

	
	deleteAuxImages(imageList)	


def getListOfDominantColors(listOfImageNames):
	'''
	Argumentos:
		listOfImageNames = Lista con todos los nombre de las imagenes
	Retorno:
		Una lista de tuplas donde cada elemento es de la forma (peak, colour)
	'''
	L = []
	for im in listOfImageNames:
		L.append(getDominantColor(im))

	return L
		


def getDominantColor(imName):
	'''
	Argumentos:
		imName = Nombre de la imagen que se va a analizar
	Retorno:
		Una tupla de dos elementos:
			peak = Codificacion similar a esto [244.00661895   5.01980305   2.19641608] (Creo que es RGB)
			colour = Codificacion de la forma (#b'\xc3\xb4\x05\x02') (Esto ya...)
		Yo no se ver los colores a ojo, maybe tu si.
		NO PIERDAS EL TIEMPO EN ESTA FUNCION SALVO QUE NOTES QUE EFECTIVAMENTE NO ESTA SACANDO EL COLOR DOMINANTE 
	'''
	#print('reading image')
	im = Image.open(imName)
	im = im.resize((150, 150))      # optional, to reduce time
	ar = np.asarray(im)
	shape = ar.shape
	ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

	#print('finding clusters')
	codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
	#print('cluster centres:\n', codes)

	vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
	counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

	index_max = scipy.argmax(counts)                    # find most frequent
	peak = codes[index_max]
	colour = ''.join(chr(int(c)) for c in peak).encode()
	
	return peak, colour
	#print('most frequent is %s (#%s)' % (peak, colour))

	#Note: when I expand the number of clusters to find from 5 to 10 or 15, it frequently gave results that were greenish or bluish. Given the input image, those are 		reasonable results too... I can't tell which colour is really dominant in that image either, so I don't fault the algorithm!


def main():
	listOfNames = []
	dataPath = os.getcwd() + IMAGES_PATH
	print(bcolors.WARNING + "ANALIZANDO FICHEROS:" + bcolors.ENDC)

	for folderName in os.listdir(dataPath):
		if folderName.startswith("."):
   			continue

		provisionalPath = dataPath + "/" + folderName
		for fileName in os.listdir(provisionalPath):
			if fileName.startswith("."):
				continue
			print(bcolors.OKBLUE + fileName + bcolors.ENDC)
			filePath = provisionalPath +  "/" + fileName 
			listOfNames.append(filePath)

	colorsList = getListOfDominantColors(listOfNames)

	createWholeImage(colorsList)



if __name__ == "__main__":
    main()
