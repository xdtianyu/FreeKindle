import json

from node import Node


class Book:
    title = ''
    average = 0
    price = 0
    author = ''
    min = 0
    score = 0
    url = ''
    min_day = ''

    item_id = None
    pages = None
    publisher = None
    brand = None
    asin = None
    binding = None
    edition = None
    editorial_review = None
    isbn = None
    large_image_url = None
    medium_image_url = None
    small_image_url = None
    region = None
    release_date = None
    publication_date = None
    sales_rank = None
    languages = None
    nodes = None

    def __init__(self, o=None):
        if o is None:
            o = dict()
        self.__dict__ = o
        nodes = []
        if 'nodes' in o:
            for n in o['nodes']:
                node = Node(n)
                nodes.append(node)
            self.nodes = nodes

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=2, ensure_ascii=False, sort_keys=True)

    def dump(self):
        return clean_dict(self.__dict__)

    def tuple(self):
        languages = None
        if self.languages and len(self.languages) > 0:
            languages = self.languages[0]
        return (
            self.title, self.author, self.score, self.url, self.item_id, self.pages, self.publisher, self.brand,
            self.asin, self.edition, self.isbn, self.large_image_url, self.medium_image_url, self.small_image_url,
            self.region, self.release_date, self.publication_date, languages
        )


def clean_dict(d):
    if not isinstance(d, dict):
        return d
    return dict((k, clean_dict(v)) for k, v in d.items() if v is not None)
