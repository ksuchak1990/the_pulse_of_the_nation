# Imports
import requests
import csv
import codecs
import json
import os
import pandas as pd
import matplotlib.pyplot as plt

# Functions
# Get url source code, else catch errors
def requestURL(inputString):
    if not isinstance(inputString, str):
        raise TypeError('inputString must be a string') 
    r = requests.get(url=inputString)
    if r.status_code != 200:
        raise Exception('Page request unsuccessful: status code {0}'.format(r.status_code))
    return(r.text)

# Get a substring from an input, given a start string and an end string
def restrict(inputString, startStr=None, endStr=None):
    if not isinstance(inputString, str):
        raise TypeError('inputString must be a string')

    startIndex = inputString.index(startStr) + len(startStr) if startStr else 0
    endIndex = inputString.index(endStr) if endStr else len(inputString)
    return(inputString[startIndex:endIndex])

# Get urls of csvs on survey website
def getDataURLs():
    baseURL = 'https://thepulseofthenation.com'
    sourceCode = requestURL(inputString=baseURL)
    downloadSection = restrict(inputString=sourceCode, startStr='<ul class="downloads">', endStr='</ul>')
    downloadList = downloadSection.split('<li>')[1:]
    linkList = [restrict(inputString=x, startStr='href="', endStr='" download>') for x in downloadList]
    urlList = ['{0}{1}'.format(baseURL, link) for link in linkList]
    return urlList

# Given a list of links, get the csv files and merge them into a list of dicts
def downloadData(urlList):
    # Make list of all records as dicts
    data = list()
    for url in urlList:
        print('Downloading data from {0}'.format(url))
        item = requests.get(url)
        content = codecs.iterdecode(item.iter_lines(), 'utf-8')
        csvReader = csv.DictReader(content)
        for record in csvReader:
            # Make sure that q&a's are clean
            item = dict()
            for k, v in record.items():
                item[k.strip()] = v.strip()
            data.append(item)

    # Get all questions
    questionSet = set()
    for record in data:
        for k in record.keys():
            questionSet.add(k)

    # Make sure that every dict in data list has the same questions
    outputData = list()
    for record in data:
        newRecord = {question: 'N/A' for question in questionSet if question not in record}
        newRecord.update(record)
        outputData.append(newRecord)

    return outputData

# Read in json data file
def pickUp(path):
    with open(path) as infile:
        item = json.load(infile)
    return item

# Write out json data file
def putDown(item, path):
    print('Writing to {0}'.format(path))
    with open(path, 'w') as outfile:
        json.dump(item, outfile)

# Write out csv data file
def putDownCSV(item, path):
    print('Writing to {0}'.format(path))
    with open(path, 'w') as outfile:
        dataWriter = csv.DictWriter(outfile, fieldnames=item[0].keys())
        dataWriter.writeheader()
        dataWriter.writerows(item)

# Wrapper for initial collection and writing of data
def collectData():
    urlList = getDataURLs()
    print('Found {0} URLs'.format(len(urlList)))
    data = downloadData(urlList)
    print('Collected {0} records'.format(len(data)))
    dataPath = './output/collectedData.json'
    putDown(data, dataPath)
    putDownCSV(data, './output/collectedData.csv')

# Main
# collectData()

data = pickUp(path='./output/collectedData.json')
df = pd.DataFrame.from_records(data)
df['Age'] = df.Age.astype(int)

df1 = df[['Age', 'Are you hungry right now?']]
values = df1['Are you hungry right now?'].unique()
for value in values:
    tempdf = df1[df1['Are you hungry right now?'] == value]
    print(value, len(tempdf))
    tempdf['Age'].plot.box(title=value)
    plt.show()
 