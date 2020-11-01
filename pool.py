from netmiko import ConnectHandler
import os
import getpass
import os.path

#Get all group policies on ASA and append to list and pass to cleanStr
def main():
    output = dvcConnect.send_command("show run group-policy | i attr")
    grpPolicies = output.split("\n")
    cleanedStr = cleanStr(grpPolicies)
    policies = getGrpPools(cleanedStr)
    pools = createPoolsArray()
    wrToFIle(policies, pools)

#Cleans out 'group-policies' and 'attributes' parts of string. Removes default group policies as well by calling rmvDflt()
def cleanStr(arr):
    cleanedArr = []
    for i in range(len(arr) - 1):
        clean1 = arr[i].replace("group-policy ","")
        clean2 = clean1.replace(" attributes","")
        clean3 = rmvDflt(clean2)
        if clean3 != False:
            cleanedArr.append(clean3)
    return cleanedArr

#Takes a cleaned group policy string and removes it from array if it matches default list
def rmvDflt(grpPolicy):
    defaults = ['GitHub-IKEv2', 'GitHub-Policy', 'DfltGrpPolicy']
    if grpPolicy in defaults:
        return False
    else:
        return grpPolicy

#Gets address pools related to group policy and writes to file
def getGrpPools(grpPolArr):
    policies = []
    for i in range(len(grpPolArr)):
        pool = dvcConnect.send_command("show run group-policy " + grpPolArr[i] +  " | i address")
        policies.append(pool.replace(" address-pools value ", " address-pools = "))
    return grpPolArr, policies

#Creates Pool array by extracting only the pool name from the show command
def createPoolsArray():
     output = dvcConnect.send_command("show run ip local pool")
     poolList = output.split("\n")
     cleanPool = []
     poolName = []
     for i in range(len(poolList) - 1):
        cleanPool.append(poolList[i].replace("ip local pool ", ""))
        poolName.append(cleanPool[i].split(" ", 1)[0])
     return getPoolRange(poolName)

#Gets the pool ranges for every pool passed in via the arr parameter.
def getPoolRange(arr):
    stats = []
    for poolName in arr:
        output = dvcConnect.send_command("show ip local pool " + poolName + " | i Begin | 255")
        stats.append(output)
    return arr, stats

#Writes all output to file and format
def wrToFIle(policies, pools):
    f = open("Gate_Pool_Summary.txt","a")
    f.write("===========================\n")
    f.write("Group Policies - " + currentFW + "\n")
    f.write("===========================\n")
    for i in range(len(policies[0])):
        f.write(policies[0][i] + "\n")
        f.write(policies[1][i] + "\n")

    f.write("===========================\n")
    f.write("Pool Summary - " + currentFW + "\n")
    f.write("===========================\n")
    for i in range(len(pools[0])):
        f.write(pools[0][i] + "\n")
        f.write(pools[1][i] + "\n\n")
    f.close()


### Functions called in order to run program. ###
#Gather user input
usrName = input('Enter Username: ')
passWord = getpass.getpass('Password: ')
ipAddr = input("Enter IP address, if multiple, enter space-seperated: ")

ipArr = ipAddr.split(" ") #Take inputted IP's and put into array
currentFW = 0 #Track current ASA in loop - Only used in wrToFile() function.

#Cleanout previous Gate_Pool_Summary.txt for new appending
if os.path.isfile('./Gate_Pool_Summary.txt'):
    os.remove('Gate_Pool_Summary.txt')

#Create object using user input to connect to gate. Loops through Ip's if more than one  entered.
for ip in ipArr:
    currentFW = ip
    cisco_asa = {
        'device_type': 'cisco_asa',
        'host': ip,
        'username': usrName,
        'password': passWord,
        'secret': passWord
    }
    dvcConnect = ConnectHandler(**cisco_asa)
    dvcConnect.enable()
    main()

print("Gate_Pool_Summary.txt was created in current directory")
dvcConnect.disconnect() #Netmiko Method to disconnect from session
