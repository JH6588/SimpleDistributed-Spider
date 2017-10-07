from my_util import Redispro,NodeProcess,judge_tree
from  downloader import Downloader
import pymongo
import traceback

import my_config
mongo_conn = pymongo.MongoClient(host=my_config.MONGO_HOST)
mongo_conn.admin.authenticate(my_config.MONGO_USER, my_config.MONGO_PASSWD)
db = mongo_conn.car
tab = db.gj


DOMAIN = "https://3g.ganji.com/"

start_url = 'https://3g.ganji.com/gz/?a=c&ifid=shouye_chengshi&backURL=ershouche%2Fa1s1%2F'
Rs = Redispro(my_config.REDIS_HOST,"6379",my_config.REDIS_PASSWD)  #


class GanDownloader(Downloader):  #根据爬虫任务定制自己的download 类

    def result__testing(self,html):  #根据爬虫任务 定制自己result_testing 方法
        if "验证码" in html:
            print(html)
            return False
        else:
            return True
    def chage_proxy(self):

        return  Downloader()(my_config.PROXY_CHANGE_URL ) #实现你自己 得到新ip的方法
ganji_downloader = GanDownloader(num_retries=5,request_verify=False)



class StartNode(NodeProcess): #city 取得所有城市地址
    def response(self):
        return ganji_downloader(self.url)
    def parse(self):
        for ele in self.make_tree().xpath('//div[@class ="city-char"]//a'):
                Rs.lpush_key(self.name, DOMAIN + ele.xpath("./@href")[0])


class LayerNodePages(NodeProcess):  #page
    def response(self):
        return ganji_downloader(self.url)
    def parse(self):
        for ele in  self.make_tree().xpath("//span[@class= 'change-page']//option/@value"):
            print(ele)
            Rs.rpush_key(self.name, DOMAIN + ele)



class LayerNodeUnit(NodeProcess):
    def response(self):
        return ganji_downloader(self.url)

    def parse(self):
        for ele in self.make_tree().xpath('//a[@class="infor"]/@href'):
            print(ele)
            Rs.rpush_key(self.name, DOMAIN + ele)




class LayerNodeDetail(NodeProcess):

    def response(self):
        return ganji_downloader(self.url)
    def parse(self):
        tree = self.make_tree()
        item ={}
        try:
            item['url'] = self.url
            item['city'] = judge_tree(tree,'//a[@rel="nofollow"]/span/text()')

            item['phone_number'] = judge_tree(tree,"//p[@class='tel-code']/text()")
            item['name'] = judge_tree(tree,"//div[@class='car-shop']/p[last()]/span[last()]/text()")
            item['car'] = judge_tree(tree,"//h1/text()")
            raw_price = judge_tree(tree, '//div[@class="price-contrast"]//tr/td/text()')
            try:
                item['original_price'] = int(float(raw_price) *10000)
            except Exception as e  :
                print("origin_price error :{} url: {}" .format(e ,self.url) )
                item['original_price']  =raw_price

            price = judge_tree(tree,'//em[@class="fc-red"]/text()')
            if "万" in price:
                item['price'] = float(price) *10000

            item['_id'] = item['phone_number'] + item['car']
            print(item)
            tab.insert(item)
        except Exception as e:
            print("错误url: {}原因 :{} \n,".format(self.url,e) , traceback.print_exc())




start_node = StartNode("city")

layer_obj_list = [start_node,LayerNodePages("pages"),LayerNodeUnit("unit") ,LayerNodeDetail('detail')]