# SuperNoder
SuperNoder is a python tool that enables increasing understable knowledge of networks by means of collapsing of frequent motifs.
It requires python 2.7 to be used.

# Example of use in default mode:
python main.py

# Parameters:
'-h', '--help': print the list of parameters
'-e', '--efile' <file_name>: the file of edges. Default: edges.txt
'-n', '--nfile' <file_name>: the file of nodes. Default: nodes.txt
'-s', '--size' <value>: the size of motifs that the software has to look for. Default: 3
'-d', '--direct': a flag to indicate if the input network is direct. Default: networks are managed as undirect
'-w', '--workspace' <path/directory>: the directory that will be used as workspace. Default: ./
'-l', '--levels' <value>: the number of supernodes levels that the software must reach. Default: 1
'-m', '--mode' <heuristic>: the heuristic the user want to use. It can be h1, h2, h3, h4, h5. Default: h1
'-t', '--threshold' <value>: the threshold employed to evalute the relevance of motifs. Default: 1
'-r', '--repetition-times' <value>: the number of shufflings that h1 has to use. Default: 5
'-k', '--samples-size' <value>: the size of samples of h2 or h5. Default: 100





