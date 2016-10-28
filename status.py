#!/usr/bin/env python3
import hashlib
import json
import os
import time

from datetime import datetime
from functools import partial

data_file = "data/status.json"


class Status:
    version = 0
    count = 0
    new_count = 0
    timestamp = None
    md5 = None

    def __init__(self):
        if not os.path.exists(data_file):
            return
        with open(data_file) as f:
            self.__dict__ = json.loads(f.read())

    def dump(self):
        print(self.version, self.timestamp)

    def json(self):
        return {"version": self.version, "count": self.count, "new_count": self.new_count, "timestamp": self.timestamp,
                'md5': self.md5}

    def update(self, file):
        self.timestamp = int(time.mktime(datetime.now().utctimetuple()))
        self.md5 = md5sum(file)
        with open(data_file, "w") as f:
            f.write(json.dumps(self.json()))

    def to_list(self):
        if not self.timestamp:
            self.timestamp = int(time.mktime(datetime.now().utctimetuple()))
        return [self.version, self.count, self.new_count, self.timestamp]

    def bump(self):
        self.version += 1


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()
