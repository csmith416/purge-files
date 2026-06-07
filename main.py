#!/usr/bin/env python3

"""
This top-line is needed so that it tells unix-based systems,
'run this file using Python'.

The #! is what is called a 'shebang'
    This must be the first line
    It tells the OS which interpreter to use

    /usr/bin/env is a program provided by the OS
    This is a helper program that runs other programs

    env finds programs using the system PATH

    python3 is the interpreter we want to run this script with

    This means we are specifying how this script should be run
    (i.e. using whatever python3 is available on the system)
"""

# This script uses standard library modules
# Everything is built-in, drop-in ready
# This means, no external dependencies
# Run 'pip freeze > requirements.txt' to verify

from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter
import argparse, fnmatch, traceback

##############################
## ARGUMENTS ##
##############################

# Define arguments passed from command line
def parse_args():
    parser = argparse.ArgumentParser(description="Purge files by name and age")

    # root dir for program scan
    parser.add_argument(
        "-d",
        required=True,
        help="Target directory to scan"
    )

    # Specify files / patterns to filter to
    parser.add_argument(
        "-files",
        nargs="+",
        required=False,
        help="List of file name filters (wildcards supported, e.g. *.csv or *test*)"
    )

    # Specify folders / patterns to include
    parser.add_argument(
        "-folders-include",
        nargs="+",
        required=False,
        help="List of folder name filters (wildcards supported, e.g. del* or *archive*)"
    )

    # Specify folders / patterns to exclude
    parser.add_argument(
        "-folders-exclude",
        nargs="+",
        required=False,
        help="Exclude folder patterns"
    )

    # Specify days for deletion (last file modified date)
    parser.add_argument(
        "-days",
        type=int,
        default=0,
        help="Delete files older than N days"
    )

    # TODO -r for recursive
    parser.add_argument(
        "-r",
        action="store_true",
        help="Scan subdirectories recursively"
    )

    return parser.parse_args()

##############################
## FUNCTIONS ##
##############################

# Function to filter a list of source paths against a given target list
# In this case, the arguments passed into the script
def filter_list(source_list: list[Path], target_list: list[str] | None) -> list[Path]:
    """
        Filter a list of Path objects based on Unix-style wildcard patterns.

        Args:
            source_list (list[Path]):
                A list of Path objects to filter

            target_list (list[str]):
                A list of patterns to match against each file or directory name
                Supports Unix-style wildcards:
                    ˙'*'  -> matches any number of characters
                    '?'  -> matches a single character
                    '[abc]' -> matches any character in the set

        Returns:
            list[Path]:
                A list of Path objects from 'source_list' that match at least one
                pattern in 'target_list'
        """

    # If no arguments given, return the source list
    if not target_list:
        return source_list
    
    # If arguments, return filtered source list against target
    return [
        value for value in source_list
        if any(fnmatch.fnmatch(value.name, target) for target in target_list)
    ]

##############################
## MAIN PROGRAM ##
##############################

