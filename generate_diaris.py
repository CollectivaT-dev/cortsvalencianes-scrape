import json
import re
from datetime import datetime

RE_NO = re.compile('^\d*')
URL = 'https://www.cortsvalencianes.es/publicaciones-CV/obtenerHtmlDS?f_clave_dscv=%s&idioma=ca_VA'

def main():
    pages = json.load(open('items.json'))
    legislatures = leg_order(pages)
    generate(legislatures)
    with open('items_diaries.json', 'w') as out:
        json.dump(legislatures, out, indent=2)

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
    for legislature, sessions in legs.items():
        sessions_sorted = sorted(sessions, key=lambda x: x['datetime'])
        for i, session in enumerate(sessions_sorted):
            session['diari_url'] = generate_urls(legislature, i, session)
            session['datetime'] = str(session['datetime'])
        legs[legislature] = sessions_sorted

def generate_urls(key, no, session):
    roman = {'1':'I', '3':'III', '7':'VII', '8':'VIII', '9':'IX', '10':'X'}
    legislature_no = roman[RE_NO.findall(key)[0]]
    code_l = "{:<4}".format(legislature_no)
    code_m = "{:05d}".format(no+1) 
    code = code_l + code_m + '0'
    return URL%code

if __name__ == "__main__":
    main()
