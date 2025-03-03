import requests
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET


'''
 20 статей на одной странице сайта cyberleninka.ru
 есть несколько разделов, возьму 
 1.Фундаментальная медицина
 2.Компьютерные и информационные науки
 3.Экономика и бизнес
 4.История и археология
 5.Математика
 При условии что будет по 1000 статей в каждой категории
 В ином случае буду добирать из других категорий 
'''

# разделы
SECTIONS = {
    "basic-medicine": "https://cyberleninka.ru/article/c/basic-medicine/",
    "computer-science": "https://cyberleninka.ru/article/c/computer-and-information-sciences/",
    "economics-and-business": "https://cyberleninka.ru/article/c/economics-and-business/",
    "history-and-archaeology": "https://cyberleninka.ru/article/c/history-and-archaeology/",
    "mathematics": "https://cyberleninka.ru/article/c/mathematics/",
}


MAX_PAGES = 50

def get_article_data(article):
    title_element = article.find("div", class_="title")
    if not title_element:
        return None  # скип если нет заголовка

    title = title_element.text.strip()
    link = "https://cyberleninka.ru" + article.find("a")["href"]
    
    year_element = article.find("span")
    year = year_element.text.strip().split("/")[0] if year_element else "Неизвестно"

    authors = year_element.text.strip().split("/")[1] if year_element else "Неизвестно"

    labels = [label.text.strip() for label in article.find_all("div", class_="label")]  # Scopus, ВАК и т. д.

    return {
        "title": title,
        "link": link,
        "year": year,
        "authors": authors,
        "labels": ", ".join(labels)
    }

def parse_articles(section_name, base_url, max_pages=1):
    articles_data = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    for page in range(1, max_pages + 1):
        url = f"{base_url}{page}"
        print(f" Собираем статьи из раздела {section_name}, страница {page}...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Ошибка {response.status_code} на странице {page}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("li")  # статьи находятся внутри <li>

        for article in articles:
            article_data = get_article_data(article)
            if article_data:
                article_data["section"] = section_name  # категория статьи (раздел)
                articles_data.append(article_data)

        time.sleep(1.5)  

    return articles_data

def save_to_xml(data, filename="articles.xml"):
    root = ET.Element("articles")

    for article in data:
        article_element = ET.SubElement(root, "article")

        for key, value in article.items():
            element = ET.SubElement(article_element, key)
            element.text = value

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

all_articles = []
for section, url in SECTIONS.items():
    articles = parse_articles(section, url, MAX_PAGES)
    all_articles.extend(articles)

save_to_xml(all_articles, "articles.xml")

print(f"Сохранено {len(all_articles)} статей в articles.xml")
