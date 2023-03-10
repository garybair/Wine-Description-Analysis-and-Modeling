from bs4 import BeautifulSoup
import time
import requests
import json
import re

class Scraper:

    def __init__(self, pullQuantity = 100000):
        self.session = requests.Session()
        self.startTime = time.time()
        self.pullQuantity = pullQuantity
        self.pullCount = 0
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
            fileObj.write('product_url|product_name|product_variety|product_origin|product_family|user_avg_rating|user_rating_count|product_description|product_reviews\n')  
        fileObj.close()
            
    def scrape(self):
        
        #determine landing page map exists
        if len(self.siteMap) == 0:
            self.scrapeLandingPage()
            self.parseLandingPage()
        
        #iterate through wine varieties
        for key, value in self.siteMap['landingPageLinks'].items():
            self.searchVarietal = key
            self.searchURL = value
            self.scrapeParseResultsPage()

        #determine runtime
        self.totalTimeRan = time.time() - self.startTime
        hours = int(self.totalTimeRan // 3600)
        minutes = int((self.totalTimeRan % 3600) // 60)
        seconds = int(self.totalTimeRan % 60)
        print(f'{self.pullCount} items scraped')
        print(f'Total time taken: {hours} hours, {minutes} minutes, {seconds} seconds')

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
        
        while self.pullCount < self.pullQuantity and self.searchURL is not None:
            print(self.searchURL)
            resultsPageResponse = self.session.get(self.searchURL, headers = self.headerData)
            time.sleep(1)
            self.resultsPageSoup = BeautifulSoup(resultsPageResponse.content, "html.parser")
            resultsContainer = self.resultsPageSoup.find('ul', attrs = {'class':'listGridLayout_list'})
            #iterate through results page
            try:
                for row in resultsContainer.find_all('div', attrs = {'class': 'listGridItemInfo'}):
                    productShortLink = row.a['href']
                    self.productURL = self.staticURL + productShortLink
                    #determine if url has already been scraped
                    if self.productURL not in self.siteMap[self.searchVarietal]:
                        print(self.productURL)
                        self.scrapeProductPage()
                        self.parseProductPage()
                        time.sleep(.5)
            except Exception:
                print(f'{self.searchURL} results page parse fail')
                time.sleep(5)
            #determine if next page exists - if so assign next searchURL
            try:
                paginationContainer = self.resultsPageSoup.find('div', attrs = {'class':'nextPagePagination'})
                self.searchURL = paginationContainer.a['href']
            except Exception:
                self.searchURL = None
                print(f'{self.productURL} pagination fail')
                
            #write sitemap to JSON file
            with open(self.siteMapDirectory + '/site-map.json', 'w') as fileObj:
                json.dump(self.siteMap, fileObj)
            fileObj.close()
            
    #validated
    def scrapeProductPage(self):
        if self.productURL not in self.siteMap[self.searchVarietal]:
            self.siteMap[self.searchVarietal][self.productURL] = dict()
        
        productPageResponse = self.session.get(self.productURL, headers = self.headerData)
        self.productPageSoup = BeautifulSoup(productPageResponse.content, "html.parser")
        
    #validated
    def parseProductPage(self):
        try:
            #generate dictionary for parsed fields
            self.prodData = dict()
            
            #product info - cannot be null
            prodInfo = self.productPageSoup.find('div', attrs = {'class': re.compile(r'pipProdInfo.*')})
            self.prodData['Product_Name'] = prodInfo.find('h1', attrs = {'class':'pipName'}).text
            self.prodData['Product_Variety'] = prodInfo.find('span', attrs = {'class':'prodItemInfo_varietal'}).text
            self.prodData['Product_Origin'] = prodInfo.find('span', attrs = {'class':'prodItemInfo_originText'}).text
            self.prodData['Product_Family'] = self.searchVarietal
            #print(self.prodData['Product_Name'], self.prodData['Product_Variety'], self.prodData['Product_Origin'], self.prodData['Product_Family'])
            
            try:
                #average user product ratings
                self.prodData['User_Avg_Rating'] = self.productPageSoup.find('span', attrs = {'class':'averageRating_average'}).text
            except Exception:
                self.prodData['User_Avg_Rating'] = ''
                print(f'{self.productURL} average user product ratings parse fail')
            #print(self.prodData['User_Avg_Rating'])
                
            try:
                #product ratings count
                self.prodData['User_Rating_Count'] = self.productPageSoup.find('span', attrs = {'class':'averageRating_number'}).text
            except Exception:
                self.prodData['User_Rating_Count'] = ''
                print(f'{self.productURL} product ratings count parse fail')
            #print(self.prodData['User_Rating_Count'])
            
            try:
                #winemaker description
                prodNotes = self.productPageSoup.find('div', attrs = {'class':'pipWineNotes'})
                wineMakerNotes = prodNotes.find('div', attrs = {'class': 'viewMoreModule_text'}).text
                #clean text of characters that may prevent text processing
                wineMakerNotes = wineMakerNotes.replace('\n', ' ')
                wineMakerNotes = wineMakerNotes.replace(',', ' ')
                wineMakerNotes = wineMakerNotes.replace(';', ' ')
                wineMakerNotes = wineMakerNotes.replace('|', ' ')
                self.prodData['Winemaker_Description'] = wineMakerNotes
            except Exception:
                self.prodData['Winemaker_Description'] = ''
                print(f'{self.productURL} winemaker description parse fail')
            #print(self.prodData['Winemaker_Description'])
            
            try:
                #critical reviews
                prodProfessionalReviews = self.productPageSoup.find('div', attrs = {'class': 'viewMoreModule_text viewMoreModule-reviews'})
                self.prodData['Critical_Reviews'] = ''
                reviewList = []
                for row in prodProfessionalReviews.find_all('div', attrs = {'class': 'pipProfessionalReviews_list'}):
                    reviewerName = row.find('div', attrs = {'class': 'pipProfessionalReviews_authorName'}).text
                    reviewerRating = row.find('span', attrs = {'class': 'wineRatings_rating'}).text
                    reviewerText = row.find('div', attrs = {'class': 'pipSecContent_copy'}).text
                    #clean text of characters that may prevent text processing
                    reviewerText = reviewerText.replace('\n', ' ')
                    reviewerText = reviewerText.replace(',', ' ')
                    reviewerText = reviewerText.replace(';', ' ')
                    reviewerText = reviewerText.replace('|', ' ')
                    reviewList.append(f'{reviewerName},{reviewerRating},{reviewerText}')
                self.prodData['Critical_Reviews'] = ';'.join(reviewList)
            except Exception:
                self.prodData['Critical_Reviews'] = ''
                print(f'{self.productURL} critical reviews parse fail')
            #print(self.prodData['Critical_Reviews'])
            
            #write data to disk
            self.writeProductData()
            self.siteMap[self.searchVarietal][self.productURL]['parseStatus'] = 'success'
        except Exception:
            self.siteMap[self.searchVarietal][self.productURL]['parseStatus'] = 'fail'
            print(f'{self.productURL} complete parse failed')

    #validated
    def writeProductData(self):
        try:
            with open(self.filePath, 'a') as file:
                file.write('{}|{}|{}|{}|{}|{}|{}|{}|{}\r\n'.format(self.productURL,
                                                                    self.prodData['Product_Name'],
                                                                    self.prodData['Product_Variety'],
                                                                    self.prodData['Product_Origin'],
                                                                    self.prodData['Product_Family'],
                                                                    self.prodData['User_Avg_Rating'],
                                                                    self.prodData['User_Rating_Count'],
                                                                    self.prodData['Winemaker_Description'],
                                                                    self.prodData['Critical_Reviews']))
            file.close()
            self.pullCount += 1
            self.siteMap[self.searchVarietal][self.productURL]['writeStatus'] = 'success'
        except Exception:
            self.siteMap[self.searchVarietal][self.productURL]['writeStatus'] = 'fail'
            print(f'{self.productURL} write fail')



if __name__ == "__main__":
    wine_com_scraper = Scraper()
    wine_com_scraper.scrape()