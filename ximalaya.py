#!/usr/bin/env python3

import requests
import html
import json
import sys
import os
from threading import Thread
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def main():
    albumId = sys.argv[1]
    getAlbum(albumId)


def getAlbum(albumId):
    pageNum = 1
    pageSize = 30
    fileList = []

    while True:
        url = f'https://www.ximalaya.com/revision/play/album?albumId={albumId}&pageNum={pageNum}&sort=-1&pageSize={pageSize}'
        print(url)

        r = requests.get(url, headers={'User-Agent': 'curl'})

        if r.status_code != 200:
            print(f'Error, request status code: {r.status_code}')
            return

        jsonstr = html.unescape(r.content.decode('utf-8'))
        album = json.loads(jsonstr)
        hasMore = album['data']['hasMore']
        tracks = album['data']['tracksAudioPlay']
        if not tracks:
            print('Error, no result')
            return

        albumName = tracks[0]['albumName']
        if not os.path.exists(albumName):
            os.makedirs(albumName)

        for t in tracks:
            src = t['src']
            if src != None:
                fileList.append((t['trackName'], src))

        if not hasMore:
            break

        pageNum += 1

    i = 1
    total = len(fileList)
    for name, link in fileList:
        # ximalaya has limit on max connection numbers at same time
        # so we use single thread here
        print(f'[{i}/{total}] {name} - {link}')
        downloadFile(link, albumName, name, '.m4a')
        i += 1

    print('Download complete!')


def downloadFile(url, folder, fileName, ext='.mp3'):
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(connect=3, backoff_factor=3))
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    r = session.get(url)
    if r.status_code == 200:
        with open(f'{folder}/{fileName}{ext}', 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    main()

