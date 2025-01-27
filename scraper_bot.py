import requests
from bs4 import BeautifulSoup
import time
import re
import threading
from abc import ABC, abstractmethod

class SiteScraperBase(ABC):
    def __init__(self, domain, base_url):
        self.domain = domain
        self.base_url = base_url
        self.telefones = []
        self.links = []

    @abstractmethod
    def extract_links(self, soup):
        """Extrai links dos anúncios da página"""
        pass

    @abstractmethod
    def extract_description(self, soup):
        """Extrai descrição do anúncio"""
        pass

    def get_phone_numbers(self):
        try:
            response = requests.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            self.links.extend(self.extract_links(soup))
        except Exception as e:
            print(f"Error: {e}")

    def discover_phones(self):
        while True:
            try:
                link = self.links.pop(0)
            except IndexError:
                return None

            try:
                ad_url = f"{self.domain}{link}"
                ad_response = requests.get(ad_url)
                ad_soup = BeautifulSoup(ad_response.content, 'html.parser')
                
                description = self.extract_description(ad_soup)
                if not description:
                    continue

                phones = re.findall(r"\(?0?([1-9]{2})[ \-\.\)]{0,2}(9[ \-\.]?\d{4})[ \-\.]?(\d{4})", description)
                if phones:
                    for phone in phones:
                        phone_str = f"{phone[0]}{phone[1]}{phone[2]}"
                        print(f"Found phone: {phone_str}")
                        self.telefones.append(phone)
                        self.save_phone(phone)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing ad: {e}")

    def save_phone(self, phone):
        string_telefone = "{}{}{}\n".format(phone[0], phone[1], phone[2])
        try:
            with open("telefones.csv", "a") as arquivo:
                arquivo.write(string_telefone)
        except Exception as e:
            print(f"Error saving phone: {e}")

    def run(self, num_threads=10):
        self.get_phone_numbers()
        
        threads = []
        for i in range(num_threads):
            t = threading.Thread(target=self.discover_phones)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

# Exemplo de implementação para o site original
class DjangoAnunciosScraper(SiteScraperBase):
    def extract_links(self, soup):
        links = []
        cards_pai = soup.find("div", class_="ui three doubling link cards")
        if cards_pai:
            cards = cards_pai.find_all("a")
            for card in cards:
                try:
                    links.append(card['href'])
                except:
                    pass
        return links

    def extract_description(self, soup):
        try:
            return soup.find_all("div", class_="sixteen wide column")[2].p.get_text().strip()
        except:
            return None

def main():
    # Exemplo de uso
    scraper = DjangoAnunciosScraper(
        domain="https://django-anuncios.solyd.com.br",
        base_url="https://django-anuncios.solyd.com.br/automoveis/"
    )
    scraper.run()

if __name__ == "__main__":
    main()
