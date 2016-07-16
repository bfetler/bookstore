# data tests

import unittest
import tempfile
import os
import json

import bookstore

from process_books import parse_books

class TestData(unittest.TestCase):

    def setUp(self):
        self.header = 'title|author|isbn|price\n'
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
        line1 = 'Horton Hears a Who|Dr. Seuss|jgh-0944|5.98\n'
        line2 = 'Room on the Broom|Julia Donaldson|bwg-7702|8.23\n'
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
        line1 = 'Horton Hears a Who|Dr. Seuss|jgh-0944|5.98\n'
        line2 = 'Room on the Broom|Julia Donaldson|bwg-7702|8.23\n'
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

    def xx_test_valid_book_found(self):
        self.add_two_books()
        rv = self.app.get('/books?valid=1', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        self.assertEqual(rdata['results'][0]['name'], 'Klaus Werkzeug')
        self.assertEqual(rdata['results'][0]['order_id'], 3573)
        self.assertTrue(rdata['results'][0]['valid'])

    def xx_test_valid_state_book_found(self):
        self.add_two_orders()
        rv = self.app.get('/orders?valid=1&state=CA', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        self.assertEqual(rdata['results'][0]['name'], 'Klaus Werkzeug')
        self.assertEqual(rdata['results'][0]['order_id'], 3573)
        self.assertTrue(rdata['results'][0]['valid'])

    def xx_test_get_book_one(self):
        self.add_two_books()
        rv = self.app.get('/book/3572', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        res0 = rdata['results'][0]
        self.assertEqual(res0['name'], 'Davis Walters')
        self.assertEqual(res0['order_id'], 3572)
        self.assertFalse(res0['valid'])
        self.assertEqual(res0['email'], 'euismod@sit.edu')
        self.assertEqual(res0['state'], 'TX')
        self.assertEqual(res0['birthday'], 'Mar 21, 1941')
        self.assertEqual(res0['zipcode'], '17899')
        self.assertEqual(res0['errors'][0]['rule'], 'ZipCodeSum')
        self.assertEqual(res0['errors'][0]['message'], 'zip code sum is too large')

    def xx_test_get_book_two(self):
        self.add_two_books()
        rv = self.app.get('/book/3573', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.headers['content-type'], 'application/json')
        rdata = json.loads(rv.data.decode('utf-8'))
        self.assertIn('results', str(rv.data))
        res1 = rdata['results'][0]
        self.assertEqual(res1['name'], 'Klaus Werkzeug')
        self.assertEqual(res1['order_id'], 3573)
        self.assertTrue(res1['valid'])
        self.assertEqual(res1['email'], 'klaus@werkzeug.com')
        self.assertEqual(res1['state'], 'CA')
        self.assertEqual(res1['birthday'], 'Mar 22, 1941')
        self.assertEqual(res1['zipcode'], '94122')
        self.assertEqual(res1['errors'], [])

if __name__ == '__main__':
    unittest.main()

