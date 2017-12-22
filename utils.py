import math

'''
This file holds various convenient mathematical calculation functions
'''

'''
euclidean_dist : calculates the euclidean distance between two points in N dimensional space
@return float distance between the two points
'''
def dist(p0, p1):
    if len(p0)!=len(p1):
        return -1
    return math.sqrt(sum([(a-b)**2 for (a,b) in zip(p0, p1)]))

def squared_vector_norm(v):
    return sum([x**2 for x in v])
