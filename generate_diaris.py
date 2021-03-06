import json
import re
import os
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs4

RE_NO = re.compile('^\d*')
URL = 'https://www.cortsvalencianes.es/publicaciones-CV/obtenerHtmlDS?f_clave_dscv=%s&idioma=ca_VA'
MONTH = {"gener":  1,
        "febrer": 2,
        "març":   3,
        "abril":  4,
        "maig":   5,
        "juny":   6,
        "juliol": 7,
        "agost":  8,
        "setembre": 9,
        "octubre":  10,
        "novembre": 11,
        "desembre": 12}

if os.path.isfile('cache.json'):
    with open('cache.json') as cache:
       CACHE = json.load(cache)
INITIAL_LEN = len(CACHE.keys())

def main():
    pages = json.load(open('items.json'))
    legislatures = leg_order(pages)
    diaris = generate(legislatures)
    with open('diaris.json', 'w') as out:
        json.dump(diaris, out, indent=2)

def leg_order(pages):
    legislatura = {}
    for page in pages.values():
        for session in page:
            leg = session.get('Legislatura/Mandato:')
            if not leg:
                msg = 'legislature info not found for %s'%str(session)
                print(msg)
            else:
                session['datetime'] = datetime.strptime(session['Fecha:'],
                                                    '%d/%m/%Y %H:%M')
                if not legislatura.get(leg):
                    legislatura[leg] = []
                if 'Ple' in session['title']:
                    legislatura[leg].append(session)
    return legislatura

def generate(legs):
    diaris_leg = {}
    for legislature, sessions in legs.items():
        diaris = []
        sessions_sorted = sorted(sessions, key=lambda x: x['datetime'])
        print(legislature)
        doc_no = 0
        diari_date = datetime.now()
        while diari_date != None:
            diari_date, diari_session, url = find_urls(legislature, doc_no)
            cache_length = len(CACHE.keys())
            diari = {'legislatura': legislature,
                     'sessio': diari_session,
                     'date': str(diari_date),
                     'url': url}
            diaris.append(diari)
            if cache_length%10 == 0 and cache_length != INITIAL_LEN:
                with open('cache.json', 'w') as out:
                    json.dump(CACHE, out, indent=2)
            doc_no += 1
        diaris_leg[legislature] = diaris
        with open('cache.json', 'w') as out:
            json.dump(CACHE, out, indent=2)
    return diaris_leg

def find_urls(key, no):
    diari_url = generate_urls(key, no)
    diari_date, diari_sessio = parse_diari(diari_url)
    print(diari_date, diari_sessio)
    return diari_date, diari_sessio, diari_url

'''
def parse_metadata_sessio(title):
    title_step = title.replace('(Ple ', 'Ple (')
    title_step2 = title_step.replace('Sessió Ple','Sessió ')+' Ple'
    title_clean = re.sub('\([^)]*\)','', title_step2).replace('  ',' ')
    result = re.search('Sessió (\d+) Ple', title_clean)
    part = 0
    sessio_2 = None
    if not result:
        # check if sessio is in two parts
        result = re.search('Sessió (\d+)-(\d) Ple', title_clean)
        if result:
            part = int(result.groups()[1])
        else:
            # check if the day has two sessions
            result = re.search('Sessió (\d+) i (\d+) Ple', title_clean)
            sessio_2 = [int(result.groups()[1])]
    sessions = [int(result.groups()[0])]
    if sessio_2:
        sessions + sessio_2
    return sessions, part
'''

def generate_urls(key, no):
    roman = {'1':'I', '3':'III', '7':'VII', '8':'VIII', '9':'IX', '10':'X'}
    legislature_no = roman[RE_NO.findall(key)[0]]
    code_l = "{:<4}".format(legislature_no)
    code_m = "{:05d}".format(no+1) 
    code = code_l + code_m + '0'
    return URL%code

def parse_diari(url):
    if CACHE.get(url):
        print('diari cached')
        date, diari_sessio = CACHE[url]
        diari_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return diari_date, diari_sessio
    else:
        res = requests.get(url)
        print(url)
        soup = bs4(res.content, 'html.parser')
        element = soup.findChildren()
        if element:
            text_full = soup.findChildren()[0].text
            text = text_full[:1000]
            clean_text = re.sub('’|‘', "'", re.sub('\s\s+',' ',text))
            date = parse_date(clean_text)
            sessio = parse_sessio(clean_text)
            CACHE[url] = (str(date), sessio)
            return date, sessio
        else:
            # reached the end of the diaris
            return None, None

def parse_date(clean_text):
    # get day
    result = re.search('el dia (\d+) de ([a-zç]+) de (\d+)', clean_text)
    if not result:
        result = re.search("el dia (\d+) d'([a-z]+) de (\d+)", clean_text)
        if not result:
            raise ValueError('date not found in text: %s'%clean_text[:200])
    day, month, year = result.groups()
    # get hour
    result = re.search('(\d+) hores', clean_text)
    if not result:
        raise ValueError('hour not found in text: %s'%clean_text[:200])
    hour = result.groups()[0]
    result = re.search(' i (\d+) minut', clean_text)
    if result:
        minute = result.groups()[0]
    else:
        minute = 0
    return datetime(int(year), MONTH[month], int(day), int(hour), int(minute))

def parse_sessio(clean_text):
    result = re.search('plenària número (\d+)', clean_text)
    if not result:
        result = re.search('plenàària núúmero (\d+)', clean_text)
        if not result:
            raise ValueError('sessio not found in text: %s'%clean_text[150:300])
    return int(result.groups()[0])

if __name__ == "__main__":
    main()
