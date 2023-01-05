import requests
from datetime import datetime
from dateutil import parser

class Tools:

    def checkDates(timeStamps):
        filteredDates = []
        betweenDates = sinceRecent = 0
        for i in timeStamps[::-1]:
            filteredDates.append(str(i).split('T')[0])
        recent =  str(timeStamps[0]).split('T')[0]
        last = str(timeStamps[-1]).split('T')[0]
        current = str(datetime.today().strftime('%Y-%m-%d'))
        sinceRecent = (parser.parse(current) - parser.parse(recent)).days
        betweenDates = (parser.parse(recent) - parser.parse(last)).days

        return filteredDates, sinceRecent, betweenDates


    def filter(date, splitMessage):
        months = {'01': 'January','02': 'February','03': 'March','04': 'April','05': 'May','06': 'June','07': 'July','08': 'August','09': 'September','10': 'October','11': 'November','12': 'December'}
        Year, Month, Date = str(date).split('T')[0].split('-', 3)
        if 'op' in splitMessage[1] or ' v ' in splitMessage[1] or ' vs ' in splitMessage[1] or 'lb' in splitMessage[1] or 'vs' in splitMessage[1] or 'lowball' in splitMessage[1]: opAmount = f'\n\n**Proof Amount**\n{splitMessage[1]}'
        else: opAmount = ''
        datePhrase = f'{Date} {months[Month]} {Year}'
        return datePhrase, opAmount


    def toUse(itemAcronym, itemName):
        if itemAcronym == 'op' or itemAcronym == 'vs': return itemName
        if itemAcronym != None: return itemAcronym
        else: return itemName

    def findItem(args, acroToName, nameToAcro, noAcronym):
        itemName, itemAcronym, amount = None, None, 0
        for i in acroToName:
            if args.lower() == i.lower():
                amount += 1
                itemAcronym = i.lower()
                itemName = acroToName[i][0].lower()
        if amount == 0:
            for i in nameToAcro:
                if args.lower() == i.lower():
                    amount += 1
                    itemName = i.lower()
                    itemAcronym = nameToAcro[i][0].lower()
        if amount == 0:
            for i in nameToAcro:
                if args.lower() in i.lower():
                    amount += 1
                    itemName = i.lower()
                    itemAcronym = nameToAcro[i][0].lower()
        if amount == 0:
            for i in noAcronym:
                if args.lower() == i.lower():
                    amount += 1
                    itemName = i.lower()
        if amount == 0:
            for i in noAcronym:
                if args.lower() in i.lower():
                    amount += 1
                    itemName = i.lower()
        if itemName != None:
            for i in '`~!@#$%^&*()_-=+[]}{\/|;:,.<>?':
                itemName = itemName.replace(i, '')
            itemName = itemName.replace('  ', ' ')
        return itemName, itemAcronym, amount
        

    def roli():
        nameToAcro, acroToName, noAcronym, assetIds = {}, {}, {}, {}
        try:
            itemDetails = requests.get(
                'https://www.rolimons.com/itemapi/itemdetails'
            ).json()['items']
            for item in itemDetails:
                acronym = itemDetails[item][1]
                name = itemDetails[item][0]
                if acronym != '':
                    nameToAcro[name] = [acronym]
                    acroToName[acronym] = [name]
                else:
                    if len(name.split()) == 1:
                        acroToName[name] = [name]
                        nameToAcro[name] = [name]
                    else:
                        noAcronym[name] = None
                for i in '`~!@#$%^&*()_-=+[]}{\/|;:,.<>?':
                    name = name.replace(i, '')
                name = name.replace('  ', ' ')
                assetIds[name.lower()] = str(item)
        except:
            return None, None, None
        else:
            return assetIds, nameToAcro, acroToName, noAcronym