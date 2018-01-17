import subprocess
import sys
import getopt
import os
import time
from support_functions import *
from read_write_operations import *
from enumeration import *
from reduction import *
from heuristics import *


def controller():

	n_arguments = len(sys.argv)
	list_of_arguments  = sys.argv

	graphfile = 'net.txt'			#default file name that contans the edges
	nodes = 'nodes.txt'				#default file name of the file that contains the nodes
	#outputfile = 'out.txt'			#default file name of the file with
	#networkfile = "net_net.txt"
	motif_size = '3'				#default motif size
	workspace = './'				#default workspace is the directory where the program is executed
	undirect = True					#this paramenter indicates if the network is directed or not. It is necessary when mfinder software is adopted
	mode = "h1"						#the dafault mode is the complete maximum independent set on all supernodes. It requires long time to be exeuted.
	nodes_dict = {}					#this variable contains the nodes with their labels
	edges_list = []					#this variable is a list of pairs, where each pair is and edge and contains the ids of nodes
	motifs = []						#this variable contains the list of all computed motifs
	supernodes_edges = {}			#this disctionary contains for each motif the list of edges between its nodes
	#frequency = []					#frequency is a variable that is adopted to count how many times a motif occurs
	sets_of_isomorphic_supernodes = {} #this variable contains lists where into each list, each supernode is isomorphic to others.
	threshold = 1					#threshold indicates the times that a motif must occur to be kept and transformed in a supernodes
	number_levels = 1				#this indicates the number of hierarchical levels the code has to be performed on temporary results
	#greedy = False					#this variable is a flag that can be activated by the user. When its value is True it splits the original graph into subgraphs to make faster the motifs computation
	#greedy_size = 100				#this variable indicate the size of subgraphs in case greedy == True. It can be also set by the user
	#greedy_split_times = 10		# this variable indicates the times that the greedy approach will be performed to compute possible subgraphs
	repetition_times = 5			#this variable indicates how many times the iset greedy will be applied on the set of motifs
	motifset = set()
	samples_size = 1000
		
	#management of user's parameter
	try:	
		opts, args = getopt.getopt(list_of_arguments[1:],"hr:e:n:l:o:ds:w:m:t:k:",["help","repetition-times=","efile=","nfile=", "levels",  "ofile=", "direct", "size=", "workspace=", "direct", "mode=", "threshold=", "samples-size"])
			
		for opt, arg in opts:
			if opt == '-h':
				print 'motif_discovery.py -e <edgefile> -n <nodes> -s <size-of-motifs> [-o <outputfile>] [-d, --direct] [-w <workspace>] [-m, --mode] [-t, --threshold] [-l <--levels>] [-g, --greedy-split-size] [-j, --greedy-split-times] [-k, --greedy-iset-times]'
			elif opt in ("-e", "--efile"):
				graphfile = arg
			elif opt in ("-o", "--ofile"):
				outputfile = arg
			elif opt in ("-s", "--size"):
				motif_size = arg
			elif opt in ("-d", "--direct"):
				undirect = False
			elif opt in ("-w", "--workspace"):
				workspace = arg
				p = subprocess.Popen(['mkdir', workspace])
				p.wait()
				print arg, "is the new workspace."
			elif opt in ("-n", "--nfile"):
				nodes = arg
			elif opt in ("-l","--levels"):
				number_levels = int(arg)
			elif opt in ("-m","--mode"):
				mode = arg
			elif opt in ("-t","--threshold"):
				threshold = int(arg)
			elif opt in ("-r","--repetition-times"):
				repetition_times = int(arg)
			elif opt in ("-k","--samples-size"):
				samples_size = int(arg)	
		
	except getopt.GetoptError:
		print 'motif_discovery.py -e <edgefile> -n <nodes> -s <size-of-motifs> [-o <outputfile>] [-d, --direct] [-w <workspace>] [-m, --mode] [-t, --threshold] [-l <--levels>] [-g, --greedy-split-size] [-j, --greedy-split-times] [-k, --greedy-iset-times]'
		sys.exit(2)
	
	#mode can only take some values to activate the chosen operation-mode
	if mode not in ["h1", "h2", "h3", "h4", "h5"]:
		print "selected mode is not valid", mode
		exit(4)

	try:
		#if the number of leveles is higher than one, then all operation are repeated.
		#the software directly performs the algorithm on each level and save outputs for each one.
		for level in range(1, number_levels + 1):
			print "level-----> " , level
			motifs = []
			sets_of_isomorphic_supernodes = {}
			if level > 1:
				nodes = "./output-resources/OUT_L" + str(level - 1) + "_NODES.txt"
				graphfile = "./output-resources/OUT_L" + str(level - 1) + "_EDGES.txt"

			print "MODE:", mode, "SUPERNODES SIZE:", motif_size
			print "file reading..."
			start_time = time.time()
			g, nodes_dict, edges_list = load_graph(workspace, graphfile, nodes, undirect)
			print "THE NETWORK HAS", len(g.nodes()), "NODES AND", len(g.edges()), "EDGES"
			print "file reading...completed in ", str(time.time() - start_time)
			
			#computation of motifs
			start_time = time.time()		
			
			print "Motifs computation by means of enumeration..."
			if undirect:
				motifset = enumerate_motifs(g.to_undirected(),motif_size)	
			else:
				motifset = enumerate_motifs(g,motif_size)	
			
			motifs = [list(x) for x in motifset]
			print "all possible motifs: ", len(motifs), "time: ", str(time.time() - start_time)	

			print "Thresholding..."
			start_time = time.time()
			motifs, count_frequent_types = get_recurrent_motifs(motifs, g, nodes_dict, undirect, threshold)
			if count_frequent_types > 0:
				print "There are", count_frequent_types, "types of motif that occur at least", threshold, "times"
			print "Count of recurrent motifs:", len(motifs), "time: ", str(time.time() - start_time)	
			thresholded_motifs = list(motifs)
			
			#motif selection step
			supernodes = []
			if mode == "h1":
				print "Search of supernodes by means of H1"
				start_time = time.time()
				supernodes = []
				for i in range(repetition_times):				
					tmp_supernodes = h1(g, motifs)
					if len(supernodes) < len(tmp_supernodes):
						supernodes = tmp_supernodes
				print "Supernodes: ",len(supernodes),  " time: ", str(time.time() - start_time)
				
			elif mode == "h2":
				print "Search of supernodes by means of H2"
				supernodes  = h2(motifs, samples_size)
				print "Supernodes: ",len(supernodes),  " time: " ,str(time.time() - start_time)
				
			elif mode == "h3":		
				print "Search of supernodes by means of H3"
				start_time = time.time()
				supernodes = h3(g, motifs)
				print "Supernodes:", len(supernodes), " time: ", str(time.time() - start_time)
				
			elif mode == "h4":
				print "Search of supernodes by means of H4"
				start_time = time.time()
				supernodes = h4(g, motifs)
				print "Supernodes:", len(supernodes), " time: ", str(time.time() - start_time)
				
			elif mode == "h5":
				print "Search of supernodes by means of H5"
				supernodes  = h5(motifs, samples_size)
				print "Supernodes: ",len(supernodes),  " time: " ,str(time.time() - start_time)
			
			print find_overlaps(supernodes)
			#reduction of the network
			nodes_dict_original = dict(nodes_dict)
			nodes_dict_reduction, edge_list_reduction = reduction(supernodes, nodes_dict, g)
			
			print_output(nodes_dict_reduction, edge_list_reduction, thresholded_motifs, supernodes, nodes_dict_original, level)
			print "The final netwrok has", len(nodes_dict_reduction), "nodes and", len(edge_list_reduction), "edges\n"
	except:
		print 'Values errors. Please check your inputs'
		sys.exit(3)
		
if __name__ == "__main__":		
	controller()


	
	
	