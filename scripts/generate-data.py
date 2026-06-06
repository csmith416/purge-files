import os

##############################
## GLOBALS
##############################

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
FILE = "del_data.csv"
FILES_OUT = 5

##############################
## Functions
##############################

control_base = os.path.normpath("local_test/control_folder")
control_dir = os.path.join(PROJECT_DIR, control_base)



##############################
## GLOBALS
##############################

# for path, dirs, files in os.walk(PROJECT_DIR):
#     print(path)
#     print(dirs)
#     print(files)