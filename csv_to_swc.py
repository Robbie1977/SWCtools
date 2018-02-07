#Script for converting a generated CSV file to an SWC formatted file as well as an id mapped csv file
#CSV files exported by Albert Cardona from his lab's CATMAID software: http://catmaid.readthedocs.io/en/stable/
#Author:Boima Massaquoi

#FILE USEAGE BELOW
#This script has been written for Python 2.7 and assumes you have "python.exe" setup in your path variables
#This must be run through the command prompt.
#Make sure that you use the correct directories for the files that you are acessing
#In the command prompt provide The following Arguments:
#"python" "csv_to_swc.py" ".csv file you want to convert" ".swc outputfile you want to generate"

#IMPORTANT NOTE
#The CSV files are generated from the Cardona Lab CATMAID software have the node xyzr values in the form of nanometers
#This script assumes that the values are in nano meters and uses a conversion factor to convert values from nanometers to micrometers

#factor for converting nanometers to micrometers
um_factor = 1000

import sys
import csv
import operator

#class for holding node data
class nnode(object):
    def __init__(self,n_id,_type,x,y,z,r,p_id):
        self.n_id = int(n_id)
        self._type = _type
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.r = float(r)
        if p_id == '':
            p_id = '-1'
        self.p_id = int(p_id)
    def set_n_id(self,i):
        self.n_id = i
    def set_p_id(self,i):
        self.p_id = i
    def get(self):
        return str(self.n_id)+" "+str(self._type)+" "+str(self.x)+" "+str(self.y)+" "+str(self.z)+" "+str(self.r)+" "+str(self.p_id)

#class for wrapping nnodes into tree nodes   
class tnode(object):
    def __init__(self,n):
        self.node = n
        self.children = []

    def get_children(self):
        return self.children
    def add_child(self,tn):
        self.children.append(tn)

#builds a tree from a "root" tnode
def build_tree(cur_tn,nlist):
    #add all children of current tree node
    for n in nlist:
        if n.p_id== cur_tn.node.n_id:
            tn = tnode(n)
            cur_tn.add_child(tn)

    #build tree continuing with children recursively       
    t_children = cur_tn.get_children()
    for c in t_children:
        build_tree(c,nlist)

#function places tree nodes in correct order with new ids based on tnode heirarchy
def order_tree(tree_list,tn,id_map):
    #assign id based on length of tree
    id_map[str(len(tree_list))]=str(tn.node.n_id)
    tn.node.set_n_id(len(tree_list))
    tree_list.append(tn.node)
    
    children = tn.get_children()
    for c in children:
        #assign parent id to child
        c.node.set_p_id(tn.node.n_id)
        order_tree(tree_list,c,id_map)
        
def write_swc():
    file_contents = ""
    mapping = {}
    with open(sys.argv[1],'rb') as csv_file:
        reader = csv.reader(csv_file,delimiter = ',',
                            quotechar = '|')
        x = 0
        n_list = []
        _type = 0
        header = ""
        s_id=0
        h_tnode = None
        for row in reader:
            if x<1:
                header = "#id type x_pos y_pos z_pos radius parent_id\n"
                x+=1
            else:
                #create our list of nodes
                r = row[2::1]
                n = nnode(r[0],_type,r[2],r[3],r[4],r[5],r[1])
                #identify soma
                if n.r>=2000:
                    n._type = 1
                    n.p_id = -1
                    s_id = n.n_id
                    #start the tree from the soma node
                    h_tnode = tnode(n)
                elif n.r<=0:
                    n.r = 5.0
                n.x = n.x/um_factor
                n.y = n.y/um_factor
                n.z = n.z/um_factor
                n.r = n.r/um_factor
                n_list.append(n)
        
        #build the tree using the soma as the head node
        build_tree(h_tnode,n_list)

        tree = []
        #orders the tree in an array list with proper ids
        order_tree(tree,h_tnode,mapping)
        
        file_contents = header
        for n in tree:
            file_contents = file_contents + n.get()+"\n" 
        #for n in n_list:
         #   file_contents = file_contents + n.get()+"\n"           
    swc_file = open(sys.argv[2],'w')
    swc_file.write(file_contents)

    file_contents =  "new_ID, original_ID\n"
    for key, item in mapping.iteritems():
        file_contents = file_contents + key + ',' + item+"\n"
    mapping_name = sys.argv[2]
    mapping_name = "id_map_"+ mapping_name[:-4]+".csv"
    mapping_file = open(mapping_name,'w')
    mapping_file.write(file_contents)

if __name__ == "__main__":
    write_swc()
    
