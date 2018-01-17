import subprocess
import sys
import getopt
import os
import collections
import textwrap
import operator
import ast
from random import shuffle
import networkx as nx
from networkx.algorithms.approximation import independent_set
from networkx.algorithms import isomorphism as iso
from networkx.algorithms.approximation import clique
from networkx.algorithms import operators
from networkx.algorithms import clique as cq
import itertools
import random
import time
import json
import random


#This function computes the degree of each node of the network
#Input:
#	g: the graph	
#Output:
#	nodes_degree: a dictionary where to each node its degree is associated
def get_nodes_degree(g):
	nodes_degrees = {}
	for node in g.nodes():
		nodes_degrees[node] = g.degree(node)
	return nodes_degrees


#Return the degree of one motif making the sum of nodes degree
#Input:
#	motif: a motif
#	degrees_nodes_dict: a dictionary where for each node its degree is associated
#Output:
#	degree: the sum of the degree of the nodes
def get_motif_degree(motif, degrees_nodes_dict):
	degree = 0
	for node in motif:
		degree += degrees_nodes_dict[node]
	return degree

	
#This function computes the sum of the degrees of nodes for each motif
#Input:
#	motifs: a list of motifs
#	degrees_nodes_dict: a dictionary where for each node its degree is associated
#Output:
#	degree: a dictionary where to each motif the sum of the degree of its nodes is associated
def get_motifs_degrees(g, motifs, degrees_nodes_dict):
	motifs_degrees  = {}
	for motif in motifs:
		subg = g.subgraph(motif)
		motifs_degrees[str(motif)] = get_motif_degree(motif, degrees_nodes_dict) - 2*len(subg.edges())
	return motifs_degrees
			
#This function computes the of motif where each node could be inserted
#Input
#	nodes_dict: a dictionary or a list of nodes
#	motifs: a list of all motifs that have been previously computed on the graph
#Output
#	nodes_motif_dict: a dictionary where to each node a list of motifs is associated
def get_motifs_set(nodes_dict, motifs):
	nodes_motifs_dict = {}

	for node in nodes_dict:
		list_of_motifs = []
		for motif in motifs:
			if node in motif:
				list_of_motifs += [motif]
		
		nodes_motifs_dict[node] = list_of_motifs

	return nodes_motifs_dict

#This function orders lists of motifs based on the sum of their nodes degree
#Input
#	nodes_motifs_dict: a dictionary where to each node a list of motifs is associated 
#	degrees_motifs_dict: a ditionary where to each motif is assoiciated the sum of their nodes degree
#Output
#	ordered_nodes_motifs_dict = a dictionary where to each node an ordered list of motifs is associated
def order(nodes_motifs_dict, degrees_motifs_dict):
	ordered_nodes_motifs_dict = {}
	for node in nodes_motifs_dict:
		list_string = [str(e) for e in nodes_motifs_dict[node]]
		list_string_ordered = sorted(list_string, key=degrees_motifs_dict.__getitem__)
		ordered_nodes_motifs_dict[node] = [ast.literal_eval(e) for e in list_string_ordered]
	return ordered_nodes_motifs_dict
					



#This function remove  a motif from a list of motif
#Input
#	motif: the motif to remove
#	motifs_list: the list of motifs
#Output:
#	motifs_list: the list of all motifs without motif
def remove_motifs(motif, motifs_list):		
	indexes_to_delete = []
	for i in range(0, len(motifs_list)):
		print motif, motifs_list[i]
		if set(motif) == set(motifs_list[i]):
				indexes_to_delete += [i]	
	print indexes_to_delete
	motifs_list = [i for j, i in enumerate(motifs_list) if j not in indexes_to_delete]
	
	return motifs_list
	

#This function computes the internal edges of a motif
#Input:
#	motif: a motif
# 	edge_list: the list of the graph edges
#Output:
#	motif_edges: the edges of the motif
def get_motif_edges(motif, g):
	motif_edges = []
	for i in range(0, len(motif) - 1):
		for j in range(i + 1, len(motif)):
			if g.has_edge(motif[i], motif[j]):
				motif_edges += [(motif[i], motif[j])]
			#for edge in edges_list:
			#	if motif[i] in edge and motif[j] in edge:
			#		motif_edges += [(motif[i], motif[j])]
	#print motif, motif_edges
	return motif_edges
					

#This function returns the labels of an edge 
def get_labeled_edge(edge, nodes_dict):	
	return (nodes_dict[edge[0]], nodes_dict[edge[1]])	


#This function is used to detect all motifs that contain at least a node shared with sub.
#Input:
#	sub: the motif to remove
#	motifs: a list of motifs
#Output:
#	removing_list: the list of motifs
def removing_motifs(sub, motifs):
	removing_list = []
	for node in sub:
		for motif in motifs:
			if node in motif and motif not in removing_list:
				removing_list += [motif]
	return removing_list



