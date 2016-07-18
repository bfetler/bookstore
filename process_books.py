# methods for processing books

from json import loads as json_loads

def parse_books(lines, content_type='plain/text'):
    "parse multi-line books"
    if content_type == 'application/json':
        return parse_books_by_json(lines)
    else:
        return parse_books_by_csv(lines)

# other alternatives for csv: pandas?

def parse_books_by_json(lines):
    data = json_loads(lines)
    data = data['data']
#   books data already in dict format
    return data

def make_book(header, values):
    "make book from header and values"
    book = {}
    for key, val in zip(header, values):
        if key == 'price':
            val = float(val)
        book[key] = val
    return book

def parse_books_by_csv(text_lines, sep=','):
    "parse multi-line orders, separated by CR, one line at a time"
    books = []
    lines = text_lines.split('\n')
    if len(lines) > 1:
        lines.append('\n')    # pad end with CR if missing from file
        header = lines[0].split(sep)
        for line in lines[1:]:
            values = line.split(sep)
            if len(values) > 1:
                book = make_book(header, values)
                books.append(book)
    return books

