mport csv

#opening files and saving to vars
f = open('Book1.csv')
f2 = open('Matt-VPN-September.csv')
csv_f = csv.reader(f)
csv_f2 = csv.reader(f2)


#creates string of date to parse through xml dates using format mm/dd/yy
def incrementDate():
    startMonth = 6
    lastMonth = 10
    startDay = 0
    lastDay = 31
    year = '2020'
    datesToCheck = []

    for i in range(lastMonth - startMonth + 1):
        if startDay != lastDay:
            for ii in range(31):
                if startDay < 9:
                    startDay = startDay + 1
                    currentDate = str(startMonth)+ '/0' + str(startDay) + '/' + year[0:2]
                    datesToCheck.append(currentDate)
                else:
                    startDay = startDay + 1
                    currentDate = str(startMonth)+ '/' + str(startDay) + '/' + year[0:2]
                    datesToCheck.append(currentDate)
            startMonth += 1
            startDay = 0
    #formatedDatesToCheck = monthFix(datesToCheck)
    #getClientData(formatedDatesToCheck)
    getClientData(datesToCheck)


#Gets all the Ip addresses and dates from client sheet and saves in list to remove duplicate IP's
def getClientData(currentDates):
    client_req_list = []
    for row in csv_f:
        if row[0] in currentDates:
            client_req_list.append(row[0] + '-' + row[2])
    cleanClientData(client_req_list)
    #print(client_req_list[2])


#Cleans all the duplicate entries in each da
def cleanClientData(clientData):
    cleanClientList = []
    for i in range(len(clientData)):
        if clientData[i] not in cleanClientList:
            cleanClientList.append(clientData[i])
            #print(clientData[i] + ' - was added tp cleaned list')
    #print(len(cleanClientList)) #- should equal 158 entries to search for
    getLogData(cleanClientList)


######## Everything above is to get the first list clean and set to check against second list #######
def getLogData(cleanClientList):
    logDataList = []
    for row in csv_f2:
        #print(row[1] + ' - ' + row[2] + ' - ' + row[3])
        date = row[1].split(' ')[0]
        fixedDate = fixDate(date)
        logDataList.append(str(fixedDate) + '-' + str(row[2]) + '-' + str(row[3]))
    cleanClientList2 = monthFix(cleanClientList)
    #print(logDataList[5])
    #print(cleanClientList2[119])
    compareLists(cleanClientList2, logDataList)



#Quick Bug fix for months that are single digits, reforms them with 0 in front to match in log file
def monthFix(cleanClientList):
    splitList = []
    for i in range(len(cleanClientList)):
        tmp = cleanClientList[i].split('/')
        if int(tmp[0]) < 10:
            splitList.append('0' + tmp[0] + '/' +tmp[1] + '/' + tmp[2])
            #print(splitList[i])
        else:
            splitList.append(tmp[0] + '/' +tmp[1] + '/' + tmp[2])
            #print(splitList[i])
    return(splitList)


#Just a small helper function to fix date for parsing
def fixDate(date):
    splitStr = date.split('/')
    year = splitStr[0][0:2]
    if len(splitStr) == 3:
        return(splitStr[1] + '/' + splitStr[2] + '/' + year)


#Compare cleaned client list to logdata from the logger logs.
def compareLists(clientList, logsList):
    ipsToCheck = []
    logsToCheck = []
    wrToFileList = []
    for i in range(len(clientList)):
        clDate = clientList[i].split('-')
        ipsToCheck.append(clDate)
    for i in range(len(logsList)):
       llDate = logsList[i].split('-')
       logsToCheck.append(llDate)

    for i in range(len(ipsToCheck)):
        for ii in range(len(logsToCheck)):
            if ipsToCheck[i][0] == logsToCheck[ii][0] and ipsToCheck[i][1] == logsToCheck[ii][1]:
                wrToFileList.append(logsToCheck[ii][0] + '-' + logsToCheck [ii][1] + '-' + logsToCheck[ii][2])
    wrToFile(wrToFileList)


def wrToFile(wrToFileList):
    cleanList = []
    with open('septemberVPNData.csv','w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Ip Address', 'Username'])
        for i in range(len(wrToFileList)):
            cleanList.append(wrToFileList[i].split('-'))
            writer.writerow([cleanList[i][0], cleanList[i][1], cleanList[i][2]])


incrementDate()

 
