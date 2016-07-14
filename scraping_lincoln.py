import pandas as pd
import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
base = 'http://quod.lib.umich.edu/cgi/t/text/text-idx?page=browse&c=lincoln'
from sqlalchemy import create_engine

titles = []
doc_links = []

titles_test = []
links_test = []
texts = []
# Define a helper function that returns the soup for a given url
def get_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    return soup


# Define a function to pull the volume links for Lincoln's collected writings
def get_lincoln_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    editions = soup.find('table', {'class':'browselist'}).findAll('td', {'class':'browsecell'})
    links  = [tag.find('a').get('href') for tag in editions if 'href' in str(tag)]
    return links

links = get_lincoln_links(base)


# Append all of the titles to a list of titles. There's a quirk in the way that
# volume 8 is structured, and the appendix kicks an error when it gets hit by this scraper
# I think I may build a separate scraper for this volume.
for item in links[0:7]:
    link_soup = get_soup(item)
    body = link_soup.find('div', {'id':'toclist'})
    for thing in body.findAll('div', {'class':'indentlevel1'}):
        titles.append(thing.find('span', {'class':'divhead'}).text)
        doc_links.append(thing.find('div', {'class':'resindentlevelx'}).find('a').get('href'))


# Define a function that returns the text from a link
def link_text(url):
    link_soup = get_soup(url)
    lincoln_said = link_soup.find('div', {'class':'textindentlevelx'}).text
    return lincoln_said

for link in doc_links:
    texts.append(link_text(link))
    time.sleep(1)


x = pd.DataFrame(titles, columns = ['title']).join(pd.DataFrame(doc_links, columns=['links']), how='left')
final = x.join(pd.DataFrame(texts, columns = ['text']))


# engine = create_engine('postgresql://cl65610:**********@lincolnlp.cdxjo0ppmsos.us-east-1.rds.amazonaws.com:5432/lincolnlp')
final.to_sql('lincoln_said', engine)



vol_8 = [links[7]]

len(titles)
len(doc_links)
# Remove the last superflous element in the titles list
titles.pop()
# Volume 8 scraper
for item in vol_8:
    link_soup = get_soup(item)
    body = link_soup.find('div', {'id':'toclist'})
    for thing in body.findAll('div', {'class':'indentlevel1'}):
        titles.append(thing.find('span', {'class':'divhead'}).text)
        doc_links.append(thing.find('div', {'class':'resindentlevelx'}).find('a').get('href'))

vol_8_texts = []
len(vol_8_texts)
titles[814]
doc_links[815]
vol_8_texts[814]
count = 0
def link_text(url):
    link_soup = get_soup(url)
    lincoln_said = link_soup.find('div', {'class':'textindentlevelx'}).text
    return lincoln_said

for link in doc_links:
    vol_8_texts.append(link_text(link))
    time.sleep(1)
    count+=1
    print count


len(vol_8_texts)
vol_8_df = pd.DataFrame(titles, columns = ['title']).join(pd.DataFrame(doc_links, columns=['links']), how='left')
final_vol_8 = vol_8_df.join(pd.DataFrame(vol_8_texts, columns=['text']))
final_vol_8.to_sql('lincoln_vol_8', engine)
