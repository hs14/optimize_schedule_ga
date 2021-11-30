class Optimize(object):
    '''
    最適化パラメータの情報
    ''' 
    def __init__(self, pop, cxpb, mutpb, indpb, ngen, tournsize):
        '''
        Parameters
        ----------
        pop : int
            個体数
        cxpb : float
            交叉を実施する確率
        mutpb : float
            突然変異を起こす確率
        indpb : float
            突然変異時の各属性の反転確率
        ngen : int
            進化計算回数
        tournsize : int
            トーナメントに参加させる個体数
        '''
        self.pop       = pop
        self.cxpb      = cxpb
        self.mutpb     = mutpb
        self.indpb     = indpb
        self.ngen      = ngen
        self.tournsize = tournsize


class Evaluate(object):
    '''
    最適化の評価関数の情報
    '''

    def __init__(self, evaluate_method, weight, description):
        '''
        Parameters
        ----------
        evaluate_method : str
            評価関数名 (エイリアス名)
        weight : float
            評価関数の重み
        description : str
            評価の説明文 (最後に評価値とともに出力する)
        '''
        self.evaluate_method = evaluate_method
        self.weight          = weight
        self.description     = description


def get_method_alias_list(evaluate_objs):
    '''
    評価関数インスタンスのmethodエイリアスのリストを返す
    '''
    method_alias_list = []
    for evaluate_obj in evaluate_objs:
        method_alias_list.append(evaluate_obj.evaluate_method)
    
    return method_alias_list

def get_weight_tuple(evaluate_objs):
    '''
    評価関数インスタンスのweightをtupleにして返す
    '''
    weight_list = []
    for evaluate_obj in evaluate_objs:
        weight_list.append(evaluate_obj.weight)
    
    return tuple(weight_list)


if __name__ == '__main__':
    pass