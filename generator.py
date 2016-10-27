#!/usr/bin/env python3

import json
import os.path

import sqlite3
import zipfile

from book import Book
from status import Status

data_dir = 'data'

books_cn = []
books_en = []
ids = set()

nodes = dict()
node_map = []
node_relation = dict()

reviews = []


def load_book(file):
    if os.path.isfile(file):
        with open(file) as json_data:
            d = json.load(json_data)
            for b in d['books']:
                book = Book(b)
                if book.item_id in ids:
                    print('added: ' + book.item_id)
                    continue
                if book.languages and len(book.languages) > 0:
                    if book.languages[0] == 'chinese' or book.languages[0] == 'traditional_chinese':
                        books_cn.append(book.tuple())
                    else:
                        books_en.append(book.tuple())
                    ids.add(book.item_id)
                    reviews.append((book.item_id, book.editorial_review))

                    if book.nodes:
                        for node in book.nodes:
                            node.node_id = node.id
                            node_map.append((book.item_id, node.node_id))
                            while True:
                                if node.node_id not in nodes:
                                    nodes[node.node_id] = node.tuple()
                                if not node.is_root:
                                    node_key = str(node.node_id) + '-' + str(node.node.node_id)
                                    if node_key not in node_relation:
                                        node_relation[node_key] = (node.node_id, node.node.node_id)
                                    node = node.node
                                else:
                                    break
                else:
                    print('no language')
                    print(book.json())


def compress(file_name):
    zip_file = file_name + ".zip"
    zf = zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED)
    zf.write(file_name, arcname=os.path.basename(file_name))
    zf.close()
    return zip_file


if not os.path.exists(data_dir):
    os.mkdir(data_dir)


# read data to list

for i in range(1, 401):
    f_cn = 'page/kindle_free_books_cn_' + str(i) + '.json'
    f_en = 'page/kindle_free_books_en_' + str(i) + '.json'
    load_book(f_cn)
    load_book(f_en)

# save to database

status = Status()

status.new_count = len(books_cn) + len(books_en) - status.count

status.count = len(books_cn) + len(books_en)
status.bump()

conn = sqlite3.connect('data/books_' + str(status.version) + '.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    score REAL,
    url TEXT,
    item_id TEXT,
    pages TEXT,
    publisher TEXT,
    brand TEXT,
    asin TEXT,
    edition TEXT,
    isbn TEXT,
    large_image_url TEXT,
    medium_image_url TEXT,
    small_image_url TEXT,
    region TEXT,
    release_date TEXT,
    publication_date TEXT,
    languages TEXT
    );''')

cur.executemany('''insert into book (
    title,
    author,
    score,
    url,
    item_id,
    pages,
    publisher,
    brand,
    asin,
    edition,
    isbn,
    large_image_url,
    medium_image_url,
    small_image_url,
    region,
    release_date,
    publication_date,
    languages
    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', books_cn + books_en)

cur.execute('''CREATE TABLE IF NOT EXISTS node (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER,
    name TEXT,
    is_root INTEGER
    );''')

cur.executemany('''insert into node (
    node_id,
    name,
    is_root
    ) values (?, ?, ?)
    ''', list(nodes.values()))

cur.execute('''CREATE TABLE IF NOT EXISTS node_relation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descendant INTEGER,
    ancestor INTEGER
    );''')

cur.executemany('''insert into node_relation (
    descendant,
    ancestor
    ) values (?, ?)
    ''', list(node_relation.values()))

cur.execute('''CREATE TABLE IF NOT EXISTS node_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT,
    node_id INTEGER
    );''')

cur.executemany('''insert into node_map (
    item_id,
    node_id
    ) values (?, ?)
    ''', node_map)

cur.execute('''CREATE TABLE IF NOT EXISTS status
    ( id INTEGER PRIMARY KEY AUTOINCREMENT, version INTEGER, count INTEGER, new_count INTEGER, time INTEGER );''')

cur.execute('insert into status (version, count, new_count, time) values (?, ?, ?, ?)', status.to_list())

# conn.commit()
# cur.close()
# conn.close()

# save reviews to database

# conn = sqlite3.connect('data/reviews_' + str(status.version) + '.db')
# cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT,
    editorial_review TEXT
    );''')

cur.executemany('''insert into review (
    item_id,
    editorial_review
    ) values (?, ?)
    ''', reviews)

conn.commit()
cur.close()
conn.close()

zip_f = compress('data/books_' + str(status.version) + '.db')
status.update(zip_f)
