from bs4 import BeautifulSoup
import requests
from time import sleep
import json
import os

MAIN_URL = "https://www.anime-planet.com"
LIST_URL = 'https://www.anime-planet.com/characters/top-loved?page={}'
DUMP_CHECKOUT_STEP = 100
DATASET_PATH = './dataset'

def parse_char_page(url):
	res = requests.get(url)
	# print(res.status_code) # 200
	if res.status_code != 200:
		return False, None
	
	# print(res.encoding) # UTF-8
	html = res.text
	soup = BeautifulSoup(html, 'html.parser')

	# tags infomation
	tags = soup.find_all('a', {"data-tooltip": "tags"})
	ret_tags = []
	for each_a in tags:
		# print(each_a.text)
		ret_tags.append(each_a.text)

	# image infomation
	image = soup.find_all('img', {'itemprop':"image"})[0]
	# print(image['src'])
	final_image_url = MAIN_URL + image['src']
	if final_image_url == "https://www.anime-planet.com/images/characters/blank_char.gif":
		final_image_url = None
	# print(final_image_url)

	# description infomation
	desc = soup.find('div', {'itemprop': 'description'})
	if desc is not None:
		desc = desc.text
	else:
		desc = None

	# meta infomation
	meta = soup.find_all('div', {'class': "pure-1 md-1-5"})
	gender = meta[0].text.split(':')[1].strip()
	hair_color = meta[1].text.split(':')[1].strip()
	rank = meta[2].text.split('#')[1].strip()
	# print(gender, hair_color, rank)

	# character name
	name = soup.find('h1', {'itemprop': 'name'})
	name = name.text
	
	# return dict structure
	ret_dict = {'tags': ret_tags, 'image_url': final_image_url, 'description': desc, 
				'gender': gender, 'hair_color':hair_color, 'love_rank':rank, 'name':name}
	
	return True, ret_dict

def parse_list_page(main_url, page_num):
	print(main_url.format(page_num))
	res = requests.get(main_url.format(page_num))
	# print(res.status_code) # 200
	if res.status_code != 200:
		return False, None
	
	# print(res.encoding) # UTF-8
	html = res.text
	soup = BeautifulSoup(html, 'html.parser')

	hrefs = soup.find_all('a', {'class': 'name'})
	ret_hrefs = []
	for each_href in hrefs:
		ret_hrefs.append(each_href['href'])
	
	return True, {'hrefs': ret_hrefs}

def dump_items(items, last_index):
	file_name = "{}_{}.json".format(last_index-(DUMP_CHECKOUT_STEP-1), last_index)
	with open(os.path.join(DATASET_PATH, file_name), 'w+') as fp:
		json.dump(items, fp)

	print(" [INFO] SAVE DONE : {}".format(os.path.join(DATASET_PATH, file_name)))

if __name__ == "__main__":
	items = []
	char_id = 2200
	for page_id in range(152, 10021):
		_status, list_item = parse_list_page(LIST_URL, page_id)
		
		for each_href in list_item['hrefs']:
			try:
				_status, char_item = parse_char_page(MAIN_URL+each_href)
				if _status:
					char_id += 1
					print("="*50)
					print(char_item)
					print("="*50)
					items.append(char_item)
					if char_id % DUMP_CHECKOUT_STEP == 0:
						dump_items(items, char_id)
						items = []
					sleep(2)
				else:
					print(" [ERROR] Fail in {}".format(MAIN_URL+each_href))
			except:
				print(" [CRITICAL] Exception Occured in {}".format(MAIN_URL+each_href))





