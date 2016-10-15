#!/usr/bin/env python3

import json
import os.path

import sqlite3

from book import Book
from status import Status

data_dir = 'data'

books_cn = []
books_en = []


def load_book(books, file):
    if os.path.isfile(file):
        with open(file) as json_data:
            d = json.load(json_data)
            for b in d['books']:
                book = Book(b)
                books.append(book)


if not os.path.exists(data_dir):
    os.mkdir(data_dir)


# read data to list

for i in range(1, 401):
    f_cn = 'page/kindle_free_books_cn_' + str(i) + '.json'
    f_en = 'page/kindle_free_books_en_' + str(i) + '.json'
    load_book(books_cn, f_cn)
    load_book(books_en, f_en)

# save to database

status = Status()

status.new_count = len(books_cn) + len(books_en) - status.count

status.count = len(books_cn) + len(books_en)
status.bump()

conn = sqlite3.connect('data/books_' + str(status.version) + '.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS book_cn
    ( id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT UNIQUE, name TEXT, count INTEGER, type INTEGER, source INTEGER,
    time INTEGER );''')

cur.executemany('insert into book_cn (number, name, count, type, source, time) values (?, ?, ?, ?, ?, ?)', books_cn)

cur.execute('''CREATE TABLE IF NOT EXISTS book_en
    ( id INTEGER PRIMARY KEY AUTOINCREMENT, number TEXT UNIQUE, name TEXT, count INTEGER, type INTEGER, source INTEGER,
    time INTEGER );''')

cur.executemany('insert into book_en (number, name, count, type, source, time) values (?, ?, ?, ?, ?, ?)', books_en)

cur.execute('''CREATE TABLE IF NOT EXISTS status
    ( id INTEGER PRIMARY KEY AUTOINCREMENT, version INTEGER, count INTEGER, new_count INTEGER, time INTEGER );''')

cur.execute('insert into status (version, count, new_count, time) values (?, ?, ?, ?)', status.to_list())

conn.commit()
cur.close()
conn.close()

