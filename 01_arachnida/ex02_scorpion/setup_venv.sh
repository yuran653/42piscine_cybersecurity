#!/bin/bash

YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

NAME='scorpion_venv'

echo -e "${YELLOW}Creating Python virtual environment ${NAME}...${NC}"
python3 -m venv ${NAME}
echo -e "${GREEN}${NAME} has been created successfully${NC}"

echo -e "${YELLOW}Activating the virtual environment...${NC}"
source ${NAME}/bin/activate
echo -e "${GREEN}Virtual environment has been activated successfully${NC}"

echo -e "${YELLOW}Updating pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}'pip' has been updated successfully${NC}"

echo -e "${YELLOW}Installing required Python packages...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}All required packages have been installed${NC}"

echo -e "${GREEN}Virtual environment setup is completed${NC}"