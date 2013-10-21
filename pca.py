import numpy as np
import scipy as sp
import sys
import re
import fileinput

def pca(input):
	input = input - input.mean(axis=0)
	(u,s,v) = np.linalg.svd(input, full_matrices=False)
	return np.dot(input, v.T)

def main():
	data = None
	for line in fileinput.input():
		items = line.split(',')
		if data == None:
			data = items
		else:
			data = np.vstack([data, items])

	A = pca(data)

	for r in A:
        print "%.04f\t%.04f" % (r[0], r[1])

if __name__ == '__main__':
	main()
