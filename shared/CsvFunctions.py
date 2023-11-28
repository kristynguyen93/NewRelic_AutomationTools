import csv
import os

def output_files():
    working_dir = os.getcwd()
    output_folder = working_dir + "/output/"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    return output_folder

def write_list_of_dicts_to_csv(list_of_dicts, file_name):
    column_names = list_of_dicts[0].keys()
    with open(file_name, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, column_names)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dicts)

