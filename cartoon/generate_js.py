# -*- coding: utf-8 -*-
import os
import json
import codecs

base_dir = 'E:/LiuBei/cartoon/'
output_js = 'E:/LiuBei/cartoon/static/data.js'
categorys = ['toptoon']
cartoon_datas = {} # <cart_id, json_data>

for category in categorys:
	root_dir = '%s/%s' % (base_dir, category)
	for filename in os.listdir(root_dir):
		cur_dir = os.path.join(root_dir, filename)
		if os.path.isdir(cur_dir):
			cart_id = int(filename)
			file_info_path = os.path.join(cur_dir, 'file_info.json')
			data = { 'id': cart_id, 'category': category }
			if os.path.exists(os.path.join(cur_dir, 'cover.jpg')):
				data['has_cover'] = True
			cartoon_datas[cart_id] = data
			if os.path.exists(file_info_path):
				with open(file_info_path, 'r') as f:
					dct = json.loads(f.read(), encoding='utf-8')
					data['title'] = dct['title'].split('(')[0].split(u'\uff08')[0]#.replace(u'\u0274\u1d07\u1d21\u29eb', '')
					data['view'] = int(dct.get('view', 0))
					data['desc'] = dct.get('desc', '')

# 根据view排序
sort_cartoon_datas = []
sort_keys = cartoon_datas.keys()
sort_keys.sort(key=lambda cart_id: -cartoon_datas[cart_id].get('view', 0))
for cart_id in sort_keys:
	sort_cartoon_datas.append(cartoon_datas[cart_id])

# 写入js
#print sort_cartoon_datas, len(sort_cartoon_datas)

js_str = '''
window.fetch_cartoon_infos = function() { return {{}};}
'''

with codecs.open(output_js, 'w', encoding='utf-8') as f:
	dump_str = json.dumps(sort_cartoon_datas, encoding='utf-8')
	js_str = js_str.replace('{{}}', dump_str)
	f.write(js_str)
