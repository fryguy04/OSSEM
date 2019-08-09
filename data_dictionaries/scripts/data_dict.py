#!/usr/bin/python
# Author: Fred Frey (@fryguy2600)
# Date: July 20, 2019
# Description: Class for using Scraped OSSEM Data Dictionary Json to GraphViz
# Note: Still very much work in progress
# Usage:
#   data_dict.py  
# Output:
#   test.gv  (graphviz)

import json
import csv
from graphviz import Digraph, Graph

gv_node_template = 'node [shape=box, style=filled, fillcolor={box_color}]; {box_list}'

class Data_Dict():
    dd = {}

    def __init__(self, data={}):
        self.dd = data
     
    @classmethod
    def fromdict(cls, master_dict={}):
        '''Initialize from dictionary/json'''
        return cls(master_dict)

    @classmethod
    def fromfile(cls, master_file='master.json'):
        with open(master_file, 'r') as infile:
            data = json.load(infile)
        return cls(data)

    def append(self, product, log, field, data):
        '''Safely add data to build up data dictionary, create keys as needed'''
        if not product in self.dd:
            self.dd[product] = {}

        if not log in self.dd[product]:
            self.dd[product][log] = {}

        self.dd[product][log][field] = data

    def filter_by_field_name(self, field_search):
        '''Given OSSEM Field Name, return all products/logs that map to this'''
        results = Data_Dict()  
            
        for product in self.dd:
            for log in self.dd[product]:
                if field_search in self.dd[product][log]:
                    results.append(product, log, field_search, self.dd[product][log][field_search])
        return(results)

    def filter_by_standard_name(self, standard_search):
        '''Given OSSEM Standard Name, return all products/logs that map to this'''
        results = Data_Dict()  

        for product in self.dd:
            for log in self.dd[product]:        
                for field in self.dd[product][log]:
                    try:
                        if self.dd[product][log][field]['Standard Name'] == standard_search:
                            results.append(product, log, field, self.dd[product][log][field])
                    except:
                        print("KEY ERROR: ", product, log, field)

        return(results)

    def filter_by_product(self, product_search):
        '''Given Product (Carbonblack, Sysmon, etc), return all products/logs that map to this'''
        results = Data_Dict()  

        for product in self.dd:
            for log in self.dd[product]:        
                for field in self.dd[product][log]:
                    if product == product_search:
                        results.append(product, log, field, self.dd[product][log][field])            

        return(results)

    def print(self, dd=None):
        '''Pretty print json'''
        if dd is None:
            dd = self.dd

        print(json.dumps(dd, indent=4))

    def return_list(self, dd=None):
        '''Flatten Json into one line/list per Data Dictionary'''
        results = []
        if dd is None:
            dd = self.dd

        for product in self.dd:
            for log in self.dd[product]: 
                for field in self.dd[product][log]:  
                    flattened = [self.dd[product][log][field][key] for key in sorted(self.dd[product][log][field].keys(), reverse=True)]
                    #print(flattened)
                    results.append([product, log, field] + flattened)
        return(results) 

    def return_list_names(self, dd=None):
        '''Return just critical fields for data dictionary. Same as return_list but simplified'''
        results = []
        if dd is None:
            dd = self.dd

        for product in self.dd:
            for log in self.dd[product]:        
                for field in self.dd[product][log]:
                    results.append([product, log, field, self.dd[product][log][field]['Standard Name']])
        return(results) 
 
    def out_csv(self, filename):
        with open(filename, "w", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(self.return_list())

    def out_graphviz(self, filename, show_only_field_changes=True, show_one_edge_only=True):
        
        dot = Digraph(comment='Parent')
        dot.attr(rankdir = 'LR')
    
        # If true, consolidate multiple edges (lines) between nodes to only One max  (helps clean graph)
        if show_one_edge_only:
            dot.attr(concentrate = 'true')


        dot_ossem = Digraph(name='cluster OSSEM',  comment='OSSEM Nodes', node_attr={'shape': 'rounded'})
        dot_ossem.attr(label='OSSEM')
        dot_ossem.attr(color='yellow')
        dot_ossem.attr(style='filled')
        dot_ossem.attr(shape='circle')
        dot_ossem.attr(concentrate = 'true')


        product_current = ''
        
        for line in self.return_list_names():
            (product, log, product_field, ossem_name) = line

            if product_current != product:
                # New Product, create new sub/cluster graph
                product_current = product
                dot_product = Digraph(name='cluster_'+product, comment=product)
                dot_product.attr(label=product)
                dot_product.attr(color='gray')
                dot_product.attr(style='filled')
                dot_product.attr(concentrate = 'true')
            # If true, show only fields that are changing name (helps clean graph)
            if show_only_field_changes and product_field == ossem_name:
                continue

            # Create OSSEM Node
            dot_ossem.node(ossem_name)
            dot_product.node(product_field)

            dot.subgraph(dot_product)
            dot.subgraph(dot_ossem)

            dot.edge(product_field, ossem_name, concentrate='true')

        dot.render(filename, view=False)
       

if __name__ == "__main__":
    results = []

    # Create from File (output of scrape_dictionary.py) or Dict
    dd = Data_Dict.fromfile('data_dict.json')

    # Filtering by field_name, standard ossem name or product
    #results = dd.filter_by_field_name("md5")
    results = dd.filter_by_standard_name("user_name")
    #results = dd.filter_by_product("sysmon")

    # Displaying by Json or List
    #results = dd.return_list()
    #results.print()  
        
    # Writing to file either Json, CSV, Graphviz
    results.out_csv('master.csv')
    results.out_graphviz('test.gv')
   
