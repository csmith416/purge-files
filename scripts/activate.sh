#!/bin/bash
set -e

LINE_BREAK="=============================================================================="

normalize_input() {
    local value="$1"

    value="$(printf '%s' "$value" | tr -d '\r' | xargs)"
    value="${value#\'}"
    value="${value%\'}"
    value="${value#\"}"
    value="${value%\"}"

    echo "$value"
    return 0
}

script_arg() {
    local prompt="$1"
    local arg="$2"
    local var_name
    
    while true; do
        read -r -p "$prompt" var_name
        var_name="$(normalize_input "$var_name")"

        if [[ "$arg" == "-d" ]]; then
            var_name="${var_name/#\~/$HOME}"
        fi

        # Check if input was given
        if [ -z "${var_name}" ]; then
            echo "No input provided!"
            continue
        fi

        if [[ "$arg" == "-d" && ! -d "$var_name" ]]; then
            echo "No valid directory provided!"
            continue

        fi 

        if [[ "$arg" == "-d" ]]; then
            cmd+=("$arg" "$var_name")
        else
            cmd+=("$arg" $var_name)
        fi
        
        echo "Updated Command: ${cmd[@]}"
        return 0
    done
}

# Set current directory to path of script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Project root: $PROJECT_ROOT"
echo "Script dir: $SCRIPT_DIR"
echo "$LINE_BREAK"

cmd=(python3 "$PROJECT_ROOT/main.py")

script_arg "Enter directory: " "-d"
script_arg "Enter file patterns (space separated, e.g. *.csv *.txt): " "-files"
script_arg "Enter folder include patterns (space separated, e.g. *.csv *.txt): " "-folders-include"
script_arg "Enter folder exclude patterns (space separated, e.g. *.csv *.txt): " "-folders-exclude"
script_arg "Enter days: " "-days"
script_arg "Recursive? (y/n): "

: << 'COMMENT'
NOTES:
    return 0:
        stop executing this function and return success

    ${list[@]}
        expand each element as a separate argument

    This is how you define a function in bash syntax:
        function_name() {
            function_stuff
        }
    ${VariableName}:
        Same as $VariableName just safer for more complex operations
    $(...):
        Runs command in a subshell, and returns its output
        This is called "command substitution"
        Whatever is printed inside, becomes the value

    dir="$(printf '%s' "$dir" | tr -d '\r' | xargs)"
        printf:
            Alternative to echo
            More portable and standardized by POSIX

        '%s':
            Replace
        
        tr -d '\r':
            tr:
                translate command on unix
                (https://www.thegeekstuff.com/2012/12/linux-tr-command/)
            -d:
                delete specified characters
            '\r':
                Carriage return character/other hidden characters
            
        xargs:
            Trim spaces

        Trim quoting:
            General reference:

            /position(#/%)pattern/replacement

            ${variable#pattern}   # remove from start
            ${variable%pattern}   # remove from end

            dir="${dir#\"}"
            dir="${dir%\"}"
            dir="${dir#\'}"
            dir="${dir%\'}"

        Absolute path:
            dir="${dir/#\~/$HOME}"
        
        1. Open your terminal and navigate to your main repository (RepoA).
        2. Run the following command (replace with your repository's URL):
            git add .gitmodules RepoB
        3. Commit the new .gitmodules file and the Repo B folder to Repo A:
            git commit -m "Add RepoB as a submodule"
        
        Alternative??
        https://git-scm.com/book/en/v2/Git-Tools-Submodules
        git submodule add https://github.com
COMMENT

# echo "Directory: $files"
# echo "Directory: $folders_include"
# echo "Directory: $folders_exclude"
# echo "Directory: $days"
# echo "Directory: $recursive"

# 
# read -p 'Include folders (space separated): ' folders_include
# read -p 'Exclude folders (space separated): ' folders_exclude
# read -p 'Days old: ' days
# read -p 'Recursive? (y/n): ' recursive