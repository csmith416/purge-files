import shutil, os

##############################
## GLOBALS ##
##############################

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
FILES = ["del_data.csv"]
FILES_OUT = 5

##############################
## Placeholder ##
##############################







global_dir = os.path.join(PROJECT_DIR, "local_test")
global_files_set = set(sorted(FILES))

control_dir = os.path.join(global_dir, "control_folder")
control_files = os.listdir(control_dir)
control_files_set = set(sorted(control_files))

output_dir = os.path.join(os.path.dirname(control_dir), "del_folder")

selected_files = [
    file for file
    in control_files_set
    if file in global_files_set
]

for file in selected_files:
    source = os.path.join(control_dir, file)
    file_split = file.split(".")
    file_name = file_split[0]
    file_extension = file_split[1]
    print(source)

    for i in range(FILES_OUT):
        new_file = f"{file_name}_{i + 1}.{file_extension}"
        target = os.path.join(output_dir, new_file)
        shutil.copy(source,target)