from lxml import html
import requests
import csv
import time

filename = time.strftime("%Y%m%d%H%M")

f = open('output/'+filename+'.csv', 'w', newline='\n')
with f:
    fnames = ['Name', 'Symbol', 'Last', 'High', 'Low', 'Vol', 'Mcap']
    writer = csv.DictWriter(f, fieldnames=fnames)
    writer.writeheader()


headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36',
    'Host':'www.investing.com',
    'Referer':'https://www.investing.com'
}

fheaders = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36',
    'Host':'www.investing.com',
    'Referer':'https://www.investing.com',
    'X-Requested-With':'XMLHttpRequest'
}
for i in range(1, 6):
    URL = 'https://www.investing.com/indices/nasdaq-composite-components'
    if i == 1:
        page = requests.get(URL, headers=headers)
        tree = html.fromstring(page.content)
    else:
        URL = URL + '/' + str(i)
        page = requests.get(URL, headers=headers)
        tree = html.fromstring(page.content)
    
    mcap = tree.xpath('//*[@id="filter_fundamental"]/@onclick')[0]
    mystring = mcap.split(",")
    reqId = mystring[5].split("\'")
    cookieID = reqId[1]
    fURL = 'https://www.investing.com/indices/Service/FundamentalInstrument?pairid=14958&sid='+cookieID+'&filterParams=&smlID=2035303&page=%s' % i
    fpage = requests.get(fURL, headers=fheaders)
    ftree = html.fromstring(fpage.content)
    
    count = tree.xpath('//*[@id="cr1"]/tbody/tr')
    countnum = (len(count)) + 1
    
    for order in range(1, countnum):
        name = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[2]' % order)[0].text_content()
        last = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[3]' % order)[0].text_content()
        high = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[4]' % order)[0].text_content()
        low = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[5]' % order)[0].text_content()
        vol = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[8]' % order)[0].text_content()
        mcap = ftree.xpath('//*[@id="fundamental"]/tbody/tr[%s]/td[4]' % order)[0].text_content()
    
        symbolname = name
    
        with open('nasdaq-symbols.csv') as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                if row[0] == symbolname:
                    symbol = row[1]
        
        f = open('output/'+filename+'.csv', 'a', newline='\n')
        with f:
            fnames = ['Name', 'Symbol', 'Last', 'High', 'Low', 'Vol', 'Mcap']
            writer = csv.DictWriter(f, fieldnames=fnames)
            writer.writerow({'Name' : name, 'Symbol': symbol, 'Last': last, 'High': high, 'Low': low, 'Vol': vol, 'Mcap': mcap})