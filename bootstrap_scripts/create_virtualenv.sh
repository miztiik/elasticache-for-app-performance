#!/bin/bash
yum -y install python-pip
yum -y install python3
pip3 install virtualenv
mkdir app
cd app
python3 -m venv .env
source .env/bin/activate
