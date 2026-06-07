#!/bin/bash

# Exit if any command fails
set -e

# Change to script directory (important for relative paths)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Run the Python script with passed arguments
python3 main.py "$@"