import math


def vectors(size, steps, direction):
	result = set()
	begining=(direction*math.pi)/2-size/2
	end=(direction*math.pi)/2+size/2
	n=int(steps+1)
	for i in range(n):
		angle=(i*begining+(steps-i)*end)/steps
		result.add((round((math.cos(angle)*10),2), round(math.sin(angle)*10,2)))


	return result

def neighbors(pos):
	return {(pos[0]-1, pos[1]), (pos[0]+1, pos[1]), (pos[0], pos[1]-1), (pos[0], pos[1]+1)}

class Line:
	def __init__(self, start, a, b):
		self.x, self.y = start
		if b == 0:
			self.a = a/abs(a)
			self.b = 0
		elif a == 0:
			self.b = b/abs(b)
			self.a = 0
		else:
			if abs(a) < abs(b):
				self.a = a/abs(b)
				self.b = b/abs(b)
			else:
				self.b = b/abs(a)
				self.a = a/abs(a)
		self.i = 0
		self.points = {start}
	def next(self, n=1):
		point = (round(self.i*self.a+self.x), round(self.i*self.b+self.y))
		self.i += 0.49
		while point in self.points:
			point = (round(self.i*self.a+self.x), round(self.i*self.b+self.y))
			self.i += 0.49
		self.points.add(point)
		return point
	def __str__(self):
		return str(self.points)

