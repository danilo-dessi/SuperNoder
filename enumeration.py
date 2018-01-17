from support_functions import *

# These function enumerate motifs of size k into a graph g. These function are a python implementation of the enumeration function 
# that has been used by the authors of fanmode software. See for more details:
# Wernicke, Sebastian. "A faster algorithm for detecting network motifs." WABI. Vol. 3692. 2005.
#
#Input
#	g: the graph 
#	k: the size of motifs
#Output:
#	motifs: a list of motifs computed on the graph
def enumerate_motifs(g,k):
	vext = []
	motifs = set()
	
	for node in sorted(g.nodes()):   # For each vertex , make a list of its neighbours
		neighbors = sorted(g.neighbors(node))
		
		neighbors_tmp = []
		for neighbor in neighbors:
			if neighbor > node:
				neighbors_tmp.append(neighbor)
		
		while len(neighbors_tmp) > 0: 

			vext = list(sorted(neighbors_tmp))
			extend_motif([node],vext,k,g,motifs)
			
			if neighbors_tmp:
				neighbors_tmp.pop(0)
	
	return motifs

def extend_motif(vsub, vextension, k, g, realsub):
	
	if len(vsub) == int(k):
		vsub_ordered =  sorted(vsub, key=lambda x: int(x))
		t_vsub = tuple(vsub_ordered)
		realsub.add(t_vsub)
		return	
	
	while len(vextension) > 0:
		
		ele = vextension.pop(0)
		vextension_first = vextension[:]
		
		for n in sorted(g.neighbors(ele)):
			if nexclusive(g,n,vsub) and n not in vextension_first and n > vsub[0]:
				vextension_first.append(n)
		
		if ele not in vsub:
			vsub.append(ele)
		extend_motif(vsub,vextension_first,k,g,realsub)
		if ele in vsub:
			vsub = vsub[:-1]
		
		
def nexclusive (g, n, vsub):
	for e in vsub:
		if n in g.neighbors(e):
			return False
	return True