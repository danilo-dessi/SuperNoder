from support_functions import *
from collections import Counter
import random
import networkx.algorithms.approximation as apx
import networkx.algorithms.clique as cl
import sys
import numpy as np
import scipy as sp
#sys.setrecursionlimit(10000)

#The function checks if the two motifs share a node
#Input
#	motif1 & motif2: the two motifs which the overlap must be checked
#Output
#	n_collisions: the number of overlapping nodes
#	collisions: the list of overlapping nodes 
def check_overlap(motif1, motif2):
	collisions = set(motif1) & set(motif2)
	n_collisions = len(collisions)
	return n_collisions, collisions
	
#The function checks if there are overlps between motifs. When an overlap is found
# it returns a boolean value and indexes of motifs.	
def find_overlaps(motifs):
	control = False	
	node_to_motifs = {}	
	for i in range(len(motifs)):
		for node in motifs[i]:
			if int(node) not in node_to_motifs:
				node_to_motifs[int(node)] = i
			else:
				return True, node_to_motifs[int(node)], i 
	return False, -1, -1
	
#Greedy Elimination
#The function takes the graph and the list of all motifs and returns a list of disjoint motifs
#Input
#	motifs: the list of motifs 
#Output:
#	mis: the list of disjoint motifs	
def h1(motifs):
	mis = []
	random.shuffle(motifs)
	for motif in motifs:
		n = 0
		for supernode in mis:
			n, c = check_overlap(motif, supernode)	#sub[0]		
			if n > 0:
				break
		if n == 0:
			mis += [motif]
	return mis

#See reference [8]	
def ramsey(g):
	if len(g.nodes()) == 0:
		return set([]), set([])
	v = random.choice(g.nodes())
	
	neighbors = set(g.neighbors(v))
	noneighbors = (set(g.nodes()) - neighbors) - set([v])
	c1, i1 = ramsey(g.subgraph(neighbors))
	c2, i2 = ramsey(g.subgraph(noneighbors))
	
	c1.add(v)
	i2.add(v)
	c = set([])
	i = set([])
	
	if len(c1) >= len(c2):
		c = c1
	else:
		c = c2
		
	if len(i1) >= len(i2):
		i = i1
	else:
		i = i2
	
	return c,i
	
#See reference [8]	
def clique_removal(g):
	g1 = g.copy()
	index = 1
	c = {}
	i = {}
	
	c[index], i[index] = ramsey(g1)
	while len(g1.nodes()) > 0:
		g1.remove_nodes_from(c[index])
		index += 1
		c[index], i[index] = ramsey(g1) 
		
	max_mis = set([])
	for key in i:
		if len(i[key]) > len(max_mis):
			max_mis = i[key]
	return max_mis, c
	
#Ramsey
#The function returns a list of disjoint motif
#Input
#	motifs: the list of motifs 
#	k: the size of samples
#Output:
#	motifs: the reduced list of disjoint motifs	
def h2(motifs, k):
	overlaps_flag = True
		
	while overlaps_flag:
		candidates = set()
		
		#assignament of an id to each motif
		flags = list()	
		for i in range(len(motifs)):
			flags += [i]
	
		#set of indexes to use as sample. Randomly k nodes are chosen and used in the sample.
		while len(flags) > 0:		
			i = 0
			sample = []
			while i < k and len(flags) > 0:
				n = random.randint(0, len(flags) - 1)
				entry = flags[n]
				sample += [entry]
				flags.pop(n)
				i += 1
			
			#for each node the list of motifs that contain it is computed
			node_to_motifs = {}
			for i in range(len(sample)):
				motif = motifs[sample[i]]
				for node in motif:
					if int(node) not in node_to_motifs:
						node_to_motifs[int(node)] = set()
					node_to_motifs[int(node)].add(sample[i])
			
			# On motifs that compose the sample a graph is built. Motifs are nodes, Edges are between nodes of
			# overlapping motifs 
			g = nx.Graph()
			for node in node_to_motifs:
				new_edges = list(itertools.combinations(node_to_motifs[node],2))
				g.add_nodes_from(node_to_motifs[node])
				g.add_edges_from(new_edges)
			t = time.time()
			
			#Ramsey application on the built graph
			s, l = clique_removal(g)			
			
			#Union of temporary disjoint motifs from each sample. 
			#test = [motifs[m] for m in s]
			candidates = candidates | s
		
		#check if in the union of candidates there are overlaps
		motifs = [motifs[m] for m in candidates]
		overlaps_flag,_,_= find_overlaps(motifs)
	
	return motifs


