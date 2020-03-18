#!/bin/bash
yum -y install python-pip
yum -y install python3
pip install virtualenv
mkdir app
cd app
python3 -m venv .env
source .env/bin/activate
