# PS-E-078526-EAS_Config
Thousandeyes | Home Depot 

On the Ubuntu server create a setup.sh file and copy the below lines:

#!/bin/bash
sudo apt update
sudo apt install python3-pip firefox git -y
git clone https://github.com/amarana-te/PS-E-078526-EAS_Config.git
cd PS-E-078526-EAS_Config
pip3 install -r requirements.txt

Then add exec permission to the script 

chmod +x setup.sh
run the script 
./setup.sh

This script should clone the repo and install the python3 requirements.

After you modify the config.json and the agents.csv you can run:

#python3 homedepot_ubuntu.py

Within the repository you may find the setup.sh script, the Selenium (Firefox) driver, the config.json and the agents.csv with 2 syntax examples one for NEW agents and another for NOT new agents. 
