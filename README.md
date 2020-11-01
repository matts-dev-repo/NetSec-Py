# NetSec-Py
Prod Scripts for network security automation using Python

Script Name and Function
=========================
1. Pool.py
-----------
- Pool.py is a python script which connects to Cisco ASA's. The main purpose of this script is to gather all the group-policies on the gate with their associated address-pools and write them to file. The script then grabs all the current ip pools on the ASA to and writes them to file. The reason this script was created for production is because with the new work from home orders, a lot of VPN users were getting the http 503 error of address not assigned in their AnyConnect DART bundles. This script allowed us to quickly gather all the information for pools and group-policies on the ASA and adjust the pools accordingly to avoid pool exhaustion in the future.

- There is another script I created that gathers all the pool information from all the ASA's we manage that runs on a cron twice a day. The only difference between the scripts is instead of manually entering an IP address for the ASA's you want to check, it just loops through an external file of managed ASA Ip's and does the exact same thing.
