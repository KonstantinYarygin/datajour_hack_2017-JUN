from bs4 import BeautifulSoup
import requests


def url2text(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    text = ' '.join([x.text for x in soup.findAll('p')])
    return text

if __name__ == '__main__':
    # url = 'https://meduza.io/feature/2017/05/23/vlasti-delayut-vse-chtoby-lyuboy-chelovek-byl-na-kryuchke'
    url = 'https://www.kommersant.ru/doc/3329680'
    text = url2text(url)
    print(text)
