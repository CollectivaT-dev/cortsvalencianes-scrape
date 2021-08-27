from bs4 import BeautifulSoup as bs4

import requests
import os
import json

def main():
    query_url = 'https://mediateca.cortsvalencianes.es/library/items?page={}&action=index&controller=library%2Fitems&date=&date_from=&date_to=&gbody_id=&legs_id=&search_type=1&speaker_id=&text=&utf8=%E2%9C%93&view_type=list'
    max_page = get_max_page(query_url)
    localizer_pages = get_localizer_pages(query_url, max_page)

    localizer_dict = {}
    for i, page in enumerate(localizer_pages):
        localizer_dict[i] = extract_localizer_page(page)

    with open('items.json', 'w') as out:
        json.dump(localizer_dict, out, indent=2)

def get_max_page(query_url):
    # TODO parse query results maximum no of pages 
    return 154

def get_localizer_pages(query_url, max_page):
    localizer_pages = []
    for i in range(max_page)[::-1]:
        localizer_pages.append(query_url.format(i+1))
    return localizer_pages

def extract_localizer_page(url):
    res = requests.get(url)
    soup = bs4(res.content, 'html.parser')
    localizer_list = soup.findAll('div', attrs={'class':'localizer_list'})
    
    gallery_items = []
    for localizer in localizer_list:
        gallery_item = {}
        a_element = localizer.find('a', attrs={'class':'h2'})
        div_details = localizer.find('div', attrs={'class':'details'})
        #gallery_items_debug.append((a_element, div_details))
        gallery_item['url'] = a_element['href']
        gallery_item['title'] = a_element.text
        # TODO parse div_details metadata
        gallery_items.append(gallery_item)
    return gallery_items

if __name__ == "__main__":
    main()
