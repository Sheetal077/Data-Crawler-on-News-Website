from requests_html import HTMLSession 
from bs4 import BeautifulSoup 
from dateparser import parse 
from urllib.parse import urljoin 
from dateparser.search import search_dates
import pandas as pd
from selenium import webdriver
from time import sleep

session = HTMLSession()

base_url = 'https://malayalam.indianexpress.com/'

# SECTION LINKS
def get_section_links(retry = 3):
    r = session.get(base_url, timeout = 180) 
    soup = BeautifulSoup(r.content, 'lxml') 
    section = soup.find('ul',{'id':'menu-main-navigation-menu'}).find_all('a')
    section_links = [urljoin(base_url, x.attrs['href']) for x in section]
    ignore_list = ['https://malayalam.indianexpress.com/opinion/',
                   'https://malayalam.indianexpress.com/children/']
    section_links = [url for url in section_links if url != base_url and url not in ignore_list]
    return section_links

section_links = get_section_links()
article_links = []
# ARTICLE
def get_article(url, retry = 3):
#for url in article_links: break
    r =session.get(url, timeout = 180)
    soup = BeautifulSoup(r.content, 'lxml')
    row = {} 
    row['title'] = soup.find('h1',{'class':'wp-block-post-title'}).text.strip() 
    row['pubDate'] = search_dates(soup.find('div',{'class':'ie-network-post-meta-date'}).text.strip())[0][1]
    row['description'] = '\n'.join([p.text.strip() for p in soup.find('div',{'class':'entry-content wp-block-post-content'}).find_all('p')]) 
    row['link'] = url
    return row

def get_article_links_frm_page(soup, retry= 3):
    #for url in section_links: break
    #r = session.get(url,timeout = 3*60)
    #soup = BeautifulSoup(r.content,features='lxml')
    articles =[urljoin(base_url,x.find('a').attrs['href']) for x in soup.find('div',{'class':'wp-block-column ie-network-grid__lhs'}).find_all('div',{'class':'entry-title'})]  
    article_links = []
    for article in articles: #break
        try :
            row = get_article(article)
            if not row:
                continue
            date = row['pubDate']
            title = row['title']
                
            if date > upto:
                article_links.append(row)
            elif date == upto:
                if title not in titles:
                    article_links.append(row)
            else:
                return article_links, True
        except:
            pass
    if len(article_links) > 0:
        return article_links, False
    return article_links, True

def get_article_links(url):
    article_links = []
       
    driver = webdriver.Chrome(executable_path='F:/Aakash/New folder/chromedriver.exe')
    driver.get(url)
    print(url)
    while True:
        #find last _article
        e = driver.find_elements_by_xpath("//div[@class='wp-block-column ie-network-grid__lhs']//div[@class='entry-title']")[-1]
        link = e.find_element_by_tag_name('a').get_attribute('href')
        row = get_article(link)
        try:
            if row['pubDate'] >= upto:
                load_more = driver.find_element_by_xpath("//div[@class='td-load-more-wrap']")
                load_more.click()
        except:
            break
        else:
            break
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    sleep(0.1)
    pg_article_links, last_page = get_article_links_frm_page(soup)
    article_links.extend(pg_article_links)
    driver.quit()
    return article_links

upto = parse('25 July 2021')
titles = []
article_links = []
for url in section_links:
    article_links.extend(get_article_links(url))

Malayalam_Indian_Express = pd.DataFrame(article_links)
Malayalam_Indian_Express .to_csv("Malayalam_Indian_Express .csv")








































































