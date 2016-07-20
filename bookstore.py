# book store

# to do:
#     add sql get_column_names  (done)
#     pip virtualenv, minimal conda   (done)
#     import JSON file    (done)
#     add html response, views
#     more tests ?
#     what else ?  don't make too complicated, it will change

from flask import Flask, jsonify, request, abort, session, g
from psycopg2 import connect as pg_connect
from json import dumps as json_dumps
from contextlib import closing
import re
import requests
# import urllib.parse as urllib_parse
# import pdb

from process_books import parse_books

DBNAME = 'bookstore'
DBUSER = 'postgres'
DBHOST = 'localhost'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    "connect to database"
    try:
        dbname = app.config['DBNAME']
        dbuser = app.config['DBUSER']
        dbhost = app.config['DBHOST']
        return pg_connect("dbname=%s user=%s host=%s" % (dbname, dbuser, dbhost))
    except:
        print("cannot connect to db", dbname)
        raise

def init_db():
    "initialize and/or reset database for posgresql"
    with closing(connect_db()) as db:
        with app.open_resource('schema_pg.sql', mode='r') as f:
            db.cursor().execute(f.read())
        db.commit()

def get_column_names():
#   sql_cmd = "select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='books';"
#   cur = g.db.cursor()
#   cur.execute(sql_cmd)
#   if cur:
#       cols = [row[0] for row in cur.fetchall()]
#       print('sql cols ', cols)
#   else:
    cols = ['id', 'title', 'author', 'isbn', 'price']
    return cols

@app.before_request
def before_request():
    g.db = connect_db()

def insert_book(book, db):
    cur = db.cursor()
    cur.execute('insert into books (title, author, isbn, \
                  price) values (%s, %s, %s, %s);', 
                 (book['title'], book['author'], book['isbn'], 
                  book['price']))

@app.route('/books/import', methods=['POST'])
def import_books():
    content_type = request.headers.get('Content-Type')
#   print('import books, Content-Type: %s' % content_type)
#   print('import books, headers %s' % request.headers.to_list())
    if len(request.form) > 0:
        data = [item for item in request.form]
        data = ''.join(data)
    else:     #  plain/text, application/json, etc
        data = request.data
        data = data.decode('utf-8')
#   print('import data, present %s, length %d' % (len(data)>0, len(data)))
    if len(data) > 0:
        books = parse_books(data, content_type)
        for book in books:
            insert_book(book, g.db)
        g.db.commit()   # commit all books to database

    return ''

@app.route('/')
@app.route('/books')
def show_books():
    """show all books, with optional parameter filtering
            e.g. /books/author=Roald%20Dahl&price=6.20"""
# need + or %20 for spaces in author (set encoding?)

    args = request.args
    column_names = get_column_names()

    sql_cmd = ["SELECT title, author FROM books"]
    if len(args) > 0:
        for j, arg in enumerate(args):
            if arg not in column_names:   # return empty list
                sql_cmd = []
                break
            else:
                if not " WHERE " in sql_cmd:
                    sql_cmd.append(" WHERE ")
                sql_cmd.append("%s='%s'" % (arg, args[arg]))
                if j+1 < len(args):
                    sql_cmd.append(" AND ")
    sql_cmd.append(";")
    sql_cmd = "".join(sql_cmd)
#   print('sql_cmd: ', sql_cmd)

    books = []
    if len(sql_cmd) > 1:
        cur = g.db.cursor()
        cur.execute(sql_cmd)
        if cur:
            books = [dict(title=row[0], author=row[1]) for row in cur.fetchall()]
#   return jsonify({'results': books})
    return json_dumps({'results': books}, indent=4)

@app.route('/book/<id>')
def show_book(id):
    "show book for a particular id"

    columns = get_column_names()
    sql_cmd = "SELECT * FROM books WHERE id = %s;" % id

    cur = g.db.cursor()
    cur.execute(sql_cmd)
    if cur:
        books = [dict(zip(columns, row)) for row in cur.fetchall()]
    else:
        books = []
    return jsonify({'results': books})

# e.g. http://isbndb.com/api/books.xml?access_key=12345678&index1=isbn&value1=0596002068
# http://www.isbndb.com/api/books.xml?access_key=Z&index1=title&value1=Charlie+and
# /api/books.xml?access_key=Z&results=details&index1=isbn&value1=0061031321

root_url = 'http://www.isbndb.com/'
isbn_key = '09NAY6M8'

@app.route('/isbn/book/<title>')
def get_isbn_book(title):
    "get isbn for a book with title"
    url = root_url + '/api/books.xml?access_key=%s&index1=title&value1=%s' % (isbn_key, title)
    print('url', url)
    r = requests.get(url)
    print('res', type(r), r)
    text = r.text
#   print('text', text)
    pat = re.compile('isbn="[0-9]+"')
    p1 = pat.search(r.text)
    if p1:
        p1 = p1.group()
    if p1:
        p1 = p1[6:-1]
    print('isbn pat search', p1)

    return ''

if __name__ == '__main__':
    app.run()

