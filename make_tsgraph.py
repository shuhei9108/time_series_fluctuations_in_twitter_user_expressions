import json
import sklearn  # 機械学習のライブラリ
from sklearn.decomposition import PCA  # 主成分分析器
import matplotlib.ticker as ticker
import csv
import sys
import operator
import os
import pandas as pd
import seaborn as sns
import collections as cl
import matplotlib.pyplot as plt
import numpy as np
import codecs
plt.rcParams["font.family"] = "IPAexGothic"

index = 1440
n_words = 1000
xticks = [0,
          60,
          120,
          180,
          240,
          300,
          360,
          420,
          480,
          540,
          600,
          660,
          720,
          780,
          840,
          900,
          960,
          1020,
          1080,
          1140,
          1200,
          1260,
          1320,
          1380,
          1440
          ]

# デバッグ用の関数


def print_value(text, value):
    print("=================================================")
    print(text)
    print("=================================================")
    print("{}".format(value))
    print("=================================================")


def print_stack_data(stack_data, word_num, time):
    print_value("stack_data[{0}][{1}][0]".format(
        word_num, time), stack_data[word_num][time][0])

# リストをCSVに


def write_json(data, path):
    if len(data) != 0:
        f = codecs.open(path, 'w', 'utf-8_sig')
        json.dump(data, f, indent=2, ensure_ascii=False)

# 時間ごとソースごとのツイート数を返す。後でツイートタイプごとの関数にも使える


def make_tsgraph(stack_data, words, hinsi, word, path):
    plt.figure(figsize=(16, 5))
    plt.subplot(1, 1, 1, xlabel='時刻', ylabel='標準化出現個数',
                xticks=xticks, xticklabels=range(25))
    xx = stack_data[words.index(word)].ravel()
    plt.plot(xx, "k-", alpha=1, c="red")
    plt.title("word:{0}".format(word))
    plt.tight_layout()
    plt.savefig(path)
    plt.clf()


def main():

    type = "all"

    graph_wordsV = {"開く", "ます", "願う", "輝く", "来る"}
    graph_wordsA = {"少ない", "危ない", "いい", "寒い", "強い"}

    with open("cluster{0}{1}/tsdata.json".format("V", type), encoding="utf-8_sig") as f:
        d = json.load(f)
    stack_data = np.array(d["stack_data"])
    words = d["words_list"]

    for word in graph_wordsV:
        path = "pcaV{0}/{1}.png".format(type, word)
        make_tsgraph(stack_data, words, "V", word, path)

    with open("cluster{0}{1}/tsdata.json".format("A", type), encoding="utf-8_sig") as f:
        d = json.load(f)
    stack_data = np.array(d["stack_data"])
    words = d["words_list"]

    for word in graph_wordsA:
        path = "pcaA{0}/{1}.png".format(type, word)
        make_tsgraph(stack_data, words, "V", word, path)


if __name__ == "__main__":
    main()
