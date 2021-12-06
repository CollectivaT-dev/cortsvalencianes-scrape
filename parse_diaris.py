import requests
from bs4 import BeautifulSoup as bs4
from collections import Counter

def main():
    pass

def parse_url(url):
    res = requests.get(url)
    soup = bs4(res.content, 'html.parser')
    spk_attr, spk_style = get_spk_style(soup)
    print(spk_attr, spk_style)
    session = parse(soup, spk_attr, spk_style)
    return session

def get_spk_style(soup):
    # return the class of the first line, which is always bold
    for element in soup.find_all('span'):
        if len(element.text) > 5:
            # to avoid the <br/>s
            bold_line = element
            break
    key, values = list(bold_line.attrs.items())[0]
    if type(values) == list:
        value = values[0]
    else:
        value = values
    return key, value

def parse(soup, spk_attr, spk_style):
    session = []
    intervention = {}
    for text_el in soup.find_all('span'):
        print(text_el.attrs)
        el_attr = text_el.attrs.get(spk_attr)
        if type(el_attr) == list:
            el_attr = el_attr[0]
        if el_attr == spk_style and len(text_el.text) > 4:
            # to avoid the lines with bold style but no text
            if intervention:
                append_and_clean(session, intervention)
            intervention = {}
            intervention['intervinent'] = text_el.text
            intervention['text'] = []
        else:
            if session:
                intervention['text'].append(text_el.text)
    append_and_clean(session, intervention)
    return session

def append_and_clean(session, intervention):
    intervention['intervencio'] = ''.join(intervention['text'])
    intervention.pop('text')
    session.append(intervention)

'''
def parse_old(soup):
    txt_style = get_txt_style(soup)
    spk_style = get_spk_style(soup)
    

def get_txt_style(soup):
    classes = []
    for span in soup.find_all('span'):
        classes.append(span.attrs['class'][0])
    return Counter(classes).most_common()[0][0]
'''

if __name__ == "__main__":
    main()