def main():

    # Call passed arguments
    args = parse_args()
    target_dir = Path(args.d).resolve()
    files_patterns = args.files  or ["del_data"]
    folders_exclude_patterns = args.folders_exclude or []
    folders_include_patterns = args.folders_include or ["del_folder"]
    days= args.days or 0
    recursive = args.r or False
    
    # Get start time / current time / file age cutoff
    start_time = perf_counter()
    current_time = datetime.now()
    cutoff = current_time - timedelta(days=days)

    # Convert current time into log timestamps for file and filename
    run_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = current_time.strftime("%Y_%m_%d_%H_%M_%S")

    # Set up logging 
    log_dir = target_dir / "purge-files-logs"
    log_file = log_dir / f"purge-files_{timestamp}.log"

    # Ensure log directory exists if not already as well as any parent directories if not created
    log_dir.mkdir(parents=True, exist_ok=True)

    # Start logging
    with open(log_file, "w") as log:

       # TODO FIX this gross logic
        # If filters for both include/exclude, log both
        if folders_include_patterns and folders_exclude_patterns:
            message = (
                f"Pattern(s) included: {folders_include_patterns}\n"
                f"Pattern(s) excluded: {folders_exclude_patterns}\n"
            )

        # Else if just include log only that
        elif folders_include_patterns:
            message = f"pattern (s) included: {folders_include_patterns}\n"

        # Else if only exclude, log that
        elif folders_exclude_patterns:
            message = f"\t\tFolder(s) excluded (or pattern): {folders_exclude_patterns}\n"
        
        # Else log none
        else:
            message = None

        # Write run details to log
        log.write(
            f"Run Details:\n"
            f"\tRun time: {run_time}\n"
            f"\tTarget directory: {target_dir}\n"
            f"\tDeletion range: {days} days\n"
            f"\tFolder patterns applied:\n{message}"
            f"\tFile patterns applied: {files_patterns}\n"
        )

        try:
            if not target_dir.exists():
                log.write(f"Error: Directory does not exist: {target_dir}")
                return

            # Check if any values or patterns are both included as args or their patterns overlap
            if folders_include_patterns and folders_include_patterns and any(
                fnmatch.fnmatch(inc, exc) or fnmatch.fnmatch(exc, inc)
                for inc in folders_include_patterns
                for exc in folders_exclude_patterns
            ):
                
                # Catch any overlapping include / exclude folder arg patterns
                log.write(
                    f"Error: Include and exclude patterns overlap.\n"
                    f"Include: {folders_include_patterns}\n"
                    f"Exclude: {folders_exclude_patterns}\n"
                )
                return
            
            # Total skipped / delete count for logs
            total_skipped = 0
            total_deleted = 0
            
            # List the paths in the source items that are directories,
            # are not the log directory, and dont contain an exclude pattern
            source_dirs = [
                path for path
                in target_dir.iterdir()
                if path.is_dir()
                and path != log_dir
                and not any(fnmatch.fnmatch(path.name, pattern)
                for pattern in folders_exclude_patterns)
            ]

            # Filter source directories against target
            target_dirs = sorted(filter_list(source_dirs, folders_include_patterns))

            # TODO
            # If args are exclude folders filter target list
            if folders_exclude_patterns:
                target_dirs = [
                    path for path in target_dirs
                    if (
                        path != log_dir
                        and not any(fnmatch.fnmatch(path.name, pattern)
                        for pattern in folders_exclude_patterns)
                    ) 
                ]

            if not target_dirs:
                log.write("\nNo directories match the filter criteria provided")
                return
            
            print(target_dirs)

            for path in target_dirs:
                dir_start = perf_counter()

                source_files = [
                    file for file
                    in path.iterdir()
                    if file.is_file()
                ]

                target_files = sorted(filter_list(source_files, files_patterns))

                log.write(f"\nDirectory marked for deletion: {path}\n\n")
                                            
                if not target_files:
                    log.write(f"\tNo files to delete!\n")
                    continue

                # Set counters to 0
                count_skipped = 0
                count_removed = 0

                for file in target_files:
                    try:

                        # .st_mtime is POSIX last modification time
                        last_modified = datetime.fromtimestamp(file.stat().st_mtime)
                        
                        # Compare POSIX timestamps, if in cutoff range, delete files.
                        if last_modified <= cutoff:
                            total_deleted += 1
                            count_removed += 1
                            file.unlink()
                            log.write(f"\tFile removed: {file}\n")
                        else:
                            total_skipped+= 1
                            count_skipped += 1
                            log.write(f"\tFile skipped, newer than {days} days: {file}\n")

                    except Exception as e:
                        log.write(f"\tError removing {file}:\n")
                        log.write(f"Traceback:\n\t{traceback.format_exc()}")
                
                dir_time = perf_counter() - dir_start

                log.write(
                    f"\n\tSummary:\n"
                    f"\t\tFiles skipped: {count_skipped}\n"
                    f"\t\tFiles removed: {count_removed}\n"
                    f"\t\tTime for directory: {dir_time:.3f} seconds\n"
                )

            end_time = perf_counter()
            execution = end_time - start_time
            
            log.write(
                f"\nTotal Summary:\n"
                f"\tTotal files skipped: {total_skipped}\n"
                f"\tTotal files removed: {total_deleted}\n"
                f"\tTime for execution: {execution:.3f} seconds"
            )

        except Exception as e:
            log.write(f"\nUnhandled Exception occurred: {e}")
            log.write(f"Traceback:\n\n\t{traceback.format_exc()}")

##############################
## MAIN EXECUTION ##
##############################

if __name__ == "__main__":
    main()