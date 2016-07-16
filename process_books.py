# methods for processing books

def parse_books(lines):
    "parse multi-line orders, separated by CR"
    return parse_books_by_line(lines)

# other alternatives: use pandas?

def make_book(header, values):
    "make book from header and values"
    book = {}
    for key, val in zip(header, values):
        if key == 'price':
            price = float(price)
        book[key] = val
    return book

def parse_books_by_line(text_lines):
    "parse books one line at a time"
    books = []
    lines = text_lines.split('\n')
    if len(lines) > 1:
        lines.append('\n')    # pad end with CR if missing from file
        header = lines[0].split('|')
        for line in lines[1:]:
            values = line.split('|')
            if len(values) > 1:
                book = make_book(header, values)
                books.append(book)
    return books

