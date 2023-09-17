#! D:\python27\python.exe
# -*- coding:utf-8 -*-
import re
import urllib
import urllib2
import codecs
import threading
import base64
import hashlib
import HTMLParser
import htmlentitydefs
from Crypto.Cipher import AES

cached_txt = {}

# 解析html特殊字符
class CustomHTMLParser(HTMLParser.HTMLParser):
	def __init__(self, encode):
		HTMLParser.HTMLParser.__init__(self)
		self.encode = encode
		self.result = []

	def handle_entityref(self, name):
		val = unichr(htmlentitydefs.name2codepoint[name])
		#print 'handle_entityref', name, val
		try:
			val = val.decode(self.encode)
		except:
			pass
		self.result.append(val)

	def handle_charref(self, name):
		val = unichr(int(name))
		#print 'handle_charref', name, val
		try:
			val = val.decode(self.encode)
		except:
			pass
		self.result.append(val)

	def handle_data(self, data):
		code_pat = re.findall('(#(\d+);)' , data)
		for src_str, code in code_pat:
			# print 'handle_data', src_str, code
			# 处理&#2093;这种内码字符
			dest_val = unichr(int(code))
			try:
				dest_val = dest_val.encode(self.encode)
			except:
				pass
			data = data.replace(src_str, dest_val)

		try:
			data = data.decode(self.encode)
		except:
			pass

		self.result.append(data)

def parse_html(html_text, encode):
	parser = CustomHTMLParser(encode)
	html_text = html_text.replace('</p>', '\r\n').replace('<p>', '')
	parser.feed(html_text)
	new_txt = ''
	for r in parser.result:
		new_txt += r.replace('&', '')
	#new_txt = new_txt.replace('</p>', '\r\n').replace('<p>', '')
	return new_txt

def decrypt_content(content, key, iv, padding, encode):
	try:
		if not iv:
			# 默认取md5(key)的前16位
			hash_obj = hashlib.md5()
			hash_obj.update(key.encode())
			md5_key = hash_obj.hexdigest()
			iv = md5_key[:16]
		try:
			content = base64.b64decode(content)
		except:
			print 'content is not base64 encode', content
		decrypted_content = AES.new(key, AES.MODE_CBC, iv).decrypt(content)
		if padding == "zero":
			decrypted_content = ''.join([chr(i) for i in decrypted_content if i != 0 ])
		elif padding == "pkcs7":
			decrypted_content = ''.join([i for i in decrypted_content if ord(i) > 32])
		#print 'decrypt_content!!', decrypted_content
		return parse_html(decrypted_content, encode)
	except:
		import sys
		sys.excepthook(*sys.exc_info())
		print 'decrypt_content failed, content=%s' % content
		return content

class ScrabChapterThread(threading.Thread):
	def __init__(self, seq, url, title, encode, content_pattern, chapter_title_pattern, replace_map, decrypt_params=None):
		super(ScrabChapterThread, self).__init__()
		self.seq = seq
		self.url = url
		self.title = title
		self.encode = encode
		self.pattern = content_pattern
		self.chapter_title_pattern = chapter_title_pattern
		self.replace_map = replace_map
		self.decrypt_params = decrypt_params # 解密参数

	def run(self):
		global cached_txt
		retry = 3
		for i in xrange(retry):
			try:
				header = {}
				header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
				urllib2.Request(self.url, headers=header)
				resp = urllib2.urlopen(self.url)
				chapter_body = str(resp.read())
				txt_re = re.search(self.pattern, chapter_body, re.S)
				if txt_re:
					txt = txt_re.group(1)
					if self.decrypt_params:
						iv = self.decrypt_params.get('iv', None)
						padding = self.decrypt_params.get('padding', None)
						txt = decrypt_content(txt, self.decrypt_params['key'], iv, padding, self.encode)

					if self.chapter_title_pattern:
						chapter_title_ret = re.search(self.chapter_title_pattern, txt, re.S)
						if chapter_title_ret:
							cached_txt[self.seq] = '\r\n' + chapter_title_ret.group() + '\r\n\r\n'
							print('chapter_title: ', chapter_title_ret.group())
						else:
							if self.title:
								cached_txt[self.seq] = '\r\n' + self.title + '\r\n\r\n'
							else:
								cached_txt[self.seq] = ''
					else:
						if self.title:
							cached_txt[self.seq] = '\r\n' + self.title + '\r\n\r\n'
						else:
							cached_txt[self.seq] = ''
					cached_txt[self.seq] += txt
				else:
					if i < retry:
						continue
					cached_txt[self.seq] = ''
				break
			except:
				import sys
				sys.excepthook(*sys.exc_info())
				print('bad url: %s' % self.url)

