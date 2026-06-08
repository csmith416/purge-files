#!/usr/bin/env bash
set -e

LINE_BREAK="=============================================================================="

# Set current directory to path of script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

# Echo project directory, execution directory, and script directory
echo "Project root: $PROJECT_ROOT"
echo "Script dir: $SCRIPT_DIR"
echo "$LINE_BREAK"

# Check if .venv exists
if [ -d "${VENV_DIR}" ]; then
    echo ".venv exists"
else
    echo "Creating .venv"
    python3 -m venv "$VENV_DIR"
fi

# Echo message on how to activate
echo
echo "To activate run:"
echo "    source \"$VENV_DIR/bin/activate\""

# After .venv has been created, or checked that already exists stores results of pip upgrade command as variable
PIP_OUTPUT=$("$VENV_DIR/bin/python" -m pip install --upgrade pip)

echo "$LINE_BREAK"

# Upgrade pip if needed
if echo "$PIP_OUTPUT" | grep -q "Requirement already satisfied: pip"; then
    echo "Pip already up to date"
else
    echo "Pip version upgraded"
fi

: << 'COMMENT'
Notes:
    #!/usr/bin/env bash:
        The #! is what is called a "shebang"
        This must be the first line
        It tells the OS which interpreter to use

        /usr/bin/env is a program provided by the OS
        This is a helper program that runs other programs

        env finds programs using the system PATH
        bash is the interpreter we want this to be ran with

        This means we are specifying how this script should be run
        (i.e. using bash found on the system)

    set -e:
        This tells the script to exit immediately if any command fails
        In bash, a non-zero exit code

        This means if any command errors, the script stops there
        This helps to catch any errors early

    $(...):
        Runs command in a subshell, and returns its output
        This is called "command substitution"
        Whatever is printed inside, becomes the value

    cd + pwd:
        cd changes directory to a specified path
        pwd prints the absolute path of that directory
    
    &&:
        Logical AND operator
        Runs the command on the right only if the command on the left succeeds
        This just ensures pwd is only ran if cd worked successfully

SCRIPT_DIR:
    ${BASH_SOURCE[0]}:
        Path to current script file including filename

    dirname:
        Gets the directory name from a path

    This means this variable is the absolute path of the directory to where
    this script is located

    This avoids relying on $PWD, which depends on where the user runs the script

PROJECT_ROOT:
    Works by applying command substitution to first run a change directory (cd)
    to the absolute path set in SCRIPT_DIR then elevates up a relative level (../)
    
    This means the project where this is being deployed must have this script
    located in a subfolder in the project directory.

VENV_DIR:
    Assumes a virtual environment name of ".venv"
    If you want a different environment name or location,
    modify this variable
COMMENT