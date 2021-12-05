import copy
import pandas as pd

# 出勤を表す定数
ATTENDANCE = 1

class Shift(object):
    '''
    シフトを表すクラス
    (日数 * 人数)次元の配列で、シフト案を持つ。
    '''

    def __init__(self, shift_list, calendar_obj, members):
        self.shift_list = shift_list
        self.calendar   = calendar_obj
        self.members    = members
        self.df_data    = self.set_dataframe_to_instance()

        # tomlファイルで指定するためにインスタンスメソッドのエイリアスを設定
        self.methods = {
            'get_sum_over_capacity_day': self.get_sum_over_capacity_day,
            'get_diff_actual_and_plan_hour': self.get_diff_actual_and_plan_hour,
            'get_sum_manager_not_exist_day': self.get_sum_manager_not_exist_day,
            'get_sum_dependency_violation_day': self.get_sum_dependency_violation_day,
            'get_sum_assign_prohibit_day': self.get_sum_assign_prohibit_day,
            'get_sum_not_assign_required_day': self.get_sum_not_assign_required_day,
            'get_sum_under_lower_limit_day': self.get_sum_under_lower_limit_day,
        }

    def _search_dependent_member(self, dep_list):
        '''
        指定したリストに該当するメンバーがmembersの何番目に入っているかのリストを返す
        '''
        member_index = []
        for dep in dep_list:
            for index, member in enumerate(self.members):
                if member.no == dep:
                    member_index.append(index)
        
        return member_index
    
    def _search_date_index_in_calendar(self, day):
        '''
        指定した日が、カレンダーの中で何番目に格納されているかを返す
        '''
        for index, date in enumerate(self.calendar.dates):
            if day == date:
                return index

    def _slice_shift_list(self):
        '''
        1次元リストを、メンバーごとのリストに2次元化変換
        '''
        date_num   = len(self.calendar.dates)
        member_num = len(self.members)

        sliced = []
        for num in range(member_num):
            start = date_num * num
            end   = date_num * (num + 1)
            sliced.append(self.shift_list[start:end])
        
        return sliced
    
    def _make_days_shift(self):
        '''
        1次元リストを、日ごとのリストに2次元化変換
        '''
        date_num   = len(self.calendar.dates)
        member_num = len(self.members)

        days_shift = []
        for d in range(date_num):
            day_shift = []
            for m in range(member_num):
                day_shift.append(self.shift_list[date_num * m + d])
            days_shift.append(day_shift)
        
        return days_shift
    
    def _make_member_names(self):
        '''
        メンバーの名前のリストを作成
        '''
        member_names = [member.name for member in self.members]
        return member_names
    
    def set_dataframe_to_instance(self):
        '''
        変数に格納されている値からDataFrameを作る
        '''
        return pd.DataFrame(
            data = self._make_days_shift(),
            index = self.calendar.dates,
            columns = self._make_member_names()
        )
    
    def print_shift(self):
        '''
        シフトを整形して表示する
        '''
        print(self.df_data.T)
    
    def to_file(self):
        '''
        csv, tsvに出力する
        '''
        self.df_data.to_csv('./output.csv')
        self.df_data.to_csv('./output.tsv', sep='\t')

    
    def _get_member_nos_by_date_index(self, date_index):
        '''
        指定の日(インデックス)に出勤することになっているメンバー番号のリストを取得
        '''       
        member_nos = []
        for assign_date, member in zip(self._slice_shift_list(), self.members):
            if assign_date[date_index] == ATTENDANCE:
                member_nos.append(member.no)
        
        return member_nos
    
    def get_sum_over_capacity_day(self):
        '''
        最大人数を超えている日数
        '''        
        over_capacity_day_num = 0
        for index, capacity in enumerate(self.calendar.upper_limit):
            if len(self._get_member_nos_by_date_index(index)) > capacity:
                over_capacity_day_num += 1
        
        return over_capacity_day_num
    
    def get_sum_under_lower_limit_day(self):
        '''
        最少人数を下回っている人数
        '''
        under_lower_limit_day_num = 0
        for index, lower_limit in enumerate(self.calendar.lower_limit):
            if len(self._get_member_nos_by_date_index(index)) < lower_limit:
                under_lower_limit_day_num += 1
        
        return under_lower_limit_day_num
    
    def get_diff_actual_and_plan_hour(self):
        '''
        工数の予実差の合計
        '''
        diff_hour_sum = 0
        date_num      = len(self.calendar.dates)

        for shift_list, member in zip(self._slice_shift_list(), self.members):
            actual_man_hour = sum(shift_list) / date_num
            diff            = abs(actual_man_hour - member.man_hour_rate)

            diff_hour_sum += diff    
        
        return diff_hour_sum
    
    def get_sum_manager_not_exist_day(self):
        '''
        マネージャがいない日の合計
        '''
        manager_not_exist_day_sum = 0
        for day_shift in self._make_days_shift():

            # マネージャのインデックスの合計値が0ならマネージャがいない
            sum_manager_attendance = 0
            for index, member in enumerate(self.members):
                if member.is_manager:
                    sum_manager_attendance += day_shift[index]
            
            if sum_manager_attendance == 0:
                manager_not_exist_day_sum += 1
        
        return manager_not_exist_day_sum
    
    def get_sum_dependency_violation_day(self):
        '''
        組み合わせ違反の日の合計
        '''
        violation_day_sum = 0
        for day_shift in self._make_days_shift():

            # 依存関係の指定のある人が、依存関係先の人と同じ出勤になっているか
            for index, member in enumerate(self.members):
                
                # 依存関係のない人であればスキップ
                if len(member.related_members) == 0:
                    continue
                
                # アサイン日でなければスキップ
                if day_shift[index] == 0:
                    continue
                
                # 依存関係がある人が全員休みの場合、違反と判定
                dep_member_index_list = self._search_dependent_member(member.related_members)
                sum_attendance = 0
                for dep_member_index in dep_member_index_list:
                    sum_attendance += day_shift[dep_member_index]
                
                if sum_attendance == 0:
                    violation_day_sum += 1
        
        return violation_day_sum
    
    def get_sum_assign_prohibit_day(self):
        '''
        出勤できない設定をした日に出勤になっている日数
        '''
        violation_day_sum = 0
        for shift_list, member in zip(self._slice_shift_list(), self.members):
            for impossible_date in member.impossible_dates:

                target_index = self._search_date_index_in_calendar(impossible_date)
                if shift_list[target_index] == ATTENDANCE:
                    violation_day_sum += 1
        
        return violation_day_sum
    
    def get_sum_not_assign_required_day(self):
        '''
        出勤必要な日が欠勤になっている日数
        '''
        violation_day_sum = 0
        for shift_list, member in zip(self._slice_shift_list(), self.members):
            for required_date in member.required_dates:

                target_index = self._search_date_index_in_calendar(required_date)
                if shift_list[target_index] != ATTENDANCE:
                    violation_day_sum += 1
        
        return violation_day_sum


if __name__ == '__main__':
    pass