#Ranked Elimination
#The function takes the graph and the list of all motifs and returns a list of disjoint motifs
#Input
#	g: the graph that represents the networkx
#	motifs: the list of motifs 
#Output:
#	supernodes: the list of disjoint motifs
def h3(g, motifs):

	nodes = g.nodes()
	edges_list = g.edges()
	
	#computation of the degree of each node
	degrees_nodes_dict = get_nodes_degree(g)

	#computation of the degree of each possible motif, the degree is the sum of the nodes degree without considering internal connections
	degrees_motifs_dict = get_motifs_degrees(g, motifs, degrees_nodes_dict)
	
	#creation of subsets of candidate supernodes for each node. The list of candidates is ordered by criteria (currently by external degrees)
	nodes_motifs_dict = get_motifs_set(nodes, motifs)
	nodes_motifs_dict = order(nodes_motifs_dict, degrees_motifs_dict)
	
	for node in nodes_motifs_dict:
		nodes_motifs_dict[node] = nodes_motifs_dict[node][:1]		

	#research of supernodes, at the beginning each supenode is the motif with minimum external degree
	supernodes = []
	index = {}		
	for node in nodes_motifs_dict:
		list_motifs = nodes_motifs_dict[node]
		index[node] = 0
		if len(list_motifs) >= 1 and list_motifs[0] not in supernodes : 
			supernodes += [list_motifs[0]]
	
	#the loop continues while there are collisions between supernodes
	check = True	
	start = 0
	while check:
		
		#searching of overlapping supernodes
		check, i, j = find_overlaps(supernodes)
		start = i
		
		#check between the degrees of collident supernodes, the motif with the highest degree will be deleted
		if check and degrees_motifs_dict[str(supernodes[i])] > degrees_motifs_dict[str(supernodes[j])]:
			del supernodes[i]			
					
		elif check and degrees_motifs_dict[str(supernodes[i])] < degrees_motifs_dict[str(supernodes[j])]:
			del supernodes[i]			

		#if the sum degree is the same, a random choice is done to remove one motif
		elif check and degrees_motifs_dict[str(supernodes[i])] == degrees_motifs_dict[str(supernodes[j])]:
			h = random.choice([i,j])		
			del supernodes[h]
	
	return supernodes
	
