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


def list_to_csv(l, path):
    f = codecs.open(path, 'w', 'utf-8_sig')
    writer = csv.writer(f)
    writer.writerows(l)


def csv_to_2dlist(path):
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        l = [row for row in reader]
        return l


def tenti(l):
    return [list(x) for x in zip(*l)]


def array_to_csv(arr, path):
    np.savetxt(path, arr, delimiter=',')

# 正規化する


def min_max(x, axis=None):
    min = x.min(axis=axis, keepdims=True)
    max = x.max(axis=axis, keepdims=True)
    result = (x-min)/(max-min)
    return result


def corr_df(tsdata, cluster_num, public_metrics, mse_pb, hinsi, type):
     # RT以外も表にできるように関数にする
        # 保存ディレクトリとファイル名をかえる
    i = cluster_num
    length = tsdata["length"]
    words = tsdata["words_list"]
    l = tsdata[public_metrics]
    mse_pb_columns = []
    array = np.array(l)
    for k in range(length):
        mse_sum = 0
        for l in range(i):
            mse_sum += mse_pb[k][l]
        mse_pb[k][i] = mse_sum / i
        mse_pb[k][i+1] = array[k]
    for j in range(i):
        mse_pb_columns.append("mse_{}".format(j+1))
    mse_pb_columns.append("mse_sum")
    mse_pb_columns.append(public_metrics)
    df_rt = pd.DataFrame(mse_pb, columns=mse_pb_columns, index=words)
    df_rt.sort_values(public_metrics, inplace=True)
    df_rt.to_csv(
        "cluster{0}{1}/{2}_mse_".format(hinsi, type, i) + public_metrics + ".csv")
    df_corr = df_rt.corr()
    plt.clf()
    sns.set_context("talk")
    fig = plt.subplots(figsize=(8, 8))
    sns.heatmap(df_corr, annot=True, fmt='.2f', cmap='Blues', square=True)
    plt.savefig(
        "cluster{0}{1}/{2}_mse_".format(hinsi, type, i) + public_metrics + "_heatmap.png")
    plt.clf()
    sns.pairplot(df_rt)
    plt.savefig(
        "cluster{0}{1}/{2}_mse_".format(hinsi, type, i) + public_metrics +
        "_pairplot.png")
