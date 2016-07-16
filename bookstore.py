# book store

from flask import Flask, jsonify, request, abort, session, g
from psycopg2 import connect as pg_connect
from json import dumps as json_dumps
from contextlib import closing
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
#   select column_name from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='books';
    return ['id', 'title', 'author', 'isbn', 'price']  # hard code for now

@app.before_request
def before_request():
    g.db = connect_db()

def insert_book(book, db):   # rename insert_book(book, db)
    cur = db.cursor()
    cur.execute('insert into books (title, author, isbn, \
                  price) values (%s, %s, %s, %s);', 
                 (book['title'], book['author'], book['isbn'], 
                  book['price']))

@app.route('/books/import', methods=['POST'])
def import_books():
    if len(request.form) > 0:
        data = [item for item in request.form]
        data = ''.join(data)
    else:     #  plain/text
        data = request.data
        data = data.decode('utf-8')
#   print('data read:', len(data)>0)
    if len(data) > 0:
        books = parse_books(data)
        for book in books:
            insert_book(book, g.db)
        g.db.commit()   # commit all books to database

    return ''

@app.route('/books')
def show_books():
    """show all books, with optional parameter filtering
            e.g. /books/author=Dahl&price=8.00"""

    args = request.args
    column_names = get_column_names()

    sql_cmd = ["SELECT title, author FROM books"]
    if len(args) > 0:
        sql_cmd.append(" WHERE ")
        for j, arg in enumerate(args):
            if arg in column_names:
                sql_cmd.append("%s='%s'" % (arg, args[arg]))
                if j+1 < len(args):
                    sql_cmd.append(" AND ")
    sql_cmd.append(";")
    sql_cmd = "".join(sql_cmd)

    cur = g.db.cursor()
    cur.execute(sql_cmd)
    if cur:
        orders = [dict(title=row[0], author=row[1]) for row in cur.fetchall()]
    else:
        orders = []
    return jsonify({'results': orders})

@app.route('/book/<id>')
def show_book(id):
    "show book for a particular id"

    columns = get_column_names()
    sql_cmd = "SELECT * FROM books WHERE id = %s;" % id

    cur = g.db.cursor()
    cur.execute(sql_cmd)
    if cur:
        orders = [dict(zip(columns, row)) for row in cur.fetchall()]
    else:
        orders = []
    return jsonify({'results': orders})

if __name__ == '__main__':
    app.run()

