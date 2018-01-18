# SuperNoder
This repository contains the SuperNoder resources, the main outcome of the work: SuperNoder: progressive collapsing of networks through the discovery of disjoint motifs.

SuperNoder is a python tool that enables the simplification of networks by means of collapsing of their frequent motifs.
It requires python 2.7 to be used.

# Example of use:
Default mode: python main.py

Others:

python main.py -e my_edges.txt -n my_nodes.txt -s 3 -l 1 -m h1 -t 20

python main.py -e my_edges.txt -n my_nodes.txt -s 3 -l 1 -m h1 -t 20 -w path/

python main.py -e my_edges.txt -n my_nodes.txt -s 4 -l 1 -m h1 -t 20 -w path/ -l 5

python main.py -e my_edges.txt -n my_nodes.txt -s 3 -l 1 -m h2 -t 20 -w path/ -s 50

python main.py -e my_edges.txt -n my_nodes.txt -s 3 -l 1 -m h5 -t 20 -w path/ -s 50

python main.py -e my_edges.txt -n my_nodes.txt -s 3 -l 1 -m h1 -t 20 -w path/ -r 10


# Parameters:
'-h', '--help':                     print the list of parameters

'-e', '--efile' <file_name>:        the file of edges. Default: edges.txt

'-n', '--nfile' <file_name>:        the file of nodes. Default: nodes.txt

'-s', '--size' <value>:             the size of motifs that the software has to look for. Default: 3
  
'-d', '--direct':                   a flag to indicate if the input network is direct. Default: networks are managed as undirect

'-w', '--workspace' <directory>:    the directory that will be used as workspace. Default: ./

'-l', '--levels' <value>:           the number of supernodes levels that the software must reach. Default: 1
  
'-m', '--mode' <heuristic>:         the heuristic the user want to use. It can be h1, h2, h3, h4, h5. Default: h1
  
'-t', '--threshold' <value>:        the threshold employed to evalute the relevance of motifs. Default: 1
  
'-r', '--repetition-times' <value>: the number of shufflings that h1 has to use. Default: 5
  
'-k', '--samples-size' <value>:     the size of samples of h2 or h5. Default: 100
  
# Format of input files:
nodes.txt

1 A

2 A

3 B

4 C

5 D

6 B

edges.txt

1 2

1 5

2 4

3 5

4 6

# Output
Output of the tool is placed in a directory 'output-resources'. The directory contains nodes, edges, list of motifs, and list of supernodes for each level of recursion. Example if l = 2 there will be the following files:

OUT_L1_NODES.txt        ->  the list of nodes of the reduce network

OUT_L1_EDGES.txt        ->  the list of edges of the reduced network

OUT_L1_MOTIFS.txt       ->  the list of all motifs computed on the original network

OUT_L1_SUPERNODES.txt   ->  the list of motifs collapsed in supernodes.

OUT_L2_NODES.txt

OUT_L2_EDGES.txt

OUT_L2_MOTIFS.txt 

OUT_L2_SUPERNODES.txt

# Test Folder
The folder 'test' contains our mapping of the yeast network nodes on five levels of the Gene-Ontology terms ontology.
The original labels of nodes and edges of the network are available in http://vlado.fmf.uni-lj.si/pub/networks/data/bio/yeast/yeast.htm
Please note that the edge file will have to contain only the list of edges as above explained.

