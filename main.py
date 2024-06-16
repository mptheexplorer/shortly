import hashlib
import sqlite3
from urllib.parse import urlparse

def create_table():
    sql_statements = """CREATE TABLE IF NOT EXISTS shorted_urls (
                id INTEGER PRIMARY KEY, 
                shorted_url text NOT NULL, 
                original_url text NOT NULL, 
                domain text NOT NULL
        );"""


    # create a database connection
    try:
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            cursor.execute(sql_statements)
            
            conn.commit()
    except sqlite3.Error as e:
        print(e)


class UrlShortener:
    def __init__(self):
        self.url_mapping = {}
        self.base_url = "http://localhost:8000/"

    def shorten_url(self, original_url):
        hash_value = hashlib.md5(original_url.encode()).hexdigest()[:6]
        short_url = self.base_url + hash_value
        self.url_mapping[short_url] = original_url
        parsed = urlparse(original_url)
        domain = parsed.netloc
        conn = sqlite3.connect('urls.db') 
        cursor = conn.cursor() 
        cursor.execute("insert into shorted_urls (shorted_url, original_url, domain) values (?, ?, ?)",
            (short_url, original_url, domain))
        conn.commit()
        return short_url

    def expand_url(self, short_url):
        original_url = self.url_mapping.get(short_url)
        return original_url

#Example


create_table()
url_shortener = UrlShortener()

original_url = input("enter url here: ")
short_url = url_shortener.shorten_url(original_url)

print(f"Original URL: {original_url}")
print(f"Short URL: {short_url}")

expanded_url = url_shortener.expand_url(short_url)
print(f"Expanded URL: {expanded_url}")