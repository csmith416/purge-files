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
## SCRIPT ARGUMENTS ##
##############################

def parse_args():
    parser = argparse.ArgumentParser(description="Purge files by name and age")

    parser.add_argument(
        "--dir",
        required=True,
    help="Target directory to scan"
    )

    parser.add_argument(
        "--files",
        nargs="+",
        required=False,
        help="List of file name filters (wildcards supported, e.g. *.csv or *test*)"
    )

    parser.add_argument(
        "--include-folders",
        nargs="+",
        required=False,
        help="List of folder name filters (wildcards supported, e.g. del* or *archive*)"
    )

    parser.add_argument(
        "--exclude-folders",
        nargs="+",
        required=False,
        help="Exclude folder patterns"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=0,
        help="Delete files older than N days"
    )

    return parser.parse_args()

##############################
## FUNCTIONS ##
##############################

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

    if not target_list:
        return source_list
    
    return [
        value for value in source_list
        if any(fnmatch.fnmatch(value.name, target) for target in target_list)
    ]

##############################
## MAIN PROGRAM ##
##############################

def main():
    args = parse_args()
    start_time = perf_counter()
    current_time = datetime.now()

    run_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    timestamp = current_time.strftime("%Y_%m_%d_%H_%M_%S")

    source_dir = Path(args.dir).resolve()
    log_dir = source_dir / "purge-files-logs"
    log_file = log_dir / f"purge-files_{timestamp}.log"
    log_dir.mkdir(parents=True, exist_ok=True)

    with open(log_file, "w") as log:
        log.write(
            f"Run time: {run_time}\n"
            f"Source directory: {source_dir}\n"
            f"Deletion range: {args.days} days\n"
            f"Folder filters: {args.include_folders}\n"
            f"File filters: {args.files}\n"
        )

        try:
            if not source_dir.exists():
                log.write(f"Error: Directory does not exist: {source_dir}")
                return

            # Check if any values or patterns are both included as args or their patterns overlap
            if args.include_folders and args.exclude_folders and any(
                fnmatch.fnmatch(inc, exc) or fnmatch.fnmatch(exc, inc)
                for inc in args.include_folders
                for exc in args.exclude_folders
            ):
                log.write(
                    f"Error: Include and exclude patterns overlap.\n"
                    f"Include: {args.include_folders}\n"
                    f"Exclude: {args.exclude_folders}\n"
                )
                return
            
            source_dirs = [
                path for path
                in source_dir.iterdir()
                if path.is_dir()
            ]

            cutoff = current_time - timedelta(days=args.days)

            total_skipped = 0
            total_deleted = 0

            print(source_dirs)

            target_dirs = sorted(filter_list(source_dirs, args.include_folders))

            if args.exclude_folders:
                target_dirs = [
                    path for path
                    in target_dirs if not any(fnmatch.fnmatch(path.name, pattern)
                    for pattern in args.exclude_folders) 
                ]

            if not target_dirs:
                log.write("\nNo directories match the filter criteria provided")
                return
            
            for path in target_dirs:
                dir_start = perf_counter()

                source_files = [
                    file for file
                    in path.iterdir()
                    if file.is_file()
                ]

                target_files = sorted(filter_list(source_files, args.files))

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
                            log.write(f"\tFile skipped, newer than {args.days} days: {file}\n")

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