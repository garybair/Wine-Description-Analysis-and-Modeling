import argparse

from bs4 import BeautifulSoup
import os
import shutil
import time
import requests
import re
import json
import glob
import expressvpn

#establish target directories
data = "data"
siteName = "wine-com"

#establish session related data
headerData = {"user-agent": ("")} #TBD

#establish static urls
staticURL = "https://www.wine.com"

class Scraper:

    def __init__(self, minimumCoverage = 1000, validateLinks = True):
        self.session = requests.Session()
        self.start_time = time.time()

    def scrapeLandingPage(self):
        
        #write assembled wine-variant urls to dictionary

    def parseLandingPage(self):
        
        #output list of scraped urls    
    
    def scrapeResultsPage(self):

        #write assembled product page urls to dictionary
        
    def parseResultsPage(self):
        
        #output list of scraped urls 

    def scrapeProductPage(self, productURL):
        productPageResponse = self.session.get(productURL, headers = headerData)
        productPageSoup = BeautifulSoup(productPageResponse.content, "html.parser")
        try:
            return self.parseProductPage(productPageSoup)
        except productPageScrapeException as e:
            with open(f"{self.start_time}_error.log", "a") as log_file:
                log_file.write(f"Error {e} on Product {productURL}\n")

    def parseProductPage(self, productPageSoup):
       
        #return parsed data

    def save_data(self, data):
        
        #write parsed data to file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("minimumCoverage", type=int)
    parser.add_argument("validateLinks", type=bool)

    args = parser.parse_args()

    wine_com_scraper = Scraper(minimumCoverage = args.pages)

    wine_com_scraper.scrape()