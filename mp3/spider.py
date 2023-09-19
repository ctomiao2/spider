#! D:\python27\python.exe
# -*- coding: utf-8 -*-
# f6f9u
import sys
sys.path.append('../')
import ScrabMultiMP3

scrab_book_params = {
    'book_dir': 'E:/LiuBei/mp3/',
    'base_host': 'https://www.xxxx.com',
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
    'chapter_pattern': '<a class="novel-chapter-item" href="(.*?)">.*?<span class="dec-ti" title="(.*?)">.*?</a>',
    'content_pattern': '<audio class="audio-player-component" controls>.*?<source src="(.*?)".*?>.*?</audio>',
}

category_urls = [
   #('长篇有声', 'https://www.xxx.com/cYcL3lvdXNoZW5nL2xpc3Qt6ZW%2F56%2BH5pyJ5aOwLmh0bWw%3D.html'),
   #('短篇有声', 'https://www.xxx.com/cYcL3lvdXNoZW5nL2xpc3Qt55%2Bt56%2BH5pyJ5aOwLmh0bWw%3D.html'),
]

ScrabMultiMP3.ScrabMultiMP3(category_urls, scrab_book_params)
