from bs4 import BeautifulSoup as bs
import requests
import re

KEYWORDS = ['разработчик', 'SQL', 'python']

# Сhoose 'en' or 'ru'
Language = 'ru'
url = 'https://habr.com/' + Language +'/all/'
HEADERS = {'accept': '*/*', 'user-agent': 'Mozilla/5.0 (X11; Linux i686; rv:98.0) Gecko/20100101 Firefox/98.0'}

def get_soup(url):
	res = requests.get(url, headers=HEADERS)
	return bs(res.text, 'html.parser')

def preview_search(soup, deep_search=False):
	previews = soup.find_all('div', class_='article-formatted-body')
	label = 'preview'
	quantity_a = len(previews)
	index_res = {}
	print('  <Идет поиск в preview статей>')
	for i, pr in enumerate(previews):
		preview_text = pr.text
		index_res = _check_words(i, index_res, preview_text, label)
	return index_res, quantity_a


def deep_search(soup, index_res, quantity_a):
	label = 'deep'
	unfound_res = list(range(quantity_a) - index_res.keys())
	titles_links = soup.find_all('a', class_='tm-article-snippet__title-link')
	print('  <Идет поиск внутри статей>')
	for i in unfound_res:
		url_in = f'https://habr.com{titles_links[i].get("href")}'
		soup_in = get_soup(url_in)
		deep_text = soup_in.find('div', class_='article-formatted-body').text
		index_res = _check_words(i, index_res, deep_text, label)
	return index_res


def get_articles(soup, index_res):
	dates = soup.find_all({'time': 'title'})
	titles_links = soup.find_all('a', {'class': 'tm-article-snippet__title-link'})
	articles = []
	print('Результаты поиска:')
	for i, words in index_res.items():
		date_a = dates[i].get('title')
		title_a = titles_links[i].text
		link_a = f'https://habr.com{titles_links[i].get("href")}'
		articles.append((date_a, title_a, link_a))
		print(f'_______________статья №{i+1}:_______________')
		print(date_a, title_a, link_a,
			  f"Поиск: '{list(words.keys())[0]}'. Ключевые слова: {list(words.values())[0]}", sep='\n')
	return articles


def _check_words(i, index_res, text, label):
	words_in_text = set([_.lower() for _ in re.findall(f'{"|".join(KEYWORDS)}', text, re.I)])
	if words_in_text:
		index_res[i] = {label: words_in_text}
	return index_res

if __name__ == '__main__':
	soup = get_soup(url)
	print(f'Поиск по ключевым словам {KEYWORDS}')
	result = preview_search(soup)
	index_res, quantity_a = result
	if len(index_res) == quantity_a:
		articles = get_articles(soup, index_res)
	else:
		index_res = deep_search(soup, index_res, quantity_a)
		if index_res:
			articles = get_articles(soup, index_res)
		else:
			print('<Ничего не найдено>')
