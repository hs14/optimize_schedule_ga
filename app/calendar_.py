from datetime import date
import calendar

import jpholiday

class Calendar(object):

    def __init__(self, year:int, month:int):
        self.year     = year
        self.month    = month
        self.dates    = []     # シフトを組む日付
        self.days     = []     # 日付に対応する曜日
        self.capacity = []     # 日付に対応するキャパシティ
        self._make_weekday_list()

    def _make_weekday_list(self):
        '''
        指定月の平日の日付と曜日のリストを作成
        '''

        # 指定月の最終日を取得
        month_range = calendar.monthrange(self.year, self.month)
        end_day     = month_range[1]

        # キャパシティは4で固定
        CAPASITY = 4

        # 日ごとに曜日を取得してリストに詰める
        for index in range(end_day):
            date_num  = index + 1      # インデックスが0から始まるため
            date_date = date(self.year, self.month, date_num)
            day_num   = date_date.weekday() 

            # 平日でない場合は終了
            if self._is_holiday(date_date, day_num):
                continue

            # 曜日を文字列に直してリストに格納
            day_name = calendar.day_name[day_num]
            self.dates.append(date_num)
            self.days.append(day_name)
            self.capacity.append(CAPASITY)
    
    def _is_holiday(self, check_date:date, day_of_week:int):
        '''
        指定の日付が休みかどうか
        '''

        # 土日の場合はTrue
        (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY) = range(7)
        if day_of_week in [SATURDAY, SUNDAY]:
            return True
        
        # それ以外の場合は祝日判定
        return jpholiday.is_holiday(check_date)

if __name__ == '__main__':
    pass
