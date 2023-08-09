#!/bin/bash

# Update package list
sudo apt update

# Install necessary packages
sudo apt install python3-pip firefox git -y

# Clone the Git repository
git clone https://github.com/amarana-te/PS-E-078526-EAS_Config.git

# Change directory to the cloned repository
cd PS-E-078526-EAS_Config

# Install Python dependencies from requirements.txt
pip3 install -r requirements.txt


#chmod +x setup.sh
#./setup.sh
#python3 homedepot_ubuntu.py