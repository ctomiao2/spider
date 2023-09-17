#! D:\python27\python.exe
# -*- coding: utf-8 -*-
import ScrabMultiBooks

BASE_HOST = '' # the website host
scrab_book_params = {
    'book_dir': 'E:/LiuBei/',
    'base_host': BASE_HOST,
    'book_url_pattern': '<a class="novel-item" href="(.*?)" target="_blank">.*?<div class="novel-item-title dec-ti" title="(.*?)">.*?</a>',
    'book_next_url_pattern': '.*<a href="(.*?)" title="下一页">下一页</a>',
    'book_next_str': '下一页',
    'book_end_url': 'javascript:;',
    'encode': 'utf-8',
    'is_relative_path': True,
    # for AES crypt website
    'decrypt_params': {
        'key': 'replace with your key',
        'iv': 'replace with your iv',
        'padding': 'replace with your padding'
    },
    'chapter_pattern': '<a class="novel-chapter-item" href="(.*?)" target="_blank">.*?<span class="dec-ti" title="(.*?)">.*?</a>',
    'content_pattern': '<div class="novel-detail-content" data-content="(.*?)"></div>',
}

category_urls = [
    # ('分类1', '分类1对应的url'),
    # ('分类2', '分类2对应的url'),
    # ...
]

ScrabMultiBooks.ScrabMultiBooks(category_urls, scrab_book_params)
