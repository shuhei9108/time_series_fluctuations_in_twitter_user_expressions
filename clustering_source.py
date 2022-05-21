import json
import csv
import sys
import operator
import os
import pandas as pd
# import japanize_matplotlib
import seaborn as sns
import MeCab
import collections as cl
import matplotlib.pyplot as plt
import numpy as np
import codecs
from tslearn.clustering import KShape
from tslearn.preprocessing import TimeSeriesScalerMeanVariance
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


def tenti(l):
    return [list(x) for x in zip(*l)]


def array_to_csv(arr, path):
    np.savetxt(path, arr, delimiter=',')


# 標準化する


def standardization(x, axis=None, ddof=0):
    x_mean = x.mean(axis=axis, keepdims=True)
    x_std = x.std(axis=axis, keepdims=True, ddof=ddof)
    return (x - x_mean) / x_std


# 正規化する

def min_max(x, axis=None):
    min = x.min(axis=axis, keepdims=True)
    max = x.max(axis=axis, keepdims=True)
    result = (x-min)/(max-min)
    return result

# 平均二乗誤差を計算


def mse(a, b, ax=0):
    result = (np.square(a - b)).mean(axis=ax)
    return result


def write_json(data, path):
    if len(data) != 0:
        f = codecs.open(path, 'w', 'utf-8_sig')
        json.dump(data, f, indent=2, ensure_ascii=False)


def ave_move(n, l):
    length = len(l)
    l_n = [0] * length
    i = 0
    while i < length:
        j = -n
        while j < n:
            l_n[i] += l[(i + j) % length]
            j += 1
        l_n[i] = l_n[i] / 10
        i += 1
    return l_n

# ソースごとの時系列データの作成


def dict_sources():
    sources = {}
    for i in range(index):
        read_path = '1minutesdata2/{}.json'.format(i)
        with open(read_path, encoding="utf-8_sig") as f:
            read_data = json.load(f)
        max = read_data["data_num"]
        for j in range(max):
            source = read_data["{}".format(j)]["source"]
            if source in sources:
                sources[source][i] += 1
            else:
                sources[source] = [0] * index
                sources[source][i] = 1
        print("sources(index:{})".format(i))
    del_count = 0
    sources_n = {}
    for k, v in sources.items():
        sources_n[k] = ave_move(5, v)
        sources_n[k].append(sources_n[k][0])
    print_value("length", sources_n)
    write_json(sources_n, "cluster_sources/sources_tweetnum.json")
    return sources_n


def transform_vector(time_series_array):
    # ベクトルに変換
    stack_list = []
    for j in range(len(time_series_array)):
        data = np.array(time_series_array[j])
        data = data.reshape((1, len(data))).T
        stack_list.append(data)
    # 一次元配列にする
    stack_data = np.stack(stack_list, axis=0)
    return stack_data


def main():
    max_cluster_num = 3
    # ツイートソースが含むツイート数の下限
    min_length = 10000
    d_sources = {}
    with open("cluster_sources/sources_tweetnum.json", encoding="utf-8_sig") as f:
        sources = json.load(f)
    # sources = dict_sources()
    for k, v in sources.items():
        s = sum(v)
        if s > min_length:
            d_sources[k] = v
    length = len(d_sources)
    sources = list(d_sources.keys())
    print_value("sources", sources)
    tsdata = np.zeros((length, index+1))
    for i in range(length):
        for j in range(index+1):
            tsdata[i][j] = d_sources[sources[i]][j]
        print("==============================")
        print(i)
        print("==============================")
        print(tsdata)
    # 標準化
    tsdata = standardization(tsdata, axis=1)
    print_value("standardization", tsdata)
    write_path = "cluster_sources/tsdata_tweetnum.csv"
    np.savetxt(write_path, tsdata)

    stack_data = transform_vector(time_series_array=tsdata)

    seed = 0
    np.random.seed(seed)

    distortions = []
    centroids = {}

    # 1~max_cluster_num-1クラスタまで計算
    for i in range(1, max_cluster_num):
        print_value("cluster_num_max", i)
        ks = KShape(n_clusters=i, n_init=10, verbose=True, random_state=seed)
        # クラスタリングの計算を実行
        # ks.fit(stack_data)
        y_pred = ks.fit_predict(stack_data)
        # print_value("y_pred", y_pred)
        # クラスタリングして可視化

        for yi in range(i):  # クラスターy1に対して
            plt.figure(figsize=(16, 5))
            print_value("cluster_num", yi+1)
            cluster_mse = []
            cluster_words = []
            cnt = 0
            plt.subplot(1, 1, 1, xlabel='時刻', ylabel='標準化出現個数',
                        xticks=xticks, xticklabels=range(25))
            for k in range(length):
                xx = stack_data[k].ravel()
                centroid = ks.cluster_centers_[yi].ravel()
                centroids["{0}-{1}".format(i, yi)] = ks.cluster_centers_[yi]
                mse_xx_centroid = round(mse(xx, centroid), 5)
                if y_pred[k] == yi:
                    cnt += 1
                    plt.plot(xx, "k-", alpha=.1, c="blue")
                    cluster_mse.append(mse_xx_centroid)
                    cluster_words.append(sources[k])
            plt.plot(centroid, "red")
            plt.title("Cluster:{0} (Count:{1})".format(yi + 1, cnt))
            print_value("cluster_mse", cluster_mse)
            df = pd.DataFrame(cluster_mse[:20], columns=[
                              '平均二乗誤差'], index=cluster_words[:20])
            df.sort_values('平均二乗誤差', inplace=True)
            df.to_csv(
                "cluster_sources/mse_{0}-{1}.csv".format(i, yi+1))
            print_value("cluster_sources_{0}-{1}.csv".format(i, yi+1), df)
            # csvにして保存
            # RTの方も同様に（columsにクラスター数をappendした後、”sum”,”RT”をappend)
            plt.tight_layout()
            plt.savefig(
                "cluster_sources/cluster{0}-{1}.png".format(i, yi+1))
            plt.clf()
        print_value("ks.inetia_", ks.inertia_)
        distortions.append(ks.inertia_)
    plt.clf()
    plt.figure(figsize=(16, 9))
    plt.plot(range(1, max_cluster_num), distortions, marker='o')
    plt.xlabel('Number of clusters')
    plt.ylabel('Distortion')
    # plt.show()
    plt.savefig("cluster_sources/numberofcluster.png")
    plt.clf()

    # セントロイドをまとめて図示
    color = ["b", "g", "r", "c", "m", "y", "k", "orange"]
    for i in range(1, max_cluster_num):
        write_path = "cluster_sources/centroids{}.png".format(i)
        plt.figure(figsize=(16, 5))
        plt.subplot(1, 1, 1, xlabel='時刻', ylabel='標準化出現個数',
                    xticks=xticks, xticklabels=range(25))
        for j in range(i):
            plt.plot(centroids["{0}-{1}".format(i, j)],
                     color[j], label="cluster{}".format(j+1))
        plt.legend()
        plt.title("max cluster num:{0}".format(i))
        plt.tight_layout()
        plt.savefig(
            write_path)
        plt.clf()

    print("length:{}".format(length))


if __name__ == "__main__":
    main()
