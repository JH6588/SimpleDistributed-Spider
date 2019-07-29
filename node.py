import lxml.html
from downloader import Downloader

D = Downloader()


class NodeProcess:
    _instance = None

    #
    def __new__(cls, name):
        if not cls._instance:
            cls._instance = super(NodeProcess, cls).__new__(cls)
        return cls._instance

    def __init__(self, name):
        self.name = name

    def set_url(self, url):
        self.url = url

    def response(self):
        return D(self.url)

    def make_tree(self):
        return lxml.html.fromstring(self.response())

    def parse(self):
        pass
