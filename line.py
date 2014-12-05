import math


def vectors(range, steps, direction):
	result = set()
	i=direction*math.pi/4-range/2
	while i <= direction*math.pi/2 + range/2:
		result.add((round(math.cos(i), 3), round(math.sin(i), 3)))
		i += range/steps
	return result

def neighbors(pos):
	return {(pos[0]-1, pos[1]), (pos[0]+1, pos[1]), (pos[0], pos[1]-1), (pos[0], pos[1]+1)}

class Line:
	def __init__(self, start, a,b):
		self.x, self.y = start
		if b == 0:
			self.a = 1
			self.b = 0
		elif a == 0:
			self.b = 1
			self.a = 0
		else:
			self.a = a/b
			self.b =b/a
		self.i = 0
		self.points = {start}
	def next(self,n=1):
		j=0
		while j<n:
			if (abs(self.a)<1):
				point=(round(self.i*self.a+self.x), round(self.i+self.y))
			else:
				#print ("first")
				#print ((self.i+self.x),(self.i/self.a+self.y))
				point=(round(self.i+self.x), round(self.i*self.b+self.y))
			self.i += 0.49
			while point in self.points:
				if (abs(self.a)<1):
					point=(round(self.i*self.a+self.x), round(self.i+self.y))
				else:
					#print ((self.i+self.x),(self.i/self.a+self.y))
					point=(round(self.i+self.x), round(self.i/self.a+self.y))
				self.i += 0.49
			self.points.add(point)
			return point
			j+=1
	def __str__(self):
		return str(self.points)


print (vectors(0.5*math.pi,20,0))