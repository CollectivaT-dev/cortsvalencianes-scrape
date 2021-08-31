import json
import os
import re
import requests
from m3u8_dl import M3u8Context, M3u8Downloader, PickleContextRestore
from m3u8_dl.cli import execute
from subprocess import Popen, PIPE

class Stream(object):
    def __init__(self, script_url, base_name):
        self.script_url = script_url
        self.base_name = base_name

        # process variables
        self.pointer_urls = []
        self.chunklist = None
        self.chunklist_url = None
        self.stream_filename = None
        self.full_stream_path = None

    def download_stream(self):
        # TODO assert params exist
        if not self.chunklist_url:
            self.get_chunklist()
        restore = PickleContextRestore()
        context = M3u8Context(file_url=self.chunklist_url,
                              referer='',
                              threads=5,
                              output_file=self.full_stream_path,
                              get_m3u8file_complete=False,
                              downloaded_ts_urls=[],
                              quiet=False)
        context['base_url'] = os.path.dirname(self.chunklist_url) + '/'
        context['sslverify'] = False

        if not os.path.isfile(self.full_stream_path):
            execute(restore, context)
        else:
            msg = '%s is available skipping'
            print(msg)

    def get_chunklist(self):
        if not self.pointer_urls:
            self.get_pointer_url()
        # TODO loop for multiple pointer_urls
        res = requests.get(self.pointer_urls[0], verify=False)
        playlist_url = res.url
        base_url = os.path.dirname(playlist_url)

        for element in str(res.content).strip().split('\\n'):
            if 'chunklist' in element:
                self.chunklist = element
                break
        if self.chunklist:
            self.chunklist_url = playlist_url.replace('playlist.m3u8','')+\
                                           self.chunklist
        else:
            # logging
            raise ValueError('chunklist not found in playlist')

        chunk_code = re.sub('(chunklist_)|(\.m3u8)', '', self.chunklist)
        self.stream_filename = '_'.join([self.base_name, chunk_code])+'.ts'
        page = self.base_name.split('_')[0]
        # TODO add absolute path
        stream_path = os.path.join('sessions', page)
        self.full_stream_path = os.path.join(stream_path, self.stream_filename)

        if not os.path.exists(stream_path):
            os.makedirs(stream_path)

    def get_pointer_url(self):
        # TODO parse JS and get all parts
        res = requests.get(self.script_url, verify=False)
        search = re.search('JSPLAYLIST.*m3u8.*?;',str(res.content))
        if search:
            script = search.group()
        else:
            msg = 'js script not found'
            raise ValueError(msg)

        # parse JS
        playlist_vars = list(set(re.findall('JSPLAYLIST1\[\d\]', script)))
        if len(playlist_vars) == 0:
            msg = 'stream pointer urls not found in script'
            raise ValueError(msg)
        for i in range(len(playlist_vars)):
            elements = re.findall('JSPLAYLIST1\[%i\].*?;'%(i+1), script)
            if len(elements) == 0:
                msg = 'stream pointer elements not found'
                raise ValueError(msg)
            # TODO parse all elements
            for element in elements:
                if 'm3u8' in element:
                    search = re.search('http.*?m3u8', element)
                    if search:
                        self.pointer_urls.append(search.group())
                    else:
                        msg = 'stream pointer url not found for element %i'%i
                        raise ValueError(msg)
                    break

def download_stream(recording, name):
    stream = Stream(recording['url'], name)
    #stream.get_pointer_url()
    stream.download_stream()

def main():
    items = json.load(open('items.json'))
    for page, recordings in items.items():
    #for page, recordings in list(items.items())[-2:-1]:
        for i, recording in enumerate(recordings):
            if 'Ple' in recording['title']:
                if not recording.get('uri'):
                    name = '_'.join([page,str(i)])
                    print('downloading %s'%(recording['title'].strip()))
                    download_stream(recording, name)

if __name__ == "__main__":
    main()
