#!/bin/bash

# Set up new directory tree for a request using PAQS for queries written in python
# Usage: /path/to/new_paqs_request.sh dir_name


## Check if the target directory has content
target=${1:-new_paqs_request}
if [[ ! -z $(ls -d "$target"/* 2>/dev/null)  || \
      ! -z $(ls -d "$target"/.[a-zA-Z0-9]* 2>/dev/null | grep -v /.git\$ ) ]]
then
    echo >&2 "Target directory $target already has content."
    exit 1
fi
if [[ ! -d "$target" ]]; then mkdir -p "$target"; fi
target_path=$(cd "$target"; pwd)

src=$(dirname $0)
src=${src:-$PWD}
if [[ ! -d "$src" || ! -e "$src/new_paqs_request.sh" ]]
then
    echo >&2 "Unable to find aql_standardized_package_python"
    exit 1
fi


cd "$src/.."
# Copy files to new request directory 
cp -r config_template shell Dockerfile requirements.txt request_info.qmd pcornet-style-sheet.css "$target_path"
cp -r code specs "$target_path"/"$target"

vers=$(git log -1 --date=short --format='%h %ad')

cd "$target_path"/"$target"
mkdir results
echo "\!.placeholder" >> results/.gitignore

# Check if Git is installed
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed." >&2
    exit 1
fi

# Initialize Git repository
git init
git add --all
git commit -m "Initial PAQS Platform Setup"