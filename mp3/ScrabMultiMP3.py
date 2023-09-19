# -*- coding: utf-8 -*-
import re
import os
import requests
import ScrabBase
import ScrabMultiBooks

class ScrabMP3(ScrabMultiBooks.ScrabBook):
	
	def __init__(self, *args, **kwargs):
		# content就是MP3的url不需要解密, 但是title需要解密
		self.title_decrypt_params = kwargs.get('decrypt_params', None)
		if kwargs.get('decrypt_params', None):
			del kwargs['decrypt_params']
		super(ScrabMP3, self).__init__(*args, **kwargs)

	def do_write_to_file(self):
		while self.last_start_seq < self.seq:
			#print cached_txt.get(self.last_start_seq, '')
			try:
				mp3_url = ScrabBase.cached_txt.get(self.last_start_seq, '')
				if mp3_url:
					# 基类会在前面加上title, 这里并不需要
					title, mp3_url = mp3_url.split('\r\n\r\n')
					title = title.strip()
					self._do_write_mp3(title, mp3_url)
			except:
				import sys
				sys.excepthook(*sys.exc_info())
			self.last_start_seq += 1
		
		ScrabBase.cached_txt.clear()
		self.threads = []
	
	def _do_write_mp3(self, title, mp3_url):
		if self.title_decrypt_params:
			iv = self.title_decrypt_params.get('iv', None)
			padding = self.title_decrypt_params.get('padding', None)
			title = ScrabBase.decrypt_content(title, self.title_decrypt_params['key'], iv, padding, self.encode)
		save_path = '%s/%s.%s' % (self.book_name, title, mp3_url.split('.')[-1])

		# 已经取过了
		if os.path.exists(save_path):
			print '%s already fetched' % title
			return
		
		print 'ScrabMP3::_do_write_mp3', save_path, mp3_url, title
		resp = requests.get(mp3_url)
		#print 'ScrabFileThread::run', self.url, resp.status_code
		if resp.status_code == 200:
			with open(save_path, 'wb') as f:
				f.write(resp.content)
		else:
			print '%s not exist in remote' % mp3_url

class ScrabMultiMP3(ScrabMultiBooks.ScrabMultiBooks):

	def init_scrabed_books(self):
		pass
	
	def add_scrabed_books(self, book_url):
		pass

	def save_scrabed_books(self):
		pass

	def begin_scrab_book(self, category, book_url, book_name, progress):
		base_host = self.book_params['base_host']
		encode = self.book_params['encode']
		is_relative_path = self.book_params['is_relative_path']
		decrypt_params = self.book_params.get('decrypt_params', None)
		chapter_pattern = self.book_params['chapter_pattern']
		content_pattern = self.book_params['content_pattern']
		book_dir = '%s%s' % (self.book_params.get('book_dir', ''), book_name)
		if os.path.exists(book_dir):
			print 'begin_scrab_book, already scrabed', category, book_url, book_name, progress
			return
		print 'begin_scrab_book', category, book_url, book_name, progress
		os.mkdir(book_dir)
		book_next_url_pattern = self.book_params.get('book_next_url_pattern', None)
		book_next_str = self.book_params.get('book_next_str', None)
		book_end_url = self.book_params.get('book_end_url', None)
		scrab_mgr = ScrabMP3(book_dir, base_host, book_url, chapter_pattern, content_pattern, 
			encode=encode, is_relative_path=is_relative_path, decrypt_params=decrypt_params,
			book_next_url_pattern=book_next_url_pattern, book_next_str=book_next_str, book_end_url=book_end_url)
		scrab_mgr.run()
