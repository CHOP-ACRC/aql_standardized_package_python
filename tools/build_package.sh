#!/bin/bash

# Check if script is executed from the top-level directory
if [[ ! -d 'tools' ]]; then
    echo "Please execute from the top-level directory"
    exit 1
fi

req_name=$(basename "$PWD")

# echo "Enter your query folder name within this directory:"  
# read -r query_name

# # Check if the entered query folder exists
# if [ ! -d "$query_name" ]; then
#     echo "The folder '$query_name' does not exist in the top-level directory"
#     exit 1
# fi

# Create a directory for query package
mkdir -p package

# Create a directory for query package - containerized
mkdir temp_dir_docker
mkdir temp_dir_docker/results
mkdir temp_dir_docker/query
mkdir temp_dir_docker/query/results
mkdir temp_dir_docker/tools
cp -r Dockerfile config_template temp_dir_docker
cp -r tools/banner tools/pcornet-style-sheet.css tools/parse_log.sh tools/PCORnet-logo-resize.png temp_dir_docker/tools
cp -r query/script_container query/code_sets temp_dir_docker/query

cd temp_dir_docker
# Create zip file with necessary contents
zip -r9X "${req_name}_docker.zip" *
mv "${req_name}_docker.zip" ../package
cd ..


mkdir temp_dir_native
mkdir temp_dir_native/query
mkdir temp_dir_native/query/results
mkdir temp_dir_native/tools
cp -r requirements.txt config_template temp_dir_native
cp -r tools/banner tools/pcornet-style-sheet.css tools/parse_log.sh tools/PCORnet-logo-resize.png tools/setup_venv* temp_dir_docker/tools
cp -r query/script_native query/code_sets temp_dir_native/query

cd temp_dir_native
# Create zip file with necessary contents
zip -r9X "${req_name}_native_python.zip" *
mv "${req_name}_native_python.zip" ../package
cd ..


# Make API calls to DockerHub to get latest tag
latest_tag=$(curl -s https://hub.docker.com/v2/namespaces/pcornetqf/repositories/qf-r-base/tags |\
 grep -o '"name":"[^"]*"' |\
 sed 's/"name":"\([^"]*\)"/\1/' |\
 grep -v latest |\
 sort |\
 tail -n 1)
# Get base image tag from Dockerfile
used_tag=$(grep '^FROM pcornetqf/qf-r-base' Dockerfile | awk -F ':' '{print $2}')
# Compare if latest
if [ "$latest_tag" != "$used_tag" ]; then
    echo -e "\033[0;31mWARNING: You are using $used_tag version of pcornetqf/qf-r-base, while the latest version on DockerHub is $latest_tag\033[0m"
else
    echo -e "\033[0;32mYou are using latest version of pcornetqf/qf-r-base: $used_tag\033[0m"
fi



# Render workplan.qmd to HTML
quarto render workplan.qmd --to html

# Create workplan directory
mkdir -p workplan

# Move HTML file to workplan with modified name
mv workplan.html "package/${req_name}_workplan.html"



# Make API calls to DockerHub to get latest tag
latest_tag=$(curl -s https://hub.docker.com/v2/namespaces/pcornetqf/repositories/qf-python-base/tags |\
 grep -o '"name":"[^"]*"' |\
 sed 's/"name":"\([^"]*\)"/\1/' |\
 grep -v latest |\
 sort |\
 tail -n 1)
# Get base image tag from Dockerfile
used_tag=$(grep '^FROM pcornetqf/qf-python-base' Dockerfile | awk -F ':' '{print $2}')
# Compare if latest
if [ "$latest_tag" != "$used_tag" ]; then
    echo -e "\033[0;31mWARNING: You are using $used_tag version of pcornetqf/qf-python-base, while the latest version on DockerHub is $latest_tag\033[0m"
else
    echo -e "\033[0;32mYou are using latest version of pcornetqf/qf-python-base: $used_tag\033[0m"
fi



# Remove temporary directories
rm -rf temp_dir_docker
rm -rf temp_dir_native