import requests
import json
import os
import re
from bs4 import BeautifulSoup as bs4
from collections import Counter

RE_SP = re.compile('\s+')

def main():
    id_file = "items_diaris_metadata.json"
    out_file = "items_diaris_metadata_text.json"
    ids = json.load(open(id_file))
    for legislatura, plens in ids.items():
        print(legislatura)
        for ple in plens:
            diari_files = []
            for i, url in enumerate(ple['diari_urls']):
                diari_file = construct_path(ple['metadata_file'], i)
                diari_files.append(diari_file)
                if os.path.isfile(diari_file):
                    print('%s already parsed and downloaded'%diari_file)
                else:
                    diari_path = os.path.dirname(diari_file)
                    if not os.path.isdir(diari_path):
                        os.makedirs(diari_path)
                    print(url)
                    session = parse_url(url)
                    with open(diari_file, 'w') as out:
                        json.dump(session, out, indent=2)
            ple['diari_files'] = diari_files

    with open(out_file, 'w') as out:
        json.dump(ids, out, indent=2)

def construct_path(path, i):
    path = path.replace('jsons', 'diaris')
    return path.replace('.json', '_%i.json'%i)

def parse_url(url):
    res = requests.get(url)
    soup = bs4(res.content, 'html.parser')
    spk_attr, spk_style = get_spk_style(soup)
    session = parse(soup, spk_attr, spk_style)
    if session[0]['intervinent'].startswith('Ple'):
        session.pop(0)
    return {'url':url, 'results':session}

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
    intervention['intervencio'] = \
                      clean(intervention['intervencio']).replace('. . .','...')
    intervention['intervinent'] = clean(intervention['intervinent'])
    session.append(intervention)

def clean(string):
    return RE_SP.sub(' ', string).strip()

if __name__ == "__main__":
    main()
