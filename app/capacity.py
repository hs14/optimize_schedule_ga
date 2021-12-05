class Capacity(object):
    '''
    定員の情報
    '''
    def __init__(self, maximum, minimum=1):
        '''
        Parameters
        ----------
        maximum : int
            最大人数(定員)
        minimum : int
            最少人数
        '''
        self.maximum = maximum
        self.minimum = minimum