
class Node:
    node = None  # ancestor
    id = None
    is_root = False
    name = None

    def __init__(self, o):
        self.__dict__ = o

        if 'node' in o:
            self.node = Node(o['node'])

    def dump(self):
        return clean_dict(self.__dict__)


def clean_dict(d):
    if not isinstance(d, dict):
        return d
    return dict((k, clean_dict(v)) for k, v in d.items() if v is not None)


