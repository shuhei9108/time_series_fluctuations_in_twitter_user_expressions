import numpy as np
import matplotlib.pyplot as plt
import collections as cl
import os
import json
import MeCab
import re
import codecs
import scipy.stats
plt.rcParams["font.family"] = "IPAexGothic"


def write_json(data, path):
    if len(data) != 0:
        f = codecs.open(path, 'w', 'utf-8_sig')
        json.dump(data, f, indent=2, ensure_ascii=False)

# 書き込み用1440個（前後5分の平均）のファイルを作る（それぞれが空のAlistとVlistを持つ）
#
# 以下を1minutesdataの1440個のファイルに対して繰り返し
#   対応する属性を含むツイートでVlistとAlistをそれぞれ作る。
#   （１minutesdataのインデックス　（－４～＋５））％１４４０をしてデータを入れるファイルを決定
#   10minutesdata前後5インデックスのファイルのVlistとAlistにappend(0なら-4から+5までのファイルに入る)
#


def MTMF():  # 後で属性による条件分岐のための引数を加える。
    i = 0
    while i < 1440:
        read_path = '1minutesdata/{}.json'.format(i)
        with open(read_path, encoding="utf-8_sig") as f:
            read_data = json.load(f)
        print(read_path + " is read")
        j = 0
        max = read_data["data_num"]
        A_list = []
        V_list = []
        while j < max:
            # ここに属性による条件分岐を加える。当てはまらなければ次の添字に進む
            A_list.extend(read_data["{}".format(j)]["A_list"])
            V_list.extend(read_data["{}".format(j)]["V_list"])
            j += 1
        k = -4
        while k < 6:
            l = (i + k) % 1440
            # 属性によってパスを変える。ディレクトリが空ならcreateTMFを実行して1440個のファイルを作成する。
            write_path = '10minutesdata/{}.json'.format(l)
            with open(write_path, encoding="utf-8_sig") as f:
                write_data = json.load(f)
            write_data["A_list"].extend(A_list)
            write_data["V_list"].extend(V_list)
            write_json(write_data, write_path)
            print(write_path + " is writed")
            k += 1
        i += 1


def main():
    # 時間ごとに分ける（後で属性指定のための引数を加える）
    MTMF()


if __name__ == "__main__":
    main()