#This function is used to count how many motifs of each type there are.
#Input:
#	motifs: the list of motifs
#	g: the graph
# 	nodes_dict: a dictionary of nodes -> labels
# 	undirect: a flag that indicates if the work mode is directet (False) or undirect (True)
#	threshold: the threshold to consider a motif relevant
#Output:
#	removing_list: the list of motifs	
def get_recurrent_motifs(motifs, g, nodes_dict, undirect, threshold):

	c = {}#counter
	motif_descriptors = []
	
	if threshold == 1:
		return motifs, -1
	
	for motif in motifs:
		descriptor = []
		g1 = g.subgraph(motif)
		g1 = nx.DiGraph(g1.edges())
		for node in motif:
			flag = False#check if the label has been already put in the count or if it is new
			label_node = nodes_dict[node]
			in_degree = g1.in_degree(node)
			out_degree = g1.out_degree(node)
			 
			for e in descriptor:
				if e[0] == label_node:
					e[1] += 1
					e[2] += in_degree
					e[3] += out_degree
					flag = True
			if not flag:
				descriptor += [[label_node, 1, in_degree, out_degree]]
				
		descriptor = [tuple(x) for x in descriptor]
		descriptor = tuple(sorted(descriptor))
		
		motif_descriptors += [descriptor]
		if descriptor not in c:
			c[descriptor] = 0
		c[descriptor]  += 1
	
	#only motifs that meet the thresholds are subsequently considered to check if they are really isomorphic
	selected_keys = set([x for x in c.keys() if c[x] >= threshold])
	hold_motifs = []
	for i in range(len(motif_descriptors)):
		if motif_descriptors[i] in selected_keys:
			hold_motifs += [motifs[i]]
	
	#for each motifs, a subgraph is built.
	motifs_subgraphs_list = []
	for i in range(len(hold_motifs)):
		if undirect:
			g1 = nx.Graph()
		else:
			g1 = nx.DiGraph()
			
		g1.add_nodes_from(hold_motifs[i])
		g1.add_edges_from(get_motif_edges(hold_motifs[i], g))
		
		for node in hold_motifs[i]:
			g1.node[node] = nodes_dict[node]
		
		motifs_subgraphs_list += [g1]
	
	#check of isomorphisms. Isomorphic motifs are indexed by the same key
	iso_dict = {}
	key_generator = 0
	for i in range(len(motifs_subgraphs_list)):
		iso = False
		for key in iso_dict:
			if undirect:
				iso = isomorphism(iso_dict[key][0], motifs_subgraphs_list[i])
			else:
				iso = isomorphism_directed(iso_dict[key][0], motifs_subgraphs_list[i])
			
			if iso:
				iso_dict[key] += [motifs_subgraphs_list[i]]
				break
		if not iso:
			iso_dict[key_generator] = [motifs_subgraphs_list[i]]
			key_generator += 1
	
	#count of motifs for each key. If the count is over the threshlold all motifs are kept.
	hold_motifs = []
	types = 0
	for key in iso_dict:
		if len(iso_dict[key]) >= threshold:
			hold_motifs += [x.nodes() for x in iso_dict[key]]
			types += 1
			
	return hold_motifs, types

	
	
def node_equals(attributes_n1, attributes_n2):	
	return attributes_n1 == attributes_n2
		
			
#This function is used to compute the isomorphism between two undirect graphs.
def isomorphism(g1, g2):	
	matcher = iso.GraphMatcher(g1, g2, node_match = node_equals)	
	return matcher.is_isomorphic()

#This function is used to compute the isomorphism between two directed graphs
def isomorphism_directed(g1, g2):
	matcher = iso.DiGraphMatcher(g1, g2, node_match = node_equals)
	return matcher.is_isomorphic()
	
	
	
#This function computes the adiacency matrix of a motif. It puts a 0 if there is not an edge between two nodes, 1 otherwise.
#The adiacency matrix is represented by a binary string.
#Input:
#	motif: the list of nodes of the motif	
#	motif_edges: the list of edges of the motif
#Output:
#	the string that represents the adiacency matrix
#def get_motif_type(motif, motif_edges):
#	motif_type = ""
#	nodes = ast.literal_eval(motif)
#	for i in range(0, len(nodes)):
#		for j in range (0, len(nodes)):
#			if (nodes[i], nodes[j]) in motif_edges or (nodes[j], nodes[i]) in motif_edges:
#				motif_type += "1"
#			else:
#				motif_type += "0"
#	return motif_type


#This function is used to computes the type for each motif
#Input:
#	motifs: the list of all motifs
#	motifs_edges: a dictionary where the key is the motif and the value is the list of it edges
#Output:
#	types: the dictionary where the key is the motif and the value is the string of its adiacency matrix
#
#def get_motifs_type(motifs, motifs_edges):
#	types = {}
#	for motif in motifs:
#		types[motif] = get_motif_type(ast.literal_eval(motif), motifs_edges[motif])
#	return types
		

#This function remove all self edges that are present into a list	
def remove_self_edges(edges_list):
	tmp_edges_list = list(edges_list)
	for edge in edges_list:
		lst = list(edge)
		if ( len(set(lst)) < len(lst) ):
			tmp_edges_list.remove(edge)
	return tmp_edges_list

#def motif2string(motif):
#	s = ""
#	for node in motif:
#		s = s + str(node) + "-"
#	return s[:-1]

#This function is used to remove the edges of nodes that have been replaced by a supernode
def remove_nonexistent_edges(edges_list, nodes_dict):
	flag = False
	new_edges_list = []
	for edge in edges_list:
		for node in nodes_dict:
			if node in edge:
				flag = True
				break
		if flag:
			flag = False
			new_edges_list += [edge]

	return new_edges_list
