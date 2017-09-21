import cv2         
import numpy as np
import scipy.sparse
import scipy.sparse.linalg

# imports
import os
import random
import sys
import math

def gradient(img,y,x):
	grad = np.array([0.0, 0.0, 0.0])
	grad = img[y, x] * 4 - img[y + 1, x] - img[y - 1, x] - img[y, x + 1] - img[y, x - 1]

	return grad

def poisson(source,target, bitmask):
	height = source.shape[0]
	width = source.shape[1]

	result = np.zeros((source.shape))
	mask = np.broadcast_to(bitmask == 0, result.shape)
	result = target * mask

	product = target.shape[0] * target.shape[1]
	coeff = scipy.sparse.identity(product, format='lil')
	gradients = np.zeros((product, 3))


	#process coefficients and gradients

	for y in range(height):
		for x in range(width):
			if mask[y,x,0]:
				index = x + y * width
				tempGradient = np.array([0.0, 0.0, 0.0])
				coeff[index, index] = 4

				if mask[i - 1, j] == 1:
					coeff[index, index - 1] = -1
				else:
					tempGradient += target[i - 1, j]

				if mask[i + 1, j] == 1:
					coeff[index, index + 1] = -1
				else:
					tempGradient += target[i + 1, j]

				if mask[i, j - 1] == 1:
					coeff[index, index - hm] = -1
				else:
					tempGradient += target[i, j - 1]

				if mask[i, j + 1] == 1:
					coeff[index, index + hm] = -1
				else:
					tempGradient += target[i, j + 1]

				gradients[index] = gradient(y, x) + tempGradient
			else:
				index = x + y * width
				gradients[index] = target[y, x]


	coeff = coeff.tocsr()

	#solve for r
	x = scipy.sparse.linalg.spsolve(coeff, gradients[:, 0])

	#can be 318 or <0, so clamp
	m = x > 255
	x[m] = 255

	m = x < 0
	x[m] = 0

	rCol = x

	#solve for g
	x = scipy.sparse.linalg.spsolve(coeff, gradients[:, 1])

	#can be 318 or <0, so clamp
	m = x > 255
	x[m] = 255

	m = x < 0
	x[m] = 0

	gCol = x

	#solve for b
	x = scipy.sparse.linalg.spsolve(coeff, gradients[:, 2])

	#can be 318 or <0, so clamp
	m = x > 255
	x[m] = 255

	m = x < 0
	x[m] = 0

	bCol = x


	'''
	#mix the gradients
	alpha = 0.5
	rGradientSource = (alpha) * rGradientSource + (1 - alpha) * rGradientTarget
	gGradientSource = (alpha) * gGradientSource + (1 - alpha) * gGradientTarget
	bGradientSource = (alpha) * bGradientSource + (1 - alpha) * bGradientTarget
	'''

	#wrap into one image
	colors = np.concatenate((rCol,gCol,bCol))

	result += colors * mask
	return result


if __name__ == "__main__":
	
	img1Name = sys.argv[1]
	img2Name = sys.argv[2]
	bitName = sys.argv[3]
	imgNameOut = sys.argv[4]

	source = cv2.imread(img1Name)
	target = cv2.imread(img2Name)
	bitmask = cv2.imread(bitName)[:,:,:1] #read only one channel (they should all the same)

	mask = bitmask > 0
	bitmask[mask] = 1
	#bitmask is now either 0 or 1
	
	result = poisson(source, target,bitmask)

	'''
	#OpenCV implementation
	center = (int(target.shape[1]/2),int(target.shape[0]/2))
	
	result = cv2.seamlessClone(source, target, bitmask, center, cv2.NORMAL_CLONE)
	'''

	cv2.imwrite(imgNameOut, result)


