import requests
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, url):
        self.url = url

    def fetch_page(self):
        response = requests.get(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            raise Exception(f'Error fetching page: {response.status_code}')
        return BeautifulSoup(response.text, 'html.parser')

if __name__ == '__main__':
    print('Scraper module ready')
