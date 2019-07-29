from spider_utils import SpiderHelper
from downloader import Downloader
from config import *
from node import NodeProcess
from schedule import *
import pymongo
import traceback

mongo_conn = pymongo.MongoClient(host=MONGO_HOST)
mongo_conn.admin.authenticate(MONGO_USER, MONGO_PASSWD)
db = mongo_conn.car
tab = db.gj



mobile_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1"


class GanDownloader(Downloader):  # 根据爬虫任务定制自己的download 类

    def result__testing(self, html):  # 根据爬虫任务 定制自己result_testing 方法
        if "验证码" in html:
            print(html)
            return False
        else:
            return True

    def chage_proxy(self):

        return Downloader()(PROXY_CHANGE_URL)  # 实现你自己 得到新ip的方法


ganji_downloader = GanDownloader(num_retries=5, user_agent=mobile_user_agent, request_verify=False)


class StartNode(NodeProcess):  # city 取得所有城市地址
    def response(self):
        return ganji_downloader(self.url)

    # 如果要做更新任务
    # def set_start_end(self, start ,end):
    #     self.page_range = range(start ,end)

    # def parse(self):
    #     # 35809
    #     for i in page_range:
    #         REDISPRO.rpush(self.name, XX_DOMAIN + "/index.php/vod/detail/id/{}.html".format(i))

    def parse(self):
        self.set_url( 'https://3g.ganji.com/gz/?a=c&ifid=shouye_chengshi&backURL=ershouche%2Fa1s1%2F')
        for ele in self.make_tree().xpath('//div[@class ="city-char"]//a'):
            REDISPRO.lpush_key(self.name, GANJI_DOMAIN + ele.xpath("./@href")[0])


class LayerNodePages(NodeProcess):  # page
    def response(self):
        return ganji_downloader(self.url)

    def parse(self):
        for ele in self.make_tree().xpath("//span[@class= 'change-page']//option/@value"):
            print(ele)
            REDISPRO.rpush_key(self.name, GANJI_DOMAIN + ele)


class LayerNodeUnit(NodeProcess):
    def response(self):
        return ganji_downloader(self.url)

    def parse(self):
        for ele in self.make_tree().xpath('//a[@class="infor"]/@href'):
            print(ele)
            REDISPRO.rpush_key(self.name, GANJI_DOMAIN + ele)


class LayerNodeDetail(NodeProcess):

    def response(self):
        return ganji_downloader(self.url)

    def parse(self):
        tree = self.make_tree()
        item = {}
        try:
            item['url'] = self.url
            item['city'] = SpiderHelper.judge_tree(tree, '//a[@rel="nofollow"]/span/text()')

            item['phone_number'] = SpiderHelper.judge_tree(tree, "//p[@class='tel-code']/text()")
            item['name'] = SpiderHelper.judge_tree(tree, "//div[@class='car-shop']/p[last()]/span[last()]/text()")
            item['car'] = SpiderHelper.judge_tree(tree, "//h1/text()")
            raw_price = SpiderHelper.judge_tree(tree, '//div[@class="price-contrast"]//tr/td/text()')
            try:
                item['original_price'] = int(float(raw_price) * 10000)
            except Exception as e:
                print("origin_price error :{} url: {}".format(e, self.url))
                item['original_price'] = raw_price

            price = SpiderHelper.judge_tree(tree, '//em[@class="fc-red"]/text()')
            if "万" in price:
                item['price'] = float(price) * 10000

            item['_id'] = item['phone_number'] + item['car']
            print(item)
            tab.insert(item)
        except Exception as e:
            print("错误url: {}原因 :{} \n,".format(self.url, e), traceback.print_exc())


gj_spider_list = [StartNode("city"), LayerNodePages("pages"), LayerNodeUnit("unit"), LayerNodeDetail('detail')]

if __name__ == '__main__':

    import sys, signal


    def signal_handler(signal, frame):
        mongo_conn.close()
        sys.exit(0)


    signal.signal(signal.SIGINT, signal_handler)

    # 是否需要运行start 节点
    if will_initlize(gj_spider_list):
        initlizer(gj_spider_list[0])
    try:
        run_spider(gj_spider_list, catch_exception=True, except_wait=180, catch_error_link=False)
    except:
        mongo_conn.close()
