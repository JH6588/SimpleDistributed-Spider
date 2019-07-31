from config import *
import traceback
import time


class Schedules:

    def __init__(self, startnode, source):
        '''

        :param startnode:
        :param source:  str
        :param last_idx: int the lastest idx of the source
        '''
        self.startnode = startnode
        self.source = source
        self._old_last_idx = self.initialize_old_last_idx()

    def initialize_old_last_idx(self):
        _old_last_idx = REDISPRO .hget(SPIDER_UPDATER, self.source)
        if not _old_last_idx:
            return 0
        self.old_last_idx = int(_old_last_idx.decode())

    @property
    def old_last_idx(self):

        return self._old_last_idx

    @old_last_idx.setter
    def old_last_idx(self, last_idx):
        REDISPRO.conn. hset(SPIDER_UPDATER, self.source, last_idx)
        self._old_last_idx = last_idx

    def initlizer(self, initiate_data):
        print("start will  go")
        time.sleep(30)
        self.startnode.set_initiate_data(initiate_data)
        self.startnode.parse()

    def will_initlize(self, node_list):
        return [x for x in node_list if REDISPRO.conn.exists(x.name) == True]

    def get_update_initiate_data(self, last_idx):
        self.initialize_old_last_idx()
        print("old index", self.old_last_idx)
        if last_idx > self.old_last_idx:
            return range(self.old_last_idx, last_idx + 1)
        return []

    def run_spider(self, spider_node_list, catch_error_link=False, catch_exception=False, except_wait=30):
        '''

        :param spider_node_list:   list 爬虫层级列表
        :param catch_error_link: boolean  遇到错误时 是否将链接重新放回缓存
        :param catch_exception: boolean  是否捕获错误
        :param except_wait: int 某一层级遇到错误时停止 在捕获错误时 需要重新运行的话 ，需暂停的时间
        :return:
        '''
        for i in range(1, len(spider_node_list)):
            while True:
                redis_key = spider_node_list[i - 1].name
                k =REDISPRO.pop_key(redis_key)
                print(k)
                if k == None:
                    break
                _layer = spider_node_list[i]
                _layer.set_url(k.decode())
                print("layer {}:{}".format(_layer, k.decode()))
                try:
                    _layer.parse()
                except Exception as e:
                    print("CRAWLER ERROR ", e)
                    traceback.print_exc()
                    if not catch_exception:
                        raise Exception()
                    else:
                        time.sleep(except_wait)
                finally:
                    if catch_error_link:
                       REDISPRO.conn.lpush(redis_key, _layer.url)

    def update_lastest(self, nodelist, last_idx, catch_exception=False, catch_error_link=False):
        '''

        :param nodelist:  NodeProcess list

        :return: update int  number
        '''

        if not self.will_initlize(nodelist):
            print("start initlization...")
            self.initlizer(self.get_update_initiate_data(last_idx))

        self.run_spider(nodelist, catch_error_link=catch_error_link, catch_exception=catch_exception)
