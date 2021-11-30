import random

from deap import base, creator, tools, cma
import toml

from member import Member
from calendar_ import Calendar
from shift import Shift
from optimize import Optimize, Evaluate
from optimize import get_method_alias_list, get_weight_tuple

def read_toml(file):
    '''
    tomlファイルの中身を読み込む
    '''
    params = toml.load(file)

    # Calendarインスタンスを作成
    param_calendar = params['calendar']
    calendar_obj = Calendar(
        param_calendar['year'],
        param_calendar['month']
    )

    # Memberインスタンスのリストを作成
    param_members = params['member']
    member_objs = []
    for member in param_members:
        member_obj = Member(
            member['no'],
            member['name'],
            member['is_manager'],
            member['man_hour_rate'],
            member['impossible_dates'],
            member['required_dates'],
            member['related_members']
        )
        member_objs.append(member_obj)
    
    # Optimizeインスタンスを作成
    param_optimize = params['optimize']
    optimize_obj = Optimize(
        param_optimize['pop'],
        param_optimize['cxpb'],
        param_optimize['mutpb'],
        param_optimize['indpb'],
        param_optimize['ngen'],
        param_optimize['tournsize']
    )

    # Evaluateインスタンスのリストを作成
    param_evaluate = params['evaluate']
    evaluate_objs = []
    for evaluate in param_evaluate:
        evaluate_obj = Evaluate(
            evaluate['method'],
            evaluate['weight'],
            evaluate['description']
        )
        evaluate_objs.append(evaluate_obj)

    return (calendar_obj, member_objs, optimize_obj, evaluate_objs)


def main():

    # ----------------------------------------------------------
    # tomlファイルの設定を読み込んでインスタンスを作成する。
    # ----------------------------------------------------------

    calendar_obj, members, optimize_obj, evaluate_objs = read_toml('./setting.toml')
    
    # ----------------------------------------------------------
    # creatorにより、第三引数以降の属性を持つクラスを作成する。
    # ----------------------------------------------------------

    # 適合度評価クラス
    creator.create('FitnessMin', base.Fitness, weights=get_weight_tuple(evaluate_objs))

    # 個体クラス (適合度評価クラスを変数に持たせる)
    creator.create('Individual', list, fitness=creator.FitnessMin)

    # ----------------------------------------------------------
    # toolboxにより、第三引数以降をパラメータに第二引数の関数を実行する
    # エイリアスを作成する。
    # ----------------------------------------------------------

    toolbox = base.Toolbox()

    # 0または1をランダムに設定する関数
    toolbox.register('attribute_bool', random.randint, 0, 1)

    # 個体を作成する関数 (個体クラスに、日数*人数次元のリストを設定する)
    shift_list_size = len(calendar_obj.dates) * len(members)
    toolbox.register('individual', tools.initRepeat, creator.Individual,
                        toolbox.attribute_bool, n=shift_list_size)
    
    # 集団を作成する関数
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)

    # 個体の評価関数
    def evaluate_shift(individual):
        shift = Shift(individual, calendar_obj, members)

        # tomlに記載した評価関数のエイリアスを実際の関数に戻してリスト化
        evaluate_methods = []
        for method_alias in get_method_alias_list(evaluate_objs):
            evaluate_methods.append(shift.methods[method_alias]())
        
        return tuple(evaluate_methods)

    toolbox.register('evaluate', evaluate_shift)

    # 交叉関数 (2つの個体を交叉させる)
    toolbox.register('mate', tools.cxTwoPoint)

    # 変異関数 (各属性を一定確率で反転させる)
    toolbox.register('mutate', tools.mutFlipBit, indpb=optimize_obj.indpb)

    # 選択関数 (トーナメント方式で選択する)
    toolbox.register('select', tools.selTournament, tournsize=optimize_obj.tournsize)

    # ----------------------------------------------------------
    # 進化計算開始
    # ----------------------------------------------------------
    pop = toolbox.population(n=optimize_obj.pop)

    # 初期集団の個体の評価
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    
    # 進化計算
    for i in range(optimize_obj.ngen):
        print(f'第{i}世代の計算中')

        # ----------------------
        #  選択
        # ----------------------

        # 次の世代の個体群を選択
        offspring = toolbox.select(pop, len(pop))

        # 個体群のクローンを生成
        offspring = list(map(toolbox.clone, offspring))

        # ----------------------
        #  交叉
        # ----------------------

        # 偶数番目と奇数番目の個体を交叉
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < optimize_obj.cxpb:
                toolbox.mate(child1, child2)

                # 交叉された個体の適合度を削除
                del child1.fitness.values
                del child2.fitness.values
        
        # ----------------------
        #  変異
        # ----------------------

        for mutant in offspring:
            if random.random() < optimize_obj.mutpb:
                toolbox.mutate(mutant)

                # 変異した個体の適合度を削除
                del mutant.fitness.values
        
        # ----------------------
        #  適合度再計算
        # ----------------------

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses   = map(toolbox.evaluate, invalid_ind)

        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        # ----------------------
        #  次世代群の設定
        # ----------------------

        pop[:] = offspring

    # ----------------------------------------------------------
    #  結果出力
    # ----------------------------------------------------------

    # 最適個体
    best_ind = tools.selBest(pop, 1)[0]

    # 各指標の出力
    print()
    print('--- 最も良い個体の評価結果 ---')
    for index, evaluate_obj in enumerate(evaluate_objs):
        print(f'{best_ind.fitness.values[index]:.2f}: {evaluate_obj.description}')

    # 最適個体の出力
    print()
    print(' --- 最も良い個体 ---')

    s = Shift(best_ind, calendar_obj, members)
    s.print_shift()
    s.to_file()


if __name__ == '__main__':
    main()
