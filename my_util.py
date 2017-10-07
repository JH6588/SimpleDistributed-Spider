from downloader import Downloader
import redis
import lxml.html

D = Downloader()
class Redispro:
    def __init__(self, host, port, password,db=0):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db ,password = password)
        self.conn = redis.StrictRedis(connection_pool=self.pool)

    def rpush_key(self, k, v):
        self.conn.rpush(k, v)
    def lpush_key(self,k,v):
        self.conn.lpush(k,v)
    def pop_key(self, k):
        v = self.conn.rpop(k)
        if v != None:
            return v.decode()




class NodeProcess:
    _instance = None
    #
    def __new__(cls, name):
        if not cls._instance:
            cls._instance = super(NodeProcess, cls).__new__(cls)
        return cls._instance

    def __init__(self,name ):

        self.name = name

    def set_url(self,url):
        self.url = url

    def response(self):

        return D(self.url)

    def make_tree(self):
        return lxml.html.fromstring(self.response())

    def parse(self):
        pass



def judge_tree(tree, select_case,index =0):
    try:
        select_trees = tree.xpath(select_case)
        if index !=all:
            result = "".join(select_trees[index])

        else:
            result = ','.join([ele.strip() for ele in select_trees]) #只排除两侧的空格

    except Exception as e:
        print('错误',select_case,e)
        result = ''

    return result