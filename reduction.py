from support_functions import *

#This function substitutes all motifs more frequent that a given value with a supernode.
#This function computes all labels of a motif 
def get_labels(motif, nodes_dict):
	motif_labeled = ""
	for node in ast.literal_eval(motif):
		#print nodes_dict[node], motif_labeled
		motif_labeled = motif_labeled + nodes_dict[node] + "-"
	
	return motif_labeled[:-1]
	
#This function substitutes all motifs more frequent that a given value with a supernode.
#This function computes all labels of a motif 
def labels(motif, nodes_dict):
	motif_labeled = ""
	for node in motif:
		#print nodes_dict[node], motif_labeled
		motif_labeled = motif_labeled + nodes_dict[node] + "-"
	
	return motif_labeled[:-1]



#Input:
#	nodes_dict: the dictionary key_node:label of all nodes of the network
#	edges_list: the list of all edges of the network
#	sets_of_isomorphic_supernodes: the dictionary that contains all list of isomorphic supernodes
#	threshold: it represents the threshold over which motifs are substituited by supernodes
#Output:
#	nodes_dict: the dictionary of nodes of the updated network
#	edges_list: the list of edges of the updates network
def reduction(supernodes, nodes_dict, g):
	edges_list = g.edges()
	last_id = max(map(int, nodes_dict)) + 1

	for supernode in supernodes:
		last_id = last_id + 1
		label = labels(supernode, nodes_dict)
		nodes_dict[str(last_id)] = label
		
		for node in supernode:
			#add all links of the node to the supernodes
			new_edges_list = []
			
			#the list of edges is updated for each interaction keeping all edges that are not involved in the motif
			#and changing edges that are involved in the motif. 
			for edge in edges_list:
				if node not in edge:
					new_edges_list += [edge]
				else:
					new_edge = []
					for e in edge:
						if e == node:
							new_edge += [str(last_id)]
						else:
							new_edge += [e]
					new_edges_list += [tuple(new_edge)]

			edges_list = new_edges_list
			
			#remove the node from the list of nodes
			del nodes_dict[node]

	edges_list = remove_nonexistent_edges(edges_list, nodes_dict)	
	edges_list = remove_self_edges(edges_list)
	edges_list = list(set(edges_list))
	
	return nodes_dict, edges_list
	
	

def graph_reduction(nodes_dict, edges_list, motifs, sets_of_isomorphic_supernodes, threshold, level):
	last_id = max(map(int, nodes_dict)) + 1		

	#for each subset which occurs at least threshold times
	for motif_id in sets_of_isomorphic_supernodes:
		if len(sets_of_isomorphic_supernodes[motif_id]) >= threshold:
			
			motif_labels = get_labels(motif_id, nodes_dict)
			#motif_type = get_motif_type(motif_id, edges_list)
						
			for motif in sets_of_isomorphic_supernodes[motif_id]:
					
				#generation of a new id for the supernode which is not present into the dict of nodes
				last_id = last_id + 1

			
				nodes_dict[str(last_id)] = motif_labels
			
				for node in motif:
					
					#add all links of the node to the supernodes
					new_edges_list = []
					
					#the list of edges is updated for each interaction keeping all edges that are not involved in the motif
					#and changing edges that are involved in the motif. 
					for edge in edges_list:
						if node not in edge:
							new_edges_list += [edge]
						else:
							new_edge = []
							for e in edge:
								if e == node:
									new_edge += [str(last_id)]
								else:
									new_edge += [e]
							new_edges_list += [tuple(new_edge)]

					edges_list = new_edges_list
					
					#remove the node from the list of nodes
					del nodes_dict[node]		
	
	#final cleanings of edges
	edges_list = remove_nonexistent_edges(edges_list, nodes_dict)	
	edges_list = remove_self_edges(edges_list)
	edges_list = list(set(edges_list))
	
	return nodes_dict, edges_list