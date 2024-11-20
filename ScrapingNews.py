import time, re, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from omegaconf import OmegaConf

class ScrapeNews():
    def __init__(self):
        # start headless if you want later on.
        #options = webdriver.ChromeOptions()
        self.driver = None
        self.news_urls = set()
        self.find_button_method = ""
        self.find_button_name = ""
        self.search_patterns = ["chinese-only+signs", "chinese+sign", 
                                                  "chinese-only+signage", "chinese-language+signs",
                                                  "chinese+only+business+signs"
                                                ]
        self.output_file = ""
    # Set search patterns
    def set_search_patterns(self, patterns):
        self.search_patterns = patterns
    # Set output file
    def set_output_file(self, output):
        self.output_file = output
    def scrape_cbc(self):
        options = Options()
        self.driver = webdriver.Chrome(options=options)
        self.news_ulrs = set()
        self.find_button_method = 'class name'
        self.find_button_name = 'loadMore'
        for search_pattern in self.search_patterns:
            url = f"https://www.cbc.ca/search?q={search_pattern}&section=news&sortOrder=relevance&media=all"
            self.driver.get(url)
            time.sleep(2)
            html = self.lazy_scroll()
            parser = BeautifulSoup(html, 'html.parser')
            href_list = parser.find('div', class_='contentListCards').find_all('a', class_='rightImage')
            for item in href_list:
                if item['data-cy'] == 'type-story':
                    link = item['href']
                    self.news_urls.add(f"https://www.cbc.ca{link}")
        self.output(self.output_file)
    
    def lazy_scroll(self, needPressButton = True):
        current_height = self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
        while True:
            self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
            time.sleep(1)
            if needPressButton:  
                try:
                    l = self.driver.find_element(self.find_button_method, self.find_button_name)
                    l.click()
                    time.sleep(1)
                except:
                    return self.driver.page_source
            new_height = self.driver.execute_script('return document.body.scrollHeight')  
            #time.sleep(1)
            if new_height == current_height:      # this means we have reached the end of the page!
                return self.driver.page_source
            current_height = new_height
            
    def output(self, output_file):
        open(output_file, 'a').close()
        with open(output_file, 'w') as file:
            for item in self.news_urls:
                file.write(item)
                file.write('\n')

if __name__ == '__main__':
  config = OmegaConf.load('./params.yaml')
  scrape_agent = ScrapeNews()
  scrape_agent.set_search_patterns(config.scrape.search_pattern)
  scrape_agent.set_output_file(config.scrape.output.search_path)
  scrape_agent.scrape_cbc()