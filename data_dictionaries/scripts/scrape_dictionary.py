#!/usr/bin/python
# Author: Fred Frey (@fryguy2600)
# Date: July 20, 2019
# Description: Scrape OSSEM Data Dictionary Markdown files and create Json data struct
#               for scripts to use
# Usage:
#   scrape_dictionary.py  -d ./OSSEM/data_dictionaries/
# Output:
#   data_dict.json

import os
import csv
import re
import sys
import json
import collections
from pathlib import Path
import argparse

# todo add asserts to make sure data dictionary is standardized/reliable

column_names = ["Product", "Standard Name", "Field Name", "Type", "Description", "Sample Value"]

def get_file_list(path):
    if os.path.isfile(path) and path.endswith('.md'):
        return([path])
    else: 
        return(list(Path(path).rglob("*.md")))

def get_data_dictionary(file):
    '''Given a path to a file, read file line by line and detect/carve out the Data Dictionary
        Return a list of lists (2D array) of Data Dictionary with line 0 being column headers and
        following lines being data elements '''

    data_dict = []
    capture = False

    # Read each line, carve out Data Dictionary after seeing Markdown header ## Data Dictionary
    with open(file, 'r', encoding='utf-8') as data:
        for line in data.readlines():
            if line.startswith('## Data Dictionary'):
                capture = True
                #print('found it')
            elif not line.replace('-','').replace('|','').strip():
                # Skip blank lines and lines only containing dashes
                pass
            elif capture and not line.startswith('|'):
                capture = False
                print('ending it')
            elif capture:
                # Strip whitespace and drop first/last junk column
                junk = [x.strip()  for x in line.split('|')[1:-1]]
                data_dict.append(junk)
            else:
                pass
            
    return(data_dict)   # [['column1_header','column2_header'], ['data_row1_col1', 'data_row1_col2'], ['data_row2_col1', 'data_row2_col2'] ]

def data_dictionary_to_json(data_dict):
    data_dict_json = {}
    headers = data_dict[0]

    for row in data_dict[1:]:
        temp = dict(zip(headers, row))
        data_dict_json[temp.pop('Field Name')] = temp
        #data_dict_json.append(dict(zip(headers, row)))

    return(data_dict_json)

def write_data_dict_to_csv(data_dict, outfile):

    # Creates quite a few CSVs for now lets put in their own dir, make if doesn't exist
    #outfile = str(outfile).replace('.md', '.csv')
    #outfile = outfile.replace('data_dictionaries', 'data_dictionaries_code')

    # if not os.path.exists(os.path.dirname(outfile)):
    #     try:
    #         os.makedirs(os.path.dirname(outfile))
    #     except OSError as exc: # Guard against race condition
    #         pass
    #         # if exc.errno != errno.EEXIST:
    #         #     raise

    with open(outfile, 'w', newline='', encoding='utf-8') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for line in data_dict:
            wr.writerow(line)

def create_arg_parser():
    """"Creates and returns the ArgumentParser object."""

    parser = argparse.ArgumentParser(description='Description of your app.')
    parser.add_argument('-d', '--data_dict_dir', type=Path,
                    help='Path to the OSSEM Data Dictionary root')
    parser.add_argument('-o', '--output_json', type=Path, default='data_dict.json',
                    help='Store scraped Data Dict Json here')
    parser.add_argument('-c', '--output_csv', type=Path, default='data_dict.csv',
                    help='Store scraped Data Dict CSV here')
    return parser

if __name__ == "__main__":
    data_dict = []
    master_csv = []
    master_json = collections.defaultdict(dict)

    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    
    if not (parsed_args.data_dict_dir and os.path.exists(parsed_args.data_dict_dir)):
        print("ERROR: Provide -d path_to_data_dictionary\n")
        arg_parser.print_help()
        sys.exit()

    files = get_file_list(parsed_args.data_dict_dir)

    # Scrape Markdown files. Build master Json and optionally dump individual Data Dict as CSVs 
    for filename in files:
        #print(filename)

        # Scrape all Markdown return 2D Array of data dictionary
        data_dict = get_data_dictionary(filename)

        if len(data_dict):
            product = 'unknown' 
            file_base = os.path.basename(filename).replace('.md', '')
            
            # Pull product from directory path. ie ../windows/windowsdefenderatp/AlertEvents.md
            m = re.search('[\\/](\S+)[\\/]\S+\.md', str(filename))

            if m:
                product = m.group(1)
           
            #master_json[product][file_base] = []
            master_json[product][file_base] = data_dictionary_to_json(data_dict)
            # todo: add product to CSV
            master_csv.append(data_dict[1:])

            # Write individual MD scraped Data Dictionaries as CSVs optionally 
            #write_data_dict_to_csv(data_dict, parsed_args.output_csv)

    # Write master CSV
    # todo: CSV not working quite yet




    # with open(parsed_args.output_csv, 'w', newline='\n', encoding='utf-8') as myfile:
    #     wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    #     for line in master_csv:
    #         wr.writerow(line)

    # Write master Json
    with open(parsed_args.output_json, 'w') as outfile:
        outfile.write(json.dumps(master_json, indent=4))

    
    