class ScrabBase(object):
	def __init__(self, book_name, base_host, chapter_path, chapter_pattern, content_pattern, **kwargs):
		self.seq = 0
		self.last_start_seq = 0
		self.threads = []
		self.book_name = book_name
		self.base_host = base_host
		self.chapter_url = base_host + chapter_path
		self.chapter_pattern = chapter_pattern
		self.content_pattern = content_pattern
		self.encode = kwargs.get('encode', 'utf-8')
		self.is_relative_path = kwargs.get('is_relative_path', False)
		self.write_batch = kwargs.get('write_batch', 10)
		self.chapter_title_pattern = kwargs.get('chapter_title_pattern', None)
		if kwargs.get('content_encode', None) is None:
			self.content_encode = self.encode
		else:
			self.content_encode = kwargs.get('content_encode', None)
		self.replace_map = kwargs.get('replace_map', None)
		self.decrypt_params = kwargs.get('decrypt_params', None)

	def write_to_file(self):
		global cached_txt
		# 等待当前批次都取完
		for thread in self.threads:
			thread.join()
		
		with codecs.open(self.book_name, 'a+', encoding=self.content_encode) as f:
			while self.last_start_seq < self.seq:
				#print cached_txt.get(self.last_start_seq, '')
				try:
					content = cached_txt.get(self.last_start_seq, '')
					content = content.replace('</p>', '\r\n').replace('<p>', '')
					f.write(content)
					f.write('\r\n')
				except:
					import sys
					sys.excepthook(*sys.exc_info())
				self.last_start_seq += 1
		
		cached_txt.clear()
		self.threads = []

	# return: [(href, title), ...]
	def fetch_chapter_hrefs(self):
		res, _ = self.do_fetch_chapter_hrefs(self.chapter_url)
		#print('fetch_chapter_hrefs: %s' % res)
		return res

	def do_fetch_chapter_hrefs(self, chapter_url):
		resp = urllib.urlopen(chapter_url)
		html_body = str(resp.read())#.decode(self.encode)
		chapter_re = re.findall(self.chapter_pattern, html_body, re.S)
		res = []
		for r in chapter_re:
			href = r[0]
			title = r[1].decode(self.encode)
			#print 'do_fetch_chapter_hrefs', href, title
			if self.decrypt_params:
				iv = self.decrypt_params.get('iv', None)
				padding = self.decrypt_params.get('padding', None)
				#href = decrypt_content(href, self.decrypt_params['key'], iv, padding, self.encode)
				title = decrypt_content(title, self.decrypt_params['key'], iv, padding, self.encode)

			if self.is_relative_path:
				href = self.base_host + href
			res.append((href, title.replace('\r\n', '')))
		
		return res, html_body

	# 子类实现
	def get_next_page_url(self, cur_page_url):
		return None

	def run(self):
		chapter_hrefs = self.fetch_chapter_hrefs()
		for h in chapter_hrefs:
			url = h[0]
			title = h[1]
			'''
			if next_page_url and self.decrypt_params:
				iv = self.decrypt_params.get('iv', None)
				padding = self.decrypt_params.get('padding', None)
				next_page_url = decrypt_content(next_page_url, self.decrypt_params['key'], iv, padding, self.encode)
			'''
			if self.seq % self.write_batch == 0:
				self.write_to_file()
			# start new thread
			#print('start fetch: %s' % url)
			scrab_thread = ScrabChapterThread(self.seq, url, title, self.content_encode, self.content_pattern, 
				self.chapter_title_pattern, self.replace_map, self.decrypt_params)
			scrab_thread.start()
			self.threads.append(scrab_thread)
			self.seq += 1
			next_page_url = self.get_next_page_url(url)
			if next_page_url is not None:
				print('start fetch next page: %s' % next_page_url)
				scrab_thread2 = ScrabChapterThread(self.seq, next_page_url, '', self.content_encode, 
					self.content_pattern, self.chapter_title_pattern, self.replace_map)
				scrab_thread2.start()
				self.threads.append(scrab_thread2)
				self.seq += 1

		self.write_to_file()

