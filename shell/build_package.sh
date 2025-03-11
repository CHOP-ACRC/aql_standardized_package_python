#!/bin/bash

# Check if script is executed from the top-level directory
if [[ ! -d 'shell' ]]; then
    echo "Please execute from the top-level directory"
    exit 1
fi

# Check if request_info.qmd needs editing
if grep -q '^Enter your Sub-title' request_info.qmd; then
    echo "Please edit request-specific description request_info.qmd"
    exit 1
fi

req_name=$(basename "$PWD")

echo "Enter your query folder name within this directory:"  
read -r query_name

# Check if the entered query folder exists
if [ ! -d "$query_name" ]; then
    echo "The folder '$query_name' does not exist in the top-level directory"
    exit 1
fi

# Create a directory for query package
mkdir -p qf-query-package
#cp shell/execute-query.sh qf-query-package 
#cp shell/parse_log.sh qf-query-package 
# Move into the query folder
cd "$query_name" || exit 1

# Function to populate folder names
populate_folder_names() {
    # Find all non-hidden directories except 'results'
    folders=$(find . -mindepth 1 -maxdepth 1 -type d ! -name ".*" ! -name "results")
    
    # Populate folder_names array
    while IFS= read -r folder; do
        folder_names+=("$(basename "$folder")")
    done <<< "$folders"
}

# Call function to populate folder names
populate_folder_names

# Loop through each folder in the array
for folder_name in "${folder_names[@]}"; do
    # Create corresponding folders in qf-query-package
    mkdir -p "../qf-query-package/" #$folder_name"
    #mkdir -p "../qf-query-package/$folder_name/renv"
    # Copy necessary files and folders
    cp -r "./$folder_name" "../qf-query-package/$folder_name" #"$folder_name"/specs "$folder_name"/site "$folder_name"/renv.lock "$folder_name"/.Rprofile
    #cp -r "$folder_name"/renv/activate.R "$folder_name"/renv/settings.json "../qf-query-package/$folder_name/renv"
    mkdir -p "../results" #$folder_name/
done

# Move back to the top-level directory
cd ..

mkdir temp_dir_docker
cp -r Dockerfile config_template qf-query-package results temp_dir_docker #"Docker desktop for windows or mac.docx"

mkdir temp_dir_native_python
cp -r requirements.txt config_template qf-query-package results temp_dir_native_python
mkdir -p temp_dir_native_python/shell
cp -r shell/setup_venv* temp_dir_native_python/shell/

# Render request_info.qmd to HTML
quarto render request_info.qmd --to html

# Create workplan directory
mkdir -p workplan

# # Move HTML file to workplan with modified name
mv request_info.html "workplan/${req_name}-workplan.html"

cd temp_dir_docker
# Create zip file with necessary contents
zip -r9X "${req_name}-docker.zip" *
mv "${req_name}"-docker.zip ..

cd ../temp_dir_native_python
# Create zip file with necessary contents
zip -r9X "${req_name}-native-python.zip" *
mv "${req_name}"-native-python.zip ..

cd ..
# Remove qf-query-package directory
rm -rf temp_dir_docker
rm -rf temp_dir_native_python
rm -rf qf-query-package