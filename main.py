# Imports
import requests
import csv
import codecs

# Functions
def requestURL(inputString):
    if not isinstance(inputString, str):
        raise TypeError('inputString must be a string') 
    r = requests.get(url=inputString)
    if r.status_code != 200:
        raise Exception('Page request unsuccessful: status code {0}'.format(r.status_code))
    return(r.text)

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
def collectData(urlList):
	data = list()
	for url in urlList:
		item = requests.get(url)
		content = codecs.iterdecode(item.iter_lines(), 'utf-8')
		csvReader = csv.DictReader(content)
		for record in csvReader:
			data.append(record)
	return data

# Main
urlList = getDataURLs()
print(urlList)
data = collectData(urlList)
print(len(data))
