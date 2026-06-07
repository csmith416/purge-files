from pathlib import Path
import shutil

##############################
## GLOBALS ##
##############################


SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent
FILES = ["del_data"]
FOLDERS = ["del_folder"]
FILES_OUT = 5

##############################
## FUNCTIONS ##
##############################

def filter_list(source_list: list[Path], target_list: list[str]) -> list[Path]:

    filtered = [
        value for value in source_list
        if any(target in value.name for target in target_list)
    ]
    
    return filtered

def copy_files(source_dir: Path, target_dir: Path, target_files: list[Path], copies: int = FILES_OUT) -> None:
    for filename in target_files:
        source_files = source_dir / filename

        if not source_files.is_file():
            raise Exception(
                "No files in the control_folder!\n"
                f"Place files in {source_dir}"
            )
        
        target_dir.mkdir(parents=True, exist_ok=True)

        for i in range(copies):
            target = target_dir / f"{source_files.stem}_{i + 1}{source_files.suffix}"

            if target.is_file():
                continue
            
            shutil.copy(source_files,target)

##############################
## MAIN PROGRAM ##
##############################

def main(copies: int = FILES_OUT) -> None:
    base_dir = PROJECT_DIR / "local_test"
    source_dir = base_dir / "control_folder"

    source_dirs = [
        path for path in base_dir.iterdir()
        if path.is_dir()
    ]

    if not FOLDERS:
        target_dirs = [
            path for path in source_dirs
            if path.name != source_dir.name
        ]

    else:
        target_dirs = filter_list(source_dirs, FOLDERS)

    source_files = list(source_dir.iterdir())
    target_files = filter_list(source_files, FILES)

    for folder in target_dirs:        
        target_dir = base_dir / folder
        if target_dir.absolute() == source_dir.absolute():
            raise Exception(
                "ERROR: Cannot copy into control_folder!"
            )

        # Ensure target dir exists
        target_dir.mkdir(parents=True, exist_ok=True)
        copy_files(source_dir, target_dir, target_files, copies)

##############################
## MAIN EXECUTION ##
##############################

if __name__ == "__main__":
    main()