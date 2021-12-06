from bs4 import BeautifulSoup as bs4
import requests
import os
import json
import re

PATH = os.path.dirname(os.path.realpath(__file__))

def main():
    id_file = "items_diaris.json"
    if os.path.isfile(id_file):
        with open("items_diaris.json") as f:
            items_diaris = json.load(f)
        get_metadata(items_diaris)
        with open(id_file.replace('.json', '_metadata.json'), 'w') as out:
            json.dump(items_diaris, out, indent=2)

def get_metadata(items_diaris):
    for legislatura, plens in items_diaris.items():
        for ple in plens:
            ple['id'] = get_id(ple['url'])
            ple['metadata_file'] = generate_path(ple['id'])
            download_metadata(ple)

def get_id(url):
    res = requests.get(url)
    soup = bs4(res.content, 'html.parser')
    m = soup.find("meta",attrs={"name":"seneca:item_id"})
    ple_id = m.attrs['content']
    try:
        int(ple_id)
    except:
        msg = "The id parsing has failed for %s with the result %s"%(url, ple_id)
        raise ValueError(msg)
    return ple_id 

def generate_path(ple_id):
    if len(ple_id) >= 2:
        dir2 = ple_id[1]
    else:
        dir2 = '0'
    ple_path = os.path.join('jsons', ple_id[0], dir2)
    if not os.path.isdir(ple_path):
        os.makedirs(ple_path)
    return os.path.join(ple_path, ple_id+'.json')

def download_metadata(ple):
    if not os.path.isfile(ple['metadata_file']):
        url = 'https://mediateca.cortsvalencianes.es/api/items/%s/playlist.json'%ple['id']
        print('downloading %s'%url)
        res = requests.get(url)
        with open(ple['metadata_file'], 'wb') as out:
            out.write(res.content)
        try:
            json.load(open(ple['metadata_file']))
        except:
            msg = 'Json format not found in %s'%url
            # TODO delete file
            raise ValueError(msg)
    else:
        print('%s was downloaded'%ple['metadata_file'])

if __name__ == "__main__":
    main()
