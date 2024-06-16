import hashlib
import sqlite3
import tldextract
import tornado.ioloop
import tornado.web

def create_table():
    sql_statements = """CREATE TABLE IF NOT EXISTS shorted_urls (
                id INTEGER PRIMARY KEY, 
                shorted_url text NOT NULL UNIQUE, 
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

create_table()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("http://localhost:8000/urls?url= ")
class UrlShortener(tornado.web.RequestHandler):

    def get(self):
        self.base_url = self.request.protocol + "://" + self.request.host + "/"
        self.original_url = self.get_arguments("url")[0]

        hash_value = hashlib.md5(self.original_url.encode()).hexdigest()[-6:]
        short_url = self.base_url + hash_value
        parsed = tldextract.extract(self.original_url)
        domain = parsed.domain
        conn = sqlite3.connect('urls.db') 
        cursor = conn.cursor() 
        try:
            cursor.execute("insert into shorted_urls (shorted_url, original_url, domain) values (?, ?, ?)",
            (short_url, self.original_url, domain))
        except:
            pass
        conn.commit()
        self.write('<a href = '+short_url+'>'+short_url+'</a>')

class ShortedUrl(tornado.web.RequestHandler):
    def get(self,slug):
        uri = self.request.protocol + "://" + self.request.host + "/"+ slug
        conn = sqlite3.connect('urls.db') 
        cursor = conn.cursor() 
        cursor.execute("SELECT original_url FROM shorted_urls WHERE shorted_url = ?", (uri,)) 
        try:
            original = cursor.fetchone()[0]
        except:
            raise tornado.web.HTTPError(404)
        conn.commit() 
        conn.close() 
        self.redirect(original)
class Metrics(tornado.web.RequestHandler):
    def get(self):
        top_domain = {}
        conn = sqlite3.connect('urls.db') 
        cursor = conn.cursor() 
        cursor.execute("SELECT domain, COUNT(domain) as c FROM shorted_urls group by domain ORDER BY c DESC limit 3") 
        try:
            original = cursor.fetchall()
            for row in original:
                top_domain[row[0]] = row[1]
        except:
            raise tornado.web.HTTPError(404)
        self.write(top_domain)
def make_app():
    return tornado.web.Application([(r"/", MainHandler),(r"/urls",UrlShortener ),(r"/metrics",Metrics ),(r"/([^/]+)", ShortedUrl)])
 
if __name__ == "__main__":
    app = make_app()
    app.listen(8000)
    print('server is running on 8000')
    tornado.ioloop.IOLoop.current().start()