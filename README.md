# NetSec-Py
Prod Scripts for network security automation using Python

Script Names and Functions
============================
-----------
1. ipsecPskVpnTunnel.py
-----------
- ipsecPskVpnTunnel.py is a Python script that configures a fully functioning Pre-Shared-Key IPSEC VPN Tunnel between two Cisco ASA firewalls. 

- The script connects to the ASA or ASA's via SSH through a management interface and fully configures - Inside and outside interface, Phase 1 tunnel settings, ACL for interesting traffic, Phase 2 tunnel settings, tunnel-group for authentication between the ASA's for pre-shared-key functionality, the crypto map and its application to the outside interface and a route.

- In order for script to work, both ASA's need to be reachable by a management interface and have SSH set up.

- There are two options for the script that you are prompted for when you run it. "Do you want to use default IP's and Subnets or your own IP's and Subnets".

- There is also another version of this script for situations where you only have access to one ASA and your client has access to the other. The only difference is one function which instead of configuring the ASA, creates a method of procedure file for the client to follow on their end to configure the IPSEC tunnel.

-------------------------
2. Pool.py
--------------------------
- Pool.py is a python script which connects to Cisco ASA's. The main purpose of this script is to gather all the group-policies on the gate with their associated address-pools and write them to file. The script then grabs all the current ip pools on the ASA to and writes them to file. The reason this script was created for production is because with the new work from home orders, a lot of VPN users were getting the http 503 error of address not assigned in their AnyConnect DART bundles. This script allowed us to quickly gather all the information for pools and group-policies on the ASA and adjust the pools accordingly to avoid pool exhaustion in the future.

- There is another script I created that gathers all the pool information from all the ASA's we manage that runs on a cron twice a day. The only difference between the scripts is instead of manually entering an IP address for the ASA's you want to check, it just loops through an external file of managed ASA Ip's and does the exact same thing.
