# -*- coding: utf-8 -*-
# desc: 爬漫画
import re
import os
import requests
import json
import codecs
import urllib
import ScrabFiles

class ScrabCartoon(object):

    def __init__(self, base_dir, first_chapter_url, cartoon_conf, image_pattern):
        print 'start scrab: ', cartoon_conf['title'], first_chapter_url
        self.base_dir = base_dir
        self.cartoon_conf = cartoon_conf
        resp = urllib.urlopen(first_chapter_url)
        html_body = str(resp.read())#.decode(self.encode)
        first_chapter_images_re = re.findall(image_pattern, html_body, re.S)
        image_urls = []
        for r in first_chapter_images_re:
            image_urls.append(r)
        self.try_scrab_cartoon(image_urls)
    
    def try_scrab_cartoon(self, first_chapter_image_urls):
        first_image_url = first_chapter_image_urls[0]
        print 'try_scrab_cartoon', first_image_url
        file_info_path = None
        cover_path = None
        if '/toptoon/' in first_image_url or '/qootoon/' in first_image_url:
            if '/toptoon/' in first_image_url:
                token = 'toptoon'
            else:
                token = 'qootoon'
            splits = first_image_url.split('/%s/' % token)
            file_host = splits[0]
            cart_id, chapter_id, image_name = splits[-1].split('/')[-3:]
            self.try_scrab_toptoon_chapter(file_host, token, cart_id, chapter_id)
            file_info_path = '%stoptoon/%s/file_info.json' % (self.base_dir, cart_id)
            cover_path = '%stoptoon/%s/cover.%s' % (self.base_dir, cart_id, image_name.split('.')[-1])
            cover_image_url = '%s/%s' % (file_host, self.cartoon_conf['image'])
        # 写下漫画信息
        if file_info_path:
            with codecs.open(file_info_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.cartoon_conf, encoding='utf-8', indent=4))
        # 下载封面
        if cover_path and not os.path.exists(cover_path):
            resp = requests.get(cover_image_url, timeout=15)
			#print 'ScrabFileThread::run', self.url, resp.status_code
            if resp.status_code == 200:
                with open(cover_path, 'wb') as f:
                    f.write(resp.content)
    
    # https://www.xxx.com/toptoon/81011/1/0.jpg
    def try_scrab_toptoon_chapter(self, file_host, token, cart_id, chapter_id):
        next_chapter_id = int(chapter_id) + 1
        next_chapter_dir = '%stoptoon/%s/%s/' % (self.base_dir, cart_id, next_chapter_id)
        # 下一章的目录创建了说明这一章已经爬过了, 直接爬下一章
        if os.path.exists(next_chapter_dir):
            print 'try_scrab_toptoon_chapter, already scrabed, file_host: %s, token: %s, cart: %s, chapter: %s' % (file_host, token, cart_id, chapter_id)
            self.try_scrab_toptoon_chapter(file_host, token, cart_id, next_chapter_id)
            return
        
        # 开始爬这一章的
        cur_batch_valid_url = None
        batch = 0
        batch_num = 10

         # 分批爬取图片
        while True:
            start_idx = batch_num * batch
            batch_image_urls = []
            for idx in range(start_idx, start_idx + batch_num):
                # https://www.xxx.com/toptoon/81011/1/0.jpg
                image_url = '%s/%s/%s/%s/%s.jpg' % (file_host, token, cart_id, chapter_id, idx)
                batch_image_urls.append(image_url)
            # 开始爬这一批次的
            save_dir = '%stoptoon/%s/%s/' % (self.base_dir, cart_id, chapter_id)
            scrabed_urls = self.scrab_batch_images(save_dir, batch_image_urls)
            print 'try_scrab_toptoon_chapter, cart: %s, chapter: %s, batch: %s, batch_image_cnt: %s' % (cart_id, chapter_id, batch, len(scrabed_urls))
            batch += 1
            # 这批次一张都没爬到, 说明这一章节爬完了
            if not scrabed_urls:
                break
            else:
                cur_batch_valid_url = scrabed_urls[0]
        
        # 继续尝试爬下一章节
        if cur_batch_valid_url:
            self.try_scrab_toptoon_chapter(file_host, token, cart_id, next_chapter_id)
    
    def scrab_batch_images(self, save_dir, image_urls):
        scrab_file = ScrabFiles.ScrabFiles(image_urls, save_dir)
        return scrab_file.run()
