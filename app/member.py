class Member(object):
    '''
    シフトを組む人の情報
    ''' 
    def __init__(self, no:int, name:str, is_manager:bool, man_hour_rate:float,
        impossible_dates:list, required_dates:list, related_members:list):
        '''
        コンストラクタ

        Parameters
        ----------
        no : int
            連番
        name : str
            氏名
        is_manager : bool
            マネージャかどうか (マネージャは各日1人はいるように)
        man_hour_rate : float
            工数 (0～1)
        impossible_dates : list
            出勤できない日付
        required_dates : list
            出勤が必要な日付
        related_members : int
            この人がいる日に出勤が必要、というリスト(Noを指定)
        '''
        self.no               = no
        self.name             = name
        self.is_manager       = is_manager
        self.man_hour_rate    = man_hour_rate
        self.impossible_dates = impossible_dates
        self.required_dates   = required_dates
        self.related_members  = related_members

if __name__ == '__main__':
    pass
