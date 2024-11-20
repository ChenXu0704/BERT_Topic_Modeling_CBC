from bs4 import BeautifulSoup
from omegaconf import OmegaConf
import requests
import pandas as pd
def news_screening(config):
  headers = {"User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36"}
  title_element = config.screen.title_element
  #title_element_name = config.screen.title_element_name
  article_element = config.screen.article_element
  article_element_name = config.screen.article_element_name
  match_patterns = config.screen.match_pattern
  infile = config.scrape.output.search_path
  outputfile = config.screen.output.screen_path
  if outputfile.split('.')[-1] != 'csv':
    print("output should be in csv format.")
    exit()
  res = []
  f = open(infile, "r")
  index = 0
  for line in f:
    try:
      if len(line.replace('\n', '')) == 0:
          continue
      line = line.replace('\n', '')
      soup = BeautifulSoup(requests.get(line, headers=headers).text, 'html.parser')
      print(line)
      head = soup.find(title_element).get_text().replace('\n',' ').lower()
      body = soup.find(article_element, class_=article_element_name).get_text().replace('\n',' ').lower()
      content = head + ' ' + body
      for pattern in match_patterns:
        if pattern in content:
          res.append([index, content])
          index += 1
          break
    except:
      continue
  df = pd.DataFrame(res, columns=['id','text'])
  df.to_csv(outputfile, index=False)               


if __name__ == '__main__':
  config = OmegaConf.load('./params.yaml')
  news_screening(config)
