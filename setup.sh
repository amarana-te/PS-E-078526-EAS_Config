#!/bin/bash

docker build -t hd_eas_script .

docker run -it hd_eas_script /bin/bash
#chmod +x setup.sh
#./setup.sh
#