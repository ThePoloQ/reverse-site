#!/bin/sh

# change-it
echo '1.2.3.4 my-website.com' >> /etc/hosts

python3 main.py
