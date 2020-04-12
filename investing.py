import threading
from lxml import html
import requests
import csv
from datetime import date, timedelta
import logging
import time

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")
MainURL = 'https://www.investing.com'

def thread_function(market):
    today = date.today()
    filename = market + "-" + str(today - timedelta(days = 1))
    # file oluşturma
    f = open('output/'+filename+'.csv', 'w', newline='\n')
    with f:
        fnames = ['PairID', 'Name', 'Symbol', 'Last', 'Chg.', 'Chg.%', 'Vol', 'Mcap']
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
    
    pagecounURL = 'https://www.investing.com/indices/'+market+'-composite-components'
    pagecountreq = requests.get(pagecounURL, headers=headers)
    pagecounttree = html.fromstring(pagecountreq.content)
    pagecount = len(pagecounttree.xpath('//*[@id="paginationWrap"]/div[2]/a')) + 1
    logging.info("%s pages found in %s." % ((pagecount - 1), market.title()))
    for i in range(1, pagecount):
        URL = 'https://www.investing.com/indices/'+market+'-composite-components'
        logging.info("%s page %s scraping started." % (market.title(), str(i)))
        if i == 1:
            page = requests.get(URL, headers=headers)
            tree = html.fromstring(page.content)
        else:
            URL = URL + '/' + str(i)
            page = requests.get(URL, headers=headers)
            tree = html.fromstring(page.content)
    
        mcap = tree.xpath('//*[@id="filter_fundamental"]/@onclick')[0]
        getsmlID = tree.xpath('//*[@id="leftColumn"]/script[1]/text()')[0]
        cookieID = mcap.split(",")[5].split("\'")[1]
        pairID = mcap.split(",")[4].split("\'")[0]
        
        for line in getsmlID.split("\n"):
            if "window.siteData.smlID" in line:
                line = line.replace(';', '').strip().split( )
                smlID = line[2]
    
        fURL = 'https://www.investing.com/indices/Service/FundamentalInstrument?pairid='+pairID+'&sid='+cookieID+'&filterParams=&smlID='+smlID+'&page=%s' % i
        fpage = requests.get(fURL, headers=fheaders)
        ftree = html.fromstring(fpage.content)
    
        rowcount = len(tree.xpath('//*[@id="cr1"]/tbody/tr')) + 1
    
        for order in range(1, rowcount):
            pairid = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[2]/span/@data-id' % order)[0]
            name = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[2]' % order)[0].text_content()
            last = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[3]' % order)[0].text_content()
            chg = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[6]' % order)[0].text_content()
            chgpercent = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[7]' % order)[0].text_content()
            vol = tree.xpath('//*[@id="cr1"]/tbody/tr[%s]/td[8]' % order)[0].text_content()
            mcap = ftree.xpath('//*[@id="fundamental"]/tbody/tr[%s]/td[4]' % order)[0].text_content()
            symbol = None
            with open(''+market+'-symbols.csv', encoding='utf-8') as csvDataFile:
                csvReader = csv.reader(csvDataFile)
                for row in csvReader:
                    if row[0] == name:
                        symbol = row[1]

            if symbol is None:
                logging.error("\"%s\" Symbol Not Found in %s! Researching started." % (name, market.title()))
                href = tree.xpath('//a[text()="%s"]/@href' % name)[0]
                time.sleep(3)
                detail = requests.get(MainURL + href, headers=headers)
                detailtree = html.fromstring(detail.content)
                symbol = detailtree.xpath('//meta[@itemprop="tickerSymbol"]/@content')[0]
                f = open(''+market+'-symbols.csv', 'a', newline='\n')
                with f:
                    fnames = ['Name', 'Symbol']
                    writer = csv.DictWriter(f, fieldnames=fnames)
                    writer.writerow({'Name' : name, 'Symbol': symbol})
                logging.info("\"%s\" Symbol found in %s : %s" % (name, market.title(), symbol))

            f = open('output/'+filename+'.csv', 'a', newline='\n')
            with f:
                fnames = ['PairID', 'Name', 'Symbol', 'Last', 'Chg.', 'Chg.%', 'Vol', 'Mcap']
                writer = csv.DictWriter(f, fieldnames=fnames)
                writer.writerow({'PairID' : pairid, 'Name' : name, 'Symbol': symbol, 'Last': last, 'Chg.': chg, 'Chg.%': chgpercent, 'Vol': vol, 'Mcap': mcap})
        logging.info("%s page %s scraping Finished." % (market.title(), str(i)))
    logging.info("Finish the Investing '%s' Job! :)" % market.title())
if __name__ == "__main__":
    nysethread = threading.Thread(target=thread_function, args=("nyse",))
    nasdaqthread = threading.Thread(target=thread_function, args=("nasdaq",))
    nysethread.start()
    nasdaqthread.start()
