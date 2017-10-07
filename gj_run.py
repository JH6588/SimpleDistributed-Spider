from my_spider import layer_obj_list,Rs




for i in  range(1,len(layer_obj_list)):
    while True:
        k = Rs .pop_key(layer_obj_list[i-1].name)

        if k == None:
            break
        _layer = layer_obj_list[i]
        _layer.set_url(k)
        print("layer {}:{}".format(_layer ,k) )
        _layer.parse()

