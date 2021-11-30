## 概要

- 遺伝的アルゴリズムを使って、スケジューリング最適化する。
- (うまく解けていない)

## 制約条件

- 以下を含め、各種条件をsetting.tomlにて設定する。

- 日ごとの定員を超えないようにする。
- 組み合わせでの出勤が必要な人が、正しく組み合わせされている。
- マネージャがどの日も1人はいるように設定される。
- 出勤できない日は休みにする。
- 出勤が必要な日は出勤にする。
- 合計の工数が予定工数に近くなるようにする。

## こちらの記事を大いに参考にした

https://qiita.com/shouta-dev/items/1970c2746c3c30f6b39e

## コンテナ起動

```
$ docker compose up -d
```

## コンテナへの入り方

```
$ docker exec -it deap_optimize bash
```

## 実行方法

```
$ cd /usr/local/deap_optimize
$ python3 main.py
```
