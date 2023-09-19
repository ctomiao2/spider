#! D:\python27\python.exe
# -*- coding: utf-8 -*-
# i6m3y
import sys
sys.path.append('../')
import json
import urllib
import requests
import ScrabCartoon

base_dir = 'E:/LiuBei/cartoon/'
base_host = 'https://www.xxx.com'
image_pattern = '<div class="reader-cartoon-image loaded"><img src="(.*?)".*?>'

def run():
    
    file_confs = {} # <id, {}>
    for i in range(1, 11):
        filename = 'page_%d.json' % i
        with open(filename, 'r') as f:
            dct = json.loads(f.read(), encoding='utf-8')
            for data in dct['result']['list']:
                cat_id = int(data['id'])
                if cat_id in file_confs:
                    continue
                file_confs[cat_id] = data
    
    sort_ids = file_confs.keys()
    sort_ids.sort(key=lambda cat_id: -int(file_confs[cat_id]['view']))
    print 'read_files_conf', len(file_confs)

    
    for idx, cat_id in enumerate(sort_ids):    
        cart_home_url = '%s/home/api/isread/id/%s' % (base_host, cat_id)
        try:
            print 'parse_cart_home, url: %s %s/%s' % (cart_home_url, idx+1, len(sort_ids)) 
            json_dct = requests.get(cart_home_url).json()
            first_chapter_url = '%s/home/book/capter/id/%s' % (base_host, json_dct['data']['capter_id'])
            ScrabCartoon.ScrabCartoon(base_dir, first_chapter_url, file_confs[cat_id], image_pattern)
        except:
            sys.excepthook(*sys.exc_info())


run()


