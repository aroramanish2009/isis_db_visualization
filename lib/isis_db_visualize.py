#!~/mypy36-venv/bin/python

"""ISIS DB VISUALIZATION
This script allows the user to convert the output 
of Junos "Show isis database detail | display json"
into dot format file which can converted in pdf, png
etc format for visualization using Graphviz. 

This script requires Python3 and common modules like
json, sys, re and argparse.

"""

#Import modules required 
try:
  import json, sys, re, argparse
except ImportError:
  raise ImportError("Unable to import module")

#Position argument json_file is required, option argument is customize the color of nodes in dot file. 
parser = argparse.ArgumentParser()
parser.add_argument("json_file", help="file containing output of Show isis database detail | display json")
parser.add_argument("-c", "--custom", help='RegEx and Color combination in json format EX: python3.6 isis_db_visualize.py bb_db.json -c {"BR0": "green", "PE0": "yellow"}')

args = parser.parse_args()

file_json = args.json_file
if args.custom:
  customization = json.loads(args.custom)

#Function to convert json data into list of dictionaries.
def json_to_list_of_dict(file_json):
  try:
    with open(file_json, "r") as rf:
      decoded_data = json.load(rf)
  except IOError:
    print ("unable to open file, please check file path")
    sys.exit(1)
  lsp_dict = {}
  for index in range(len(decoded_data["isis-database-information"][0]["isis-database"][1]["isis-database-entry"])):
    for key in decoded_data["isis-database-information"][0]["isis-database"][1]["isis-database-entry"][index]:
      if key == "lsp-id":
        data_list = decoded_data["isis-database-information"][0]["isis-database"][1]["isis-database-entry"][index][key]
        for item in data_list:
          for k,v in item.items():
            v = v.replace("-", "_")
            normalize_v = re.sub(r'\..*', '', v)
            lsp_dict.setdefault(normalize_v, [])
      if key == "isis-neighbor":
        data_list = decoded_data["isis-database-information"][0]["isis-database"][1]["isis-database-entry"][index][key]
        for index in range(len(data_list)):
          data1 = (data_list[index])
          for k,v in data1.items():
            if k == "is-neighbor-id":
              for k1,v1 in v[0].items():
                v1 = v1.replace("-", "_")
                normalize_v1 = re.sub(r'\..*', '', v1)
                lsp_dict[normalize_v].append(normalize_v1)
  return (lsp_dict)

#Function to convert list of dictionaries in dot format. 
def list_of_dict_to_dot_file(lsp_dict,customization=None):
  with open("isis_db.dot", "a") as af:
    af.write('digraph finite_state_machine {\n')
    af.write('    rankdir=TB;\n')
    af.write('    edge [dir="both"]\n')
    af.write('    concentrate=true\n')
    af.write('    node [shape = circle];\n')
    if customization is not None:
      uniq_list = []
      for k,v in customization.items():
        regex_color = '    node [shape = doublecircle, color = ' + v +', style = filled]; '
        for k1,v1 in lsp_dict.items():
          for item in v1:
            if re.search(k, item) and item not in uniq_list:
              uniq_list.append(item)
              regex_color = regex_color + item + ' '
        af.write(regex_color + ';\n')
    for k,v in lsp_dict.items():
      for item in v:
        af.write('    ' + k + ' -> ' + item + ' [ label = "' + k + '-' + item + '" ];\n')
    af.write('}')
  print ("isis_db.dot is ready")
  return ()
            
def main():
  lsp_dict = json_to_list_of_dict(file_json)
  if 'customization' in globals():
    list_of_dict_to_dot_file(lsp_dict,customization)
  else:
    list_of_dict_to_dot_file(lsp_dict)

if __name__ == "__main__":
  main()