#Ranked Elimination V2
#The function takes the graph and the list of all motifs and returns a list of disjoint motifs
#Input
#	g: the graph that represents the networkx
#	motifs: the list of motifs 
#Output:
#	supernodes: the list of disjoint motifs	
def h4(g, motifs):

	nodes = g.nodes()
	edges_list = g.edges()
	motifs_copy = list(motifs)
	supernodes_final = []
	g_copy = g.copy()
	
	while len(motifs_copy) > 0:
		covered_nodes = set()
		
		#computation of the degree of each node
		degrees_nodes_dict = get_nodes_degree(g_copy)

		#computation of the degree of each possible motif, the degree is the sum of the nodes degree
		degrees_motifs_dict = get_motifs_degrees(g, motifs_copy, degrees_nodes_dict)
		
		#creation of subsets of candidate supernodes for each node. The list of candidates is ordered by criteria (currently by external degrees)
		nodes_motifs_dict = get_motifs_set(nodes, motifs_copy)
		nodes_motifs_dict = order(nodes_motifs_dict, degrees_motifs_dict)
		
		for node in nodes_motifs_dict:
			nodes_motifs_dict[node] = nodes_motifs_dict[node][:1]		

		#research of supernodes, at the beginning each supenode is the motif with minimum external degree
		supernodes = []
		index = {}		
		for node in nodes_motifs_dict:
			list_motifs = nodes_motifs_dict[node]
			index[node] = 0
			if len(list_motifs) >= 1 and list_motifs[0] not in supernodes : 
				supernodes += [list_motifs[0]]
		
		#the loop continues while there are collisions between supernodes
		check, i, j = find_overlaps(supernodes)	
		start = 0
		while check:
			
			#searching of overlapping supernodes
			#check, collisions, i, j = find_overlapping(supernodes, start)
			check, i, j = find_overlaps(supernodes)
			start = i
			
			#check between the degrees of collident supernodes, the motif with higher degree will be deleted
			if check and degrees_motifs_dict[str(supernodes[i])] > degrees_motifs_dict[str(supernodes[j])]:
				del supernodes[i]			
						
			elif check and degrees_motifs_dict[str(supernodes[i])] < degrees_motifs_dict[str(supernodes[j])]:
				del supernodes[i]			

			#if the sum degree is the same, a random choice is done to remove one motif
			elif check and degrees_motifs_dict[str(supernodes[i])] == degrees_motifs_dict[str(supernodes[j])]:
				h = random.choice([i,j])		
				del supernodes[h]
		
		# check which nodes belong to a supernode
		for s in supernodes:
			supernodes_final += [s]
			for node in s:
				covered_nodes.add(node)
				g_copy.remove_node(node)
		
		#for subsequent steps, all motifs with orphan nodes are considered (i.e. all motifs that have a node that has already
		# been considered are removed
		motifs_copy_tmp = []
		for motif in motifs_copy:
			if len(set(motif) & covered_nodes) == 0:
				motifs_copy_tmp += [motif]
		motifs_copy = motifs_copy_tmp
			
	return supernodes_final
	
	
def h5(motifs, k):
	check, i, j = find_overlaps(motifs)	
		
	while check:
		mis = set()
		
		#assignament of an id to each motif
		flags = list()	
		for i in range(len(motifs)):
			flags += [i]
	
		#set of indexes to use as sample
		while len(flags) > 0:		
			i = 0
			sample = []
			while i < k and len(flags) > 0:
				n = random.randint(0, len(flags) - 1)
				entry = flags[n]
				sample += [entry]
				flags.pop(n)
				i += 1
			
			#for each node the list of motifs that contain it is built
			node_to_motifs = {}
			for i in range(len(sample)):
				motif = motifs[sample[i]]
				for node in motif:
					if int(node) not in node_to_motifs:
						node_to_motifs[int(node)] = set()
					node_to_motifs[int(node)].add(i)
 
			m = np.zeros((len(sample), len(sample)))
			
			#for each sample, a adiacency matrix (from Nodes to Nodes) is built. Nodes are motifs.
			# There is a 1 if motifs overlap.
			for node in node_to_motifs:
				edges = list(itertools.combinations(node_to_motifs[node],2))
				for edge in edges:
					m[edge[0], edge[1]] = 1
					m[edge[1], edge[0]] = 1
					
			collisions = True
			
			while collisions:
				sum = m.sum(axis=1).tolist()
				
				degree = {}
				for i in range(len(sample)):
					degree[i] = sum[i]
					
				#there are not collisions where matrix contains only zeros
				collisions = not all(v == 0 for v in degree.values())

				if collisions:
					sorted_degree = sorted(degree.items(), key=operator.itemgetter(1),reverse=True)
					i_to_remove = sorted_degree[0][0]
					del sample[i_to_remove]
					m = np.delete(m, i_to_remove, 0) # 0 = rows
					m = np.delete(m, i_to_remove, 1) # 1 = cols
			
			mis = mis | set(sample) #union
			
		motifs = [motifs[m] for m in mis]
		check, i, j = find_overlaps(motifs)	
		
		
	return motifs	
	


		
		