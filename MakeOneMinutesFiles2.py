# import matplotlib.pyplot as plt
import collections as cl
import shutil
import os
import json
import MeCab
import re
import codecs
import datetime as dt
# plt.rcParams["font.family"] = "IPAexGothic"

# 形態素解析＋１分毎にファイルに分ける
# これを実行したらdaydataの中は空にする


def write_json(data, path):
    if len(data) != 0:
        f = codecs.open(path, 'w', 'utf-8_sig')
        json.dump(data, f, indent=2, ensure_ascii=False)

# タスク：時差の是生は収集時に行う。それに合わせてこちらも変更。


def MOMF():
    timedifference = 9  # 時差
    dir = "daydata"
    files = os.listdir(dir)
    file = [f for f in files if os.path.isfile(os.path.join(dir, f))]
    m = MeCab.Tagger('-Ochasen')
    file_num = 0
    alldata_num = 0
    filenamehour_list = [0] * 24
    for f in file:
        read_path = dir + "/" + f
        filename_hour = int(read_path[21:23])  # もとは14-16
        filenamehour_list[filename_hour] += 1
    filenamehour_min = min(filenamehour_list)
    filenamehour_list = [filenamehour_min] * 24
    # print(hour_list)
    for f in file:
        read_path = dir + "/" + f
        file_num += 1
        with open(read_path, encoding="utf-8_sig") as f:  # これから読み取るファイルを開く
            read_data = json.load(f)  # 読み取った特定日時ファイルから受け取ったjsonデータ
        print("loaded(r)" + read_path)

        # ここから下をコメントアウト

        # indexが0から始まらない読み込みファイルをはじく
        if not "0" in read_data:
            print(read_path + " do not have content")
            new_path = shutil.move(read_path, 'daydata_error/')
            print("=========================================")
            continue
        max = read_data['data_num']

        # 収集が途中で途切れていて｛｝が閉じていなかったりデータ数が合わないファイルをはじく
        if not "{}".format(max - 1) in read_data:
            print(read_path + " is not perfect file")
            new_path = shutil.move(read_path, 'daydata_error/')
            print("=========================================")
            continue
        # 読み取りデータの最初のデータの時刻を取得
        first_time = read_data['0']['created_at']
        # hourは読み取りファイルが変わらない限り変わらないのでforループ内で固定
        filename_hour = int(first_time[11:13])

        # ファイル数が最も少ない時間帯に数合わせする。（最小数を上回るなら取り込まない）
        if(filenamehour_list[filename_hour] == 0):
            print(read_path + " is timezone that is over number")
            # 後で使えるかも知れないから移動しないでとっておく。
            # new_path = shutil.move(read_path, 'daydata_over/')
            print("=========================================")
            continue

        first_minute = int(first_time[14:16])

        # 最初に書き込むファイルは0分台のはず（0分台じゃなかったらファイルをはじく）
        if not first_minute == 0:
            print(read_path + " is not started 0 minutes")
            new_path = shutil.move(read_path, 'daydata_imperfect/')
            print("=========================================")
            continue

        # 読み取りデータの最後のデータの時刻を取得
        last_time = read_data['{}'.format(max - 1)]['created_at']
        last_minute = int(last_time[14:16])
        if not last_minute == 59:
            print(read_path + " is not finished 59 minutes")
            new_path = shutil.move(read_path, 'daydata_imperfect/')
            print("=========================================")
            continue

        # データが少なすぎるファイルははじく
        if max < 5000:
            print(read_path + " has very few data")
            new_path = shutil.move(read_path, 'daydata_imperfect/')
            print("=========================================")
            continue

        time = dt.datetime.strptime(first_time, '%Y-%m-%dT%H:%M:%S.000Z')
        time = time + dt.timedelta(hours=timedifference)
        hour = time.hour
        minute = time.minute
        index = hour*60 + minute
        weekday = time.weekday()

        # 書き込みファイルのパスを指定（何時何分のデータか）
        write_path = '1minutesdata2/{}.json'.format(index)
        # もしパスが存在しなければファイルを作成
        if not os.path.exists(write_path):
            d_new = {"data_num": 0}
            write_json(d_new, write_path)
            # print("made new file {}".format(index))
        # 書き込むファイルから更新前のデータをとってくる
        with open(write_path, encoding="utf-8_sig") as f:
            write_data = json.load(f)
        # print("loaded(w) {}".format(index))

        # 書き込み側のインデックス
        j = write_data['data_num']

        # 読み取るファイルのデータが最後になるまで繰り返し
        i = 0

        while i < max:
            read_dataconts = read_data['{}'.format(i)]
            # 読み取りデータの時刻を更新
            new_minute = int(read_dataconts['created_at'][14:16])
            # 分数が変わったら、書き込み先ファイルを変える（今までの分数のファイルに書き込んで新しい分数のファイルを開く）
            if not minute == new_minute:

                # １分刻みじゃなかったら読み込み中止したかったが、もうそれ以前の分数を読み込みファイルから読み込んでしまっているので断念。
                # if not minute + 1 == new_minute:
                #     print(read_path + "is not started 0 minutes")
                #     continue

                # 書き込みファイルのデータ数更新
                write_data['data_num'] = j
                # 書き込み
                write_json(write_data, write_path)
                # print("writed(w) {}".format(index))
                # 次に書き込むファイルを指定
                minute = new_minute
                index = hour*60 + minute
                write_path = '1minutesdata2/{}.json'.format(index)
                # 書き込みファイルが存在しなければ作成
                if not os.path.exists(write_path):
                    d_new = {"data_num": 0}
                    write_json(d_new, write_path)
                    # print("made new file {}".format(index))
                with open(write_path, encoding="utf-8_sig") as f:
                    write_data = json.load(f)
                # print("loaded(w) {}".format(index))

                j = write_data['data_num']  # 書き込む側のインデックスを新しいファイルの最後尾に合わせる

            write_dataconts = {}  # 書き込みファイルのj番目に入れるデータ
            a = []
            v = []
            # n = []
            # 受け取った、新しく統合する一つのツイートテキスト
            text = read_dataconts["text"]
            text = re.sub(
                'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', text)
            text = re.sub(r'(@[^\s]+)', '', text)
            text = re.sub(r'(#[^\s]+)', '', text)
            node = m.parseToNode(text)
            while node:
                hinshi = node.feature.split(",")[0]
                if hinshi in '形容詞':
                    origin = node.feature.split(",")[6]
                    a.append(origin)
                if hinshi in '動詞':
                    origin = node.feature.split(",")[6]
                    v.append(origin)
                # 名詞はタイトルに合わない＋感情語抽出が難しそうなので消去
                # if hinshi in '名詞':konnntinha

                #     origin = node.feature.split(",")[6]
                #     n.append(origin)
                node = node.next
            write_dataconts["A_list"] = a
            write_dataconts["V_list"] = v
            # write_dataconts["N_list"] = n
            if "referenced_tweets" in read_dataconts:
                write_dataconts["tweet_type"] = read_dataconts["referenced_tweets"][0]["type"]
            write_dataconts["source"] = read_dataconts["source"]
            write_dataconts["public_metrics"] = read_dataconts["public_metrics"]
            write_dataconts["weekday"] = weekday
            write_data[j] = write_dataconts
            j += 1
            i += 1  # 次のデータを読み取る
            alldata_num += 1
        # 最後の書き込み

        write_data["data_num"] = j
        write_json(write_data, write_path)
        # print("last writed {} from ".format(index) + read_path)
        # 特定時間をカウントする
        filenamehour_list[filename_hour] -= 1
        # print(hour_list)
        new_path = shutil.move(read_path, 'daydata_loaded/')
        print("=========================================")

    print("総ツイート数：{0} 日数：{1}" .format(
        alldata_num, file_num/24))


def main():
    MOMF()  # 形態素解析＋１つにまとまったファイルにする


if __name__ == "__main__":
    main()
