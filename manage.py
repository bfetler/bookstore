# setup

import sys
from bookstore import init_db

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'initdb':
            init_db()   # initialize database

if __name__ == '__main__':
    main()

