from support_functions import *

#The functions reads two file: a file of labels and a file of edges.
#The function receives the workspace and the names of files that descibe the network,
#and returns a graph g, the dictionary of nodes with their labels, and the list of edges.
#
#In the file of labels there is a row of each node which is represented by a pair key label
#example:
#key_node_1 1 label_1
#key_node_2 label_2
#key_node_3 label_3
#
#The second file contains a row for each edge of the network.
#each row of the file must have the following structure:
#key_node_x, key_node_y, w
#that means that there is an edge between the nodes x and y with weight w
def load_graph(workspace, graphfile, labelfile, undirect):

	nodes_dictionary = {}
	edges_list = []
	labels = {}
	if undirect:
		g = nx.DiGraph()	
	else:	
		g = nx.Graph()
	
	with open(workspace + labelfile, "rb") as f:
		n_row = 1
		for row in f:
			
			list_row = row.split()				
			if len(list_row) >= 1:
				nodes_dictionary[list_row[0]] = list_row[1]	 	
				g.add_node(list_row[0], label=list_row[1])
				#g.node[list_row[0]] = list_row[1]
			
			n_row += 1
	
	with open(workspace + graphfile, "rb") as f:
		for row in f:
			list_row = row.split()
			
			#adding edge
			if len(list_row) > 1 and list_row[0] in nodes_dictionary and list_row[1] in nodes_dictionary and list_row[0] != list_row[1]:#len(edges_list) < 3500 and \
				g.add_edge(list_row[0], list_row[1])
				
	edges_list = g.edges()					
	
	return g, nodes_dictionary, edges_list
	

#This function is used for generating two files which describe an input graph
#Input:
#	nodes_dict: the dictionary of nodes of a graph
#	edges_list: the list of edges of the graph
# 	level: the level of the graph we are working with
#Output:
#	nothing
def print_output(nodes_dict, edges_list, motifs, supernodes, nodes_dict_original, level):
	
	try:
		if not os.path.exists("./output-resources"):
			os.makedirs("./output-resources")
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			print "output-resources directory creation has failed"
			exit(1)
		
	with open("./output-resources/OUT_L" + str(level) + "_NODES.txt", "w") as nodes_file:
		for node in nodes_dict:
			nodes_file.write(node + " " + nodes_dict[node] + "\n")

	with open("./output-resources/OUT_L" + str(level) + "_EDGES.txt", "w") as edges_file:
		for (n1,n2) in edges_list:
			edges_file.write(n1 + " " + n2 + "\n")
			
	with open("./output-resources/OUT_L" + str(level) + "_SUPERNODES.txt", "w") as edges_file:
		
		for s in supernodes:
			ids = ""
			labels = ""
			for id in s:
				ids += str(id) + " "
				labels += nodes_dict_original[id] + " "
			edges_file.write(ids + labels + "\n")
			
	with open("./output-resources/OUT_L" + str(level) + "_MOTIFS.txt", "w") as edges_file:
		
		for s in motifs:
			ids = ""
			labels = ""
			for id in s:
				ids += str(id) + " "
				labels += nodes_dict_original[id] + " "
			edges_file.write(ids + labels + "\n")
	return
	
	

			
	
	
	
	
	
	