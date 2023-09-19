#! D:\python27\python.exe
# -*- coding: utf-8 -*-
import sys
sys.path.append('../')
import ScrabMultiBooks

scrab_book_params = {
    'book_dir': 'E:/LiuBei/novel/',
    'base_host': 'https://www.xxx.com',
    'book_url_pattern': '<a class="novel-item" href="(.*?)" target="_blank">.*?<div class="novel-item-title dec-ti" title="(.*?)">.*?</a>',
    'book_next_url_pattern': '.*<a href="(.*?)" title="下一页">下一页</a>',
    'book_next_str': '下一页',
    'book_end_url': 'javascript:;',
    'encode': 'utf-8',
    'is_relative_path': True,
    'decrypt_params': {
        'key': 'IdTJq0HklpuI6mu8iB%OO@!vd^4K&uXW',
        'iv': '$0v@krH7V2883346',
        'padding': 'pkcs7'
    },
    'chapter_pattern': '<a class="novel-chapter-item" href="(.*?)" target="_blank">.*?<span class="dec-ti" title="(.*?)">.*?</a>',
    'content_pattern': '<div class="novel-detail-content" data-content="(.*?)"></div>',
}

category_urls = [
   # ('category1', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt5Y2B5aSn5ZCN6JGXLmh0bWw%3D.html'),
   # ('category2', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt6ZW%2F56%2BH6L%2Be6L29Lmh0bWw%3D.html'),
   # ('category3', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt6YO95biC55Sf5rS7Lmh0bWw%3D.html'),
   # ('category4', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt5qCh5Zut5pil6ImyLmh0bWw%3D.html'),
   # ('category5', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt5q2m5L6g5Y%2Bk5YW4Lmh0bWw%3D.html'),
   # ('category6', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt5piO5pif57O75YiXLmh0bWw%3D.html'),
   # ('category7', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt5a625bqt5Lmx5LymLmh0bWw%3D.html'),
   # ('category8', 'https://www.xxx.com/cYcL3hpYW9zaHVvL2xpc3Qt5Y2I5aSc5oCq6LCILmh0bWw%3D.html'),
]

ScrabMultiBooks.ScrabMultiBooks(category_urls, scrab_book_params)
