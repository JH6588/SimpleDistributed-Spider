import traceback
import time
from config import *


def will_initlize(node_list):
    return [x for x in node_list if REDISPRO.conn.exists(x.name) == True]


def initlizer(startnode, start=0, end=0):
    print("start will  go")
    time.sleep(30)
    startnode.set_start_end(start, end)
    startnode.parse()



def run_spider(spider_node_list, catch_error_link=False, catch_exception=False, except_wait=30):
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
            k = REDISPRO.rpop(redis_key)
            if k == None:
                break
            _layer = spider_node_list[i]
            _layer.set_url(k)
            print("layer {}:{}".format(_layer, k))
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
                    REDISPRO.lpush(redis_key, _layer.url)


def update_lastest(nodelist, source, last_idx, catch_exception=False, catch_error_link=False):
    '''
    注意 ： 更新任务，必须保证 startnode  实现了 start_start_end 方法
    :param nodelist: list  爬虫层级列表
    :param source:  str  更新信息缓存到以hash 的方式 缓存到redis ,hash的name为 SPIDER_UPDATER  ,source 为key
    :param last_idx: int 该网站 上一次 已经爬到的id
    :return: update int  id 更新数目
    '''

    _old_last_idx = REDISPRO.conn.hget(SPIDER_UPDATER, source)
    if not _old_last_idx:
        return 0
    old_last_idx = int(_old_last_idx.decode())
    if old_last_idx >= last_idx:
        return 0
    print("old last idx ", old_last_idx)
    if not will_initlize(nodelist):
        print("start initlization..")
        initlizer(nodelist[0], old_last_idx, last_idx)

    run_spider(nodelist, catch_error_link=catch_error_link, catch_exception=catch_exception)
    return last_idx - old_last_idx
