import redis



class Redispro:
    def __init__(self, host, port, password,db=0):
        self.pool = redis.ConnectionPool(host=host, port=port, db=db ,password = password)
        self.conn = redis.StrictRedis(connection_pool=self.pool)

    def pop_key(self, k):
        v = self.conn.rpop(k)
        if v != None:
            return v.decode()




class SpiderHelper:
    @staticmethod
    def judge_tree(tree, select_case, index=0):
        try:
            select_trees = tree.xpath(select_case)
            if index != "all":
                result = "".join(select_trees[index])
            else:
                result = ','.join([ele.strip() for ele in select_trees])  # 只排除两侧的空格
        except Exception as e:
            print('错误', select_case, e)
            result = ''
        return result
