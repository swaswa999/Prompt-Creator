from math import sqrt

def calculate_area(a, b, c):   #вычисляет
	p=(a+b+c)/2
	s = sqrt(p*(p-a)*(p-b)*(p-c))
	return s