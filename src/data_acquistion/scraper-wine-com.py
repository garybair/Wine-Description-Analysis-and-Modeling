from time import sleep
from bs4 import BeautifulSoup
import time
import requests
import json

class Scraper:

    def __init__(self, pullQuantity = 10000):
        self.session = requests.Session()
        self.startTime = time.time()
        self.pullQuantity = pullQuantity
        self.staticURL = 'https://www.wine.com'
        self.siteMapDirectory = '../../data/wine-com/'
        self.filePath = '../../data/wine-com/raw/{}.txt'.format(self.startTime)
        self.headerData = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

       #determine if sitemap exists, initialize if not
        try:
            with open(self.siteMapDirectory + '/site-map.json', 'r') as fileObj:
                self.siteMap = json.load(fileObj)
        except:
            self.siteMap = {}
        
        #generate session file - validated
        with open(self.filePath,'w') as fileObj:
            fileObj.write('url|name|variety|origin|family|description|reviews\n')  
        fileObj.close()
            
    def scrape(self):
        #determine landing page map exists
        if len(self.siteMap) == 0:
            self.scrapeLandingPage()
            self.parseLandingPage()
        #iterate through wine varieties
        sleep(2)
        for key, value in self.siteMap['landingPageLinks'].items():
            self.searchVarietal = key
            self.searchURL = value
            self.scrapeParseResultsPage()
            #write sitemap to JSON file
            with open(self.siteMapDirectory + '/site-map.json', 'w') as fileObj:
                json.dump(self.siteMap, fileObj)
            fileObj.close()

    # validated
    def scrapeLandingPage(self):
        landingPageResponse = self.session.get(self.staticURL, headers = self.headerData)
        self.landingPageSoup = BeautifulSoup(landingPageResponse.content, "html.parser")
    
    #validated
    def parseLandingPage(self):
        self.siteMap['landingPageLinks'] = dict()
        landingPageVarietalsLevel0 = self.landingPageSoup.find('section', attrs = {'class': 'mainNav_section mainNav_section-varietal mainNavList_item-level0'})
        for row in landingPageVarietalsLevel0.find_all('li', attrs = {'class': 'mainNavList_item mainNavList_item-level2'}):
            a_tag = row.find('a', attrs = {'class': 'mainNavList_itemLink'})
            self.varietalName = a_tag.text
            self.varietalLink = a_tag.get('href')
            self.siteMap['landingPageLinks'][self.varietalName] = self.staticURL + self.varietalLink
        #for some reason boxed sets and glassware links are present in varietals tab
        del self.siteMap['landingPageLinks']['Wine Tasting Sets']
        del self.siteMap['landingPageLinks']['Glassware & Accessories']
    
    def scrapeParseResultsPage(self):
        if self.searchVarietal not in self.siteMap:
            self.siteMap[self.searchVarietal] = dict()
        
        self.pullCount = 0
        while self.pullCount < self.pullQuantity and self.searchURL is not None:
            print(self.searchURL)
            resultsPageResponse = self.session.get(self.searchURL, headers = self.headerData)
            self.resultsPageSoup = BeautifulSoup(resultsPageResponse.content, "html.parser")
            resultsContainer = self.resultsPageSoup.find('ul', attrs = {'class':'prodList'})
            for row in resultsContainer.find_all('div', attrs = {'class': 'prodItemInfo'}):
                productShortLink = row.a['href']
                self.productURL = self.staticURL + productShortLink
                if self.productURL not in self.siteMap[self.searchVarietal]:
                    self.scrapeProductPage()
                    self.parseProductPage()
                else:
                    pass
            if self.pullCount < self.pullQuantity:
                try:
                    paginationContainer = self.resultsPageSoup.find('div', attrs = {'class':'nextPagePagination'})
                    self.searchURL = paginationContainer.a['href']
                except Exception:
                    self.searchURL = None
            
    #validated
    def scrapeProductPage(self):
        if self.productURL not in self.siteMap[self.searchVarietal]:
            self.siteMap[self.searchVarietal][self.productURL] = dict()
        
        try:
            productPageResponse = self.session.get(self.productURL, headers = self.headerData)
            self.productPageSoup = BeautifulSoup(productPageResponse.content, "html.parser")
            
            self.siteMap[self.searchVarietal][self.productURL]['scrapeStatus'] = 'success'
        except Exception:
            self.siteMap[self.searchVarietal][self.productURL]['scrapeStatus'] = 'fail'
            
    #validated
    def parseProductPage(self):
        try:
            #generate dictionary for parsed fields
            self.prodData = dict()
            
            #product info
            prodInfo = self.productPageSoup.find('div', attrs = {'class':'pipInfo'})
            self.prodData['Name'] = prodInfo.find('h1', attrs = {'class':'pipName'}).text
            self.prodData['Variety'] = prodInfo.find('span', attrs = {'class':'prodItemInfo_varietal'}).text
            self.prodData['Origin'] = prodInfo.find('span', attrs = {'class':'prodItemInfo_originText'}).text
            
            #product attributes
            prodAttr = self.productPageSoup.find('ul', attrs = {'class':'prodAttr'}).find('li')
            self.prodData['Family'] = prodAttr['title']

            #winemaker notes
            prodNotes = self.productPageSoup.find('div', attrs = {'class':'pipWineNotes_copy viewMoreModule js-expanded'})
            wineMakerNotes = prodNotes.find('div', attrs = {'class': 'viewMoreModule_text'}).text
            wineMakerNotes = wineMakerNotes.replace('\n', ' ')
            self.prodData['Description'] = wineMakerNotes
            
            #professional reviews
            prodProfessionalReviews = self.productPageSoup.find('div', attrs = {'class': 'viewMoreModule_text viewMoreModule-reviews'})
            self.prodData['Reviews'] = ''
            for row in prodProfessionalReviews.find_all('div', attrs = {'class': 'pipProfessionalReviews_list'}):
                reviewData = row.find('div', attrs = {'class': 'pipSecContent_copy'}).text
                reviewData = reviewData.replace('\n', ' ')                             
                self.prodData['Reviews'] = self.prodData['Reviews'] + ';;' + reviewData

            #write data to disk
            self.writeProductData()
            self.siteMap[self.searchVarietal][self.productURL]['parseStatus'] = 'success'
        except Exception:
            self.siteMap[self.searchVarietal][self.productURL]['parseStatus'] = 'fail'
            print('{} parse failed'.format(self.productURL))

    #validated
    def writeProductData(self):
        try:
            with open(self.filePath, 'a') as file:
                file.write('{}|{}|{}|{}|{}|{}|{}\n'.format(self.productURL,
                                                           self.prodData['Name'],
                                                           self.prodData['Variety'],
                                                           self.prodData['Origin'],
                                                           self.prodData['Family'],
                                                           self.prodData['Description'],
                                                           self.prodData['Reviews']))
                file.close()
            self.pullCount += 1
            self.siteMap[self.searchVarietal][self.productURL]['writeStatus'] = 'success'
        except Exception:
            self.siteMap[self.searchVarietal][self.productURL]['writeStatus'] = 'fail'



if __name__ == "__main__":
    wine_com_scraper = Scraper()

    wine_com_scraper.scrape()