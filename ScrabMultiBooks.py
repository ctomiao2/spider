#! D:\python27\python.exe
# -*- coding:utf-8 -*-
import re
import os
import urllib
import ScrabBase

class ScrabBook(ScrabBase.ScrabBase):

	def __init__(self, *args, **kwargs):
		super(ScrabBook, self).__init__(*args, **kwargs)
		self.book_next_url_pattern = kwargs.get('book_next_url_pattern', None)
		self.book_next_str = kwargs.get('book_next_str', None)
		self.book_end_url = kwargs.get('book_end_url', None)
	
	def fetch_chapter_hrefs(self):
		chapter_url = self.chapter_url
		res = []
		page_idx = 0
		while chapter_url:
			cur_res, html_body = self.do_fetch_chapter_hrefs(chapter_url)
			res.extend(cur_res)
			page_idx += 1
			print 'fetch_chapter_hrefs, page: %d, chapter_num: %d, next_page_url: %s' % (page_idx, len(cur_res), chapter_url)
			chapter_url = None
			if self.book_next_url_pattern:
				if self.book_next_str and self.book_next_str not in html_body:
					break
				next_url_re = re.search(self.book_next_url_pattern, html_body, re.S)
				if next_url_re:
					next_url = next_url_re.groups()[0]
					# 还有下一页
					if next_url != self.book_end_url:
						chapter_url = self.base_host + next_url
		
		print('fetch_chapter_hrefs, total chapters: %s' % len(res))
		return res

class ScrabMultiBooks(object):

	def __init__(self, category_urls, book_params):
		self.init_scrabed_books()
		self.book_params = book_params
		try:
			for category, category_url in category_urls:
				self.begin_scrab_book_url(category, category_url)
		except:
			import sys
			sys.excepthook(*sys.exc_info())
		# 保存已经爬到的books避免下次重复爬
		self.save_scrabed_books()
	
	def init_scrabed_books(self):
		# 已经爬取了的books, 避免重复爬
		self.scrabed_books = set([])
		try:
			with open('scrabed_book_log.txt', 'r') as f:
				books = f.read()
				if books:
					self.scrabed_books = set(eval(books))
		except:
			import sys
			sys.excepthook(*sys.exc_info())
	
	def add_scrabed_books(self, book_url):
		self.scrabed_books.add(book_url)
		if len(self.scrabed_books) % 5 == 0:
			self.save_scrabed_books()

	def save_scrabed_books(self):
		with open('scrabed_book_log.txt', 'w') as f:
			f.write('%s' % list(self.scrabed_books))

	def begin_scrab_book_url(self, category, first_url):
		print 'begin_scrab_book_url:', category, first_url
		base_host = self.book_params['base_host']
		book_url_pattern = self.book_params['book_url_pattern']
		book_next_url_pattern = self.book_params.get('book_next_url_pattern', None)
		book_next_str = self.book_params.get('book_next_str', None)
		book_end_url = self.book_params.get('book_end_url', None)
		encode = self.book_params['encode']
		#is_relative_path = self.book_params['is_relative_path']
		decrypt_params = self.book_params.get('decrypt_params', None)
		category_url = first_url
		books = []

		page_idx = 1
		while category_url:
			resp = urllib.urlopen(category_url)
			html_body = str(resp.read())#.decode(encode)
			#print('html_body: %s' % html_body)
			bool_url_re = re.findall(book_url_pattern, html_body, re.S)
			for r in bool_url_re:
				href = r[0]
				title = r[1].decode(encode)
				if decrypt_params:
					iv = decrypt_params.get('iv', None)
					padding = decrypt_params.get('padding', None)
					title = ScrabBase.decrypt_content(title, decrypt_params['key'], iv, padding, encode)
					#print 'title: ', title
				books.append((href, title.replace('\r\n', '').replace('/', '_')))
			
			# 看下还有无下一页
			category_url = None
			if book_next_url_pattern:
				if book_next_str and book_next_str not in html_body:
					break
				next_url_re = re.search(book_next_url_pattern, html_body, re.S)
				if next_url_re:
					next_url = next_url_re.groups()[0]
					if next_url != book_end_url:
						category_url = base_host + next_url
						print 'page: %d, next_url: %s' % (page_idx, category_url)
						page_idx += 1
				
		print 'begin_scrab_book_url, total books: ', len(books)
		# 逐一爬取当前页面的book
		idx = 0
		for book_url, book_name in books:
			try:
				idx += 1
				progress = '%d/%d' % (idx, len(books))
				self.begin_scrab_book(category, book_url, book_name, progress)
			except:
				import sys
				sys.excepthook(*sys.exc_info())

	def begin_scrab_book(self, category, book_url, book_name, progress):
		if book_url in self.scrabed_books:
			print 'has scrabed book: %s, book_name: %s' % (book_url, book_name)
			return
		print 'begin_scrab_book', progress, category, book_url, book_name
		base_host = self.book_params['base_host']
		encode = self.book_params['encode']
		is_relative_path = self.book_params['is_relative_path']
		decrypt_params = self.book_params.get('decrypt_params', None)
		chapter_pattern = self.book_params['chapter_pattern']
		content_pattern = self.book_params['content_pattern']
		book_dir = self.book_params.get('book_dir', '') + category.decode(encode)
		if not os.path.exists(book_dir):
			os.mkdir(book_dir)
		book_filename = '%s/%s.txt' % (book_dir, book_name)
		book_next_url_pattern = self.book_params.get('book_next_url_pattern', None)
		book_next_str = self.book_params.get('book_next_str', None)
		book_end_url = self.book_params.get('book_end_url', None)
		scrab_mgr = ScrabBook(book_filename, base_host, book_url, chapter_pattern, content_pattern, 
			encode=encode, is_relative_path=is_relative_path, decrypt_params=decrypt_params,
			book_next_url_pattern=book_next_url_pattern, book_next_str=book_next_str, book_end_url=book_end_url)
		scrab_mgr.run()
		self.add_scrabed_books(book_url)


