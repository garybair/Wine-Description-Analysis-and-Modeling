import argparse

from bs4 import BeautifulSoup
import os
import shutil
import time
import requests
import json
import glob
from expressvpn.wrapper import random_connect


class Scraper:

    def __init__(self, pullQuantity = 1000):
        self.session = requests.Session()
        self.startTime = time.time()
        self.pullQuantity = pullQuantity
        self.staticURL = 'https://www.wine.com'
        self.targetDirectory = 'data/wine-com'
        self.filePath = 'data/wine-com/{}.txt'.format(self.startTime)
        self.headerData = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'

        #determine if target directory exists, generate if not
        if not os.path.isdir(self.targetDirectory): 
            os.mkdir(self.targetDirectory)

       #determine if sitemap exists, initialize if not
        try:
            with open(self.targetDirectory + '/site-map.json', 'r') as fileObj:
                self.siteMap = json.load(fileObj)
        except:
            self.siteMap = {}
        
        #generate session file
        with open(self.filePath,'w') as fileObj:
            fileObj.write('url|name|variety|origin|description|reviews\n')  
        fileObj.close()
            
    def scrape(self):
        #connect to vpn
        random_connect()
        #determine landing page map exists
        if len(self.siteMap) == 0:
            self.scrapeLandingPage()
            self.parseLandingPage()
        else:
            #iterate through wine varieties
            for key, value in self.siteMap['landingPageLinks'].items():
                self.searchVarietal = key
                self.searchURL = value
                self.scrapeParseResultsPage()
        #write sitemap to JSON file
        with open(self.targetDirectory + '/site-map.json', 'w') as fileObj:
            json.dump(self.siteMap, fileObj)
        fileObj.close()

    def scrapeLandingPage(self):
        landingPageResponse = self.session.get(self.staticURL, headers = self.headerData)
        self.landingPageSoup = BeautifulSoup(landingPageResponse.content, "html.parser")

    def parseLandingPage(self):
        self.siteMap['landingPageLinks'] = dict()
        landingPageVarietals = self.landingPageSoup.find('div', attrs = {'class': 'mainNav_section mainNav_section-varietal mainNavList_item-level0'})
        for row in landingPageVarietals.find_all_next('div', attrs = {'class': 'mainNavList'}):
            self.varietalName = row.find('a', attrs = {'class': 'mainNavList_itemLink '}).text
            self.varietalLink = row.find('href', attrs = {'class': 'mainNavList_itemLink '})
            self.siteMap['landingPageLinks'][self.varietalName] = self.varietalLink
        
        #for some reason boxed sets and glassware links are present in varietals tab
        del self.siteMap['landingPageLinks']['Wine Tasting Sets']
        del self.siteMap['landingPageLinks']['Glassware & Accessories']
    
    def scrapeParseResultsPage(self):
        if self.varietalName not in self.siteMap:
            self.siteMap[self.varietalName] = dict()
        
        self.pullCount = 0
        while self.pullCount < self.pullQuantity or self.seachURL is not None:
            random_connect()
            resultsPageResponse = self.session.get(self.seachURL, headers = self.headerData)
            self.resultsPageSoup = BeautifulSoup(resultsPageResponse.content, "html.parser")
            resultsContainer = self.resultsPageSoup.find('ul', attrs = {'class':'prodList'})
            for row in resultsContainer.find_all_next('div', attrs = {'class': 'prodItemInfo'}):
                self.productURL = row.a['href']
                self.scrapeProductPage()
            try:
                paginationContainer = self.resultsPageSoup.find('div', attrs = {'class':'nextPagePagination'})
                self.searchURL = paginationContainer.a['href']
            except Exception:
                self.searchURL = None
        
    def scrapeProductPage(self):
        if self.productURL not in self.siteMap[self.varietalName]:
            self.siteMap[self.varietalName][self.productURL] = dict()
        
        try:
            productPageResponse = self.session.get(self.productURL, headers = self.headerData)
            self.productPageSoup = BeautifulSoup(productPageResponse.content, "html.parser")
            self.siteMap['varietal']['url']['scrapeStatus'] = 'success'
        except Exception:
            self.siteMap['varietal']['url']['scrapeStatus'] = 'fail'
            
    def parseProductPage(self):
        try:
            #generate dictionary for parsed fields
            self.prodData = dict()
            
            #product info
            prodInfo = self.productPageSoup.find('div', attrs = {'class':'pipInfo'})
            self.prodData['Name'] = prodInfo.find('h1', attrs = {'class':'pipName'}).text
            self.prodData['Variety'] = prodInfo.find('span', attrs = {'class':'prodItemInfo_varietal'}).text
            self.prodData['Origin'] = prodInfo.find('span', attrs = {'class':'prodItemInfo_originText'}).text
    
            #winemaker notes
            prodNotes = self.productPageSoup.find('div', attrs = {'class':'pipWineNotes_copy viewMoreModule js-expanded'})
            self.prodData['Description'] = prodNotes.find('div', attrs = {'class': 'viewMoreModule_text'}).text
            
            #professional reviews
            prodProfessionalReviews = self.productPageSoup.find('div', attrs = {'class': 'viewMoreModule_text viewMoreModule-reviews'})
            self.prodReviews = []
            for row in prodProfessionalReviews.find_all_next('div', attrs = {'class': 'pipProfessionalReviews_list'}):
                self.prodReviews.append(row.find('div', attrs = {'class': 'pipSecContent_copy'}).text)                                          
            self.prodData['Reviews'] = ' '.join(self.prodReviews)
            
            #write data to disk
            self.writeProductData()
            self.siteMap['varietal']['url']['parseStatus'] = 'success'
        except Exception:
            self.siteMap['varietal']['url']['parseStatus'] = 'fail'

    def writeProductData(self):
        try:
            with open(self.filePath, 'a') as file:
                file.write('{}|{}|{}|{}|{}\n'.format(self.prodData['Name'], 
                                                     self.prodData['Variety'], 
                                                     self.prodData['Origin'], 
                                                     self.prodData['Description'],
                                                     self.prodData['Reviews']))
                self.pullCount += 1
            self.siteMap['varietal']['url']['writeStatus'] = 'success'
        except Exception:
            self.siteMap['varietal']['url']['writeStatus'] = 'fail'



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("minimumCoverage", type=int)

    args = parser.parse_args()

    wine_com_scraper = Scraper(minimumCoverage = args.pages)

    wine_com_scraper.scrape()