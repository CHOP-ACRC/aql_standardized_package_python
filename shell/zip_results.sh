#!/bin/bash

# Ask user for prefix
read -p "Enter the zipname that you'd like: " zipname

# Check if the 'results' folder exists
if [ -d "results" ]; then
    # Zip the 'results' folder with provided prefix and fixed suffix
    zip -r "${zipname}" results
    echo "Folder 'results' zipped successfully as ${zipname}"

else
    echo "Error: 'results' folder not found in the current directory."
fi


# Function to clean files in 'results' directory and subdirectories
clean_results_directory() {
    local directory="$1"
    find "$directory" -type f -delete
    echo "Files cleaned in '$directory' directory."
}

# Prompt user if they want to clean the directory
read -p "Do you want to clean the 'results' directory before zipping? (yes/no): " clean_choice

# Check if the 'results' folder exists
if [ -d "results" ]; then
    # Check user's choice for cleaning the directory
    if [ "$clean_choice" = "yes" ]; then
        # Clean files in 'results' directory and subdirectories
        clean_results_directory "results"
    else
      echo "Files left unchanged"
    fi
fi