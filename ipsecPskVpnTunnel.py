from netmiko import ConnectHandler

class Asa:
    def __init__(self, mgmt, pub, pubNet, pri, priNet):
        self.mgmt = mgmt
        self.pub = pub
        self.pubNet = pubNet
        self.pri = pri
        self.priNet = priNet

asa_dict = {}

#Gather user input and create ASA objects for configuration.
def userInput():
    usrChoice = input("Do you want to set your own public and private IP's? Enter (Y/N): ")
    if usrChoice.upper() == "Y":
        print("##### Follow the prompts to set your IP's #####\n")
        for i in range(2):
            mgmtIP = input("Enter Management interface IP of ASA " + str(i+1) + ": ")
            pubIP = input("Enter Public Interface IP for ASA " + str(i+1) + ": ")
            pubNet = input("Enter Public Interface Network Address and Subnet Mask, e.g(192.168.1.0 255.255.255.0)")
            priIP = input("Enter Private Interface IP for ASA " + str(i+1) + ": ")
            priNet = input("Enter Private Interface Network Address and Subnet Mask, e.g(192.168.1.0 255.255.255.0)")
            #Creates ASA object and sets to dictionary
            asa_dict[i] = Asa(mgmtIP, pubIP, pubNet, priIP, priNet)
    else:
        print("##### You will receive two prompts for the management IP's used on both gates below, default IP's will be used for public and private interfaces ##### \n")
        for i in range(2):
            mgmtIP = input("Enter Management IP of ASA " + str(i+1) + ": ")
            print("### Data Entered Successfully for " + mgmtIP)
            asa_dict[i]= Asa(mgmtIP, '100.100.100.'+str(i+1),"100.100.100.0 255.255.255.252", '192.168.'+str(i+1)+'.1','192.168.'+str(i+1)+'.0 255.255.255.0')


#Loop through acl_dict and create configuration using information saved in objects
def main():
    userInput() #Call function to prompt user for data thats stored in acl_dict dictionary
    print("\n Putting together your configuration, please wait...")
    for i in range(len(asa_dict)):
        cisco_asa = {
            'device_type': 'cisco_asa',
            'host': asa_dict[i].mgmt,
            'username': 'cisco',
            'password': 'cisco',
            'secret': 'cisco'
            }
        dvcConnect = ConnectHandler(**cisco_asa)
        dvcConnect.enable()
        #Call function to start config
        setInterfaces(dvcConnect, asa_dict[i])
        dvcConnect.disconnect()

#Set up public and private interfaces on the ASA's
def setInterfaces(dvcConnect, current_asa):
    priSub = current_asa.priNet.split() #This splits the network address and subnet mask returning an array where we only care about sub mask.
    pubSub = current_asa.pubNet.split()
    #Both the IP address and subnet mask below are pulled from the current object being looped in the asa_dict.
    #priSub[1] takes the subnet mask portion of the array.
    dvcConnect.send_config_set([
        'int g0/0',
        'ip address ' + current_asa.pri + ' ' + priSub[1],
        'nameif inside',
        'no shut',

        'int g0/1',
        'ip address ' + current_asa.pub + ' ' + pubSub[1],
        'nameif outside',
        'no shut'
        ])
    phase1Tunnel(dvcConnect, current_asa)


#Creates IPSEC Phase 1/MGMT Tunnel settings on both ASA's
def phase1Tunnel(dvcConnect, current_asa):
    dvcConnect.send_config_set([
        'crypto ikev2 enable outside',
        'crypto ikev2 policy 10',
        'encryption aes-256', 'integrity sha512', 'prf sha512', 'group 19', 'lifetime 86400'
        ])
    createACL(dvcConnect, current_asa)

#Create ACL for interesting traffic. Current_asa is the current ASA being looped, asa_dict.mgmt is the management IP attribute
#of the ASA object.if current asa object in loop rotation has the same value set for its mgmt property as the asa object located in
#location 0 of the asa_dict dictionary, then use the network address(priNet property of the object) as the source network and
# network address of the other ASA object as the destination network, and vice versa.
def createACL(dvcConnect, current_asa):
    if current_asa.mgmt == asa_dict[0].mgmt:
        dvcConnect.send_config_set([
            'access-list L2L extended permit ip ' + asa_dict[0].priNet +  " " + asa_dict[1].priNet
        ])
    else:
        dvcConnect.send_config_set([
            'access-list L2L extended permit ip ' + asa_dict[1].priNet +  " " + asa_dict[0].priNet
        ])
    phase2Tunnel(dvcConnect, current_asa)


#Create IPSEC Phase 2 tunnel settings
def phase2Tunnel(dvcConnect, current_asa):
    dvcConnect.send_config_set([
        'crypto ipsec ikev2 ipsec-proposal VPN-TRANSFORM',
        'protocol esp encryption aes-256',
        'protocol esp integrity sha-256'
        ])
    tunnelGroup(dvcConnect, current_asa)

#Create transform set for phase two tunnel. Control flow says - if current asa object in loop rotation has the same
#value set for its mgmt property as the asa object located in location 0 of the asa_dict dictionary, then use the
#public IP address of the other ASA for the tunnel group name and vice versa.
def tunnelGroup(dvcConnect, current_asa):
    if current_asa.mgmt == asa_dict[0].mgmt:
        dvcConnect.send_config_set([
            'tunnel-group ' + asa_dict[1].pub + ' type ipsec-l2l',
            'tunnel-group ' + asa_dict[1].pub + ' ipsec-attributes',
            'ikev2 remote-authentication pre-shared-key cisco123',
            'ikev2 local-authentication pre-shared-key cisco123'
        ])
    else:
        dvcConnect.send_config_set([
            'tunnel-group ' + asa_dict[0].pub + ' type ipsec-l2l',
            'tunnel-group ' + asa_dict[0].pub + ' ipsec-attributes',
            'ikev2 remote-authentication pre-shared-key cisco123',
            'ikev2 local-authentication pre-shared-key cisco123'
        ])
    cryptoMap(dvcConnect, current_asa)


#Create and apply crypto map to outside interface of ASA's.
def cryptoMap(dvcConnect, current_asa):
    if current_asa.mgmt == asa_dict[0].mgmt:
        dvcConnect.send_config_set([
            'crypto map CRYPTO-MAP 1 match address L2L',
            'crypto map CRYPTO-MAP 1 set peer ' + asa_dict[1].pub,
            'crypto map CRYPTO-MAP 1 set ikev2 ipsec-proposal VPN-TRANSFORM',
            'crypto map CRYPTO-MAP interface outside'
        ])
    else:
        dvcConnect.send_config_set([
            'crypto map CRYPTO-MAP 1 match address L2L',
            'crypto map CRYPTO-MAP 1 set peer ' + asa_dict[0].pub,
            'crypto map CRYPTO-MAP 1 set ikev2 ipsec-proposal VPN-TRANSFORM',
            'crypto map CRYPTO-MAP interface outside'
        ])

    addRoute(dvcConnect, current_asa)

#Add route for traffic outgoing outside interface
def addRoute(dvcConnect, current_asa):
    priNet = current_asa.pubNet.split()
    if current_asa.mgmt == asa_dict[0].mgmt:
        priNet = asa_dict[1].priNet.split()
        dvcConnect.send_config_set([
            'route outside 0.0.0.0 0.0.0.0 ' + priNet[0] + ' 1',
            'wr mem'
        ])
    else:
        priNet = asa_dict[0].priNet.split()
        dvcConnect.send_config_set([
            'route outside 0.0.0.0 0.0.0.0 ' + priNet[0] + ' 1',
            'wr mem'
        ])

main()

#########################################
# Version Notes and Edits #
#########################################
# V1 - 11/12/2020 - Added a print statement for UX purposes in main function, just under the userInput() call.
