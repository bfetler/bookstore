# data tests

import unittest
import tempfile
import os
import json

import bookstore

from process_books import parse_books

class TestData(unittest.TestCase):

    def setUp(self):
        self.header = 'title,author,isbn,price\n'
        bookstore.app.config['TESTING'] = True
        bookstore.app.config['DBNAME'] = 'books_test'
        self.app = bookstore.app.test_client()
        with bookstore.app.app_context():
            bookstore.init_db()
        self.data_fp, self.data_path = tempfile.mkstemp()

    def tearDown(self):
        os.unlink(self.data_path)
        with bookstore.app.app_context():
            bookstore.init_db()

    def add_two_books(self):
        "data setup, not used in all tests"
        line1 = 'Horton Hears a Who,Dr. Seuss,jgh-0944,5.98\n'
        line2 = 'Room on the Broom,Julia Donaldson,bwg-7702,8.23\n'
        lines = '%s%s%s' % (self.header, line1, line2)
        books = parse_books(lines)
        db = bookstore.connect_db()
        for book in books:
            bookstore.insert_book(book, db)
        db.commit() 

    def test_no_books(self):
        rv = self.app.get('/books')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        self.assertIn('results', str(rv.data))
        self.assertEqual(rdata['results'], [])

    def test_no_book_number(self):
        rv = self.app.get('/book/203')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        self.assertIn('results', str(rv.data))
        self.assertEqual(rdata['results'], [])

    def test_post_two_books(self):
        line1 = 'Horton Hears a Who,Dr. Seuss,jgh-0944,5.98\n'
        line2 = 'Room on the Broom,Julia Donaldson,bwg-7702,8.23\n'
        lines = '%s%s%s' % (self.header, line1, line2)
        with open(self.data_path, 'w') as fp:
            fp.write(lines)
            rv = self.app.post('/books/import', data=self.data_path, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.headers['content-type'], 'text/html; charset=utf-8')

    def test_two_books_found(self):
        self.add_two_books()
        rv = self.app.get('/books', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        self.assertEqual(rdata['results'][0]['title'], 'Horton Hears a Who')
        self.assertEqual(rdata['results'][0]['author'], 'Dr. Seuss')
        self.assertEqual(rdata['results'][1]['title'], 'Room on the Broom')
        self.assertEqual(rdata['results'][1]['author'], 'Julia Donaldson')

    def test_price_book_found(self):
        self.add_two_books()
        rv = self.app.get('/books?price=5.98', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        self.assertEqual(rdata['results'][0]['title'], 'Horton Hears a Who')
        self.assertEqual(rdata['results'][0]['author'], 'Dr. Seuss')

    def test_author_price_book_found(self):
        self.add_two_books()
        rv = self.app.get('/books?author=Julia%20Donaldson&price=8.23', follow_redirects=True)
#       rv = self.app.get('/books?author=Julia Donaldson&price=8.23', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        self.assertEqual(rdata['results'][0]['title'], 'Room on the Broom')
        self.assertEqual(rdata['results'][0]['author'], 'Julia Donaldson')

    def test_get_book_one(self):
        self.add_two_books()
        rv = self.app.get('/book/1', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        res0 = rdata['results'][0]
        self.assertEqual(res0['title'], 'Horton Hears a Who')
        self.assertEqual(res0['author'], 'Dr. Seuss')
        self.assertEqual(res0['price'], 5.98)
        self.assertEqual(res0['isbn'], 'jgh-0944')

    def test_get_book_two(self):
        self.add_two_books()
        rv = self.app.get('/book/2', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        res1 = rdata['results'][0]
        self.assertEqual(res1['title'], 'Room on the Broom')
        self.assertEqual(res1['author'], 'Julia Donaldson')
        self.assertEqual(res1['price'], 8.23)
        self.assertEqual(res1['isbn'], 'bwg-7702')

if __name__ == '__main__':
    unittest.main()

