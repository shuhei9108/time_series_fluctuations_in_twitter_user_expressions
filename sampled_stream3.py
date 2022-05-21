import requests
import os
import json
import time
import datetime
import codecs
from janome.tokenizer import Tokenizer
from botocore.vendored.requests.exceptions import ChunkedEncodingError

# 環境変数"BEARER_TOKEN"を設定する必要がある。APIで取得した値を設定する。


def auth():
    return os.environ.get("BEARER_TOKEN")


# tweet.fields=以下でTwitterから取得する属性を指定
def create_url():
    return "https://api.twitter.com/2/tweets/sample/stream?tweet.fields=id,created_at,author_id,lang,conversation_id,referenced_tweets,public_metrics,source,geo,entities,organic_metrics,promoted_metrics,context_annotations,attachments,withheld"
    # public_metrics.retweet_count,public_metrics.reply_count,public_metrics.like_count,public_metrics.quote_count"


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

# jsonに書き込むための関数


def write_json(data, path):
    if len(data) != 0:
        f = codecs.open(path, 'w', 'utf-8_sig')
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    bearer_token = auth()
    url = create_url()
    headers = create_headers(bearer_token)
    # timeout = 0
    count = 0
    start = time.time()

    while True:
        # 15分あたりのリクエスト数上限50を超えないための条件分岐
        if count == 50:
            count = 0
            t = time.time() - start
            start = time.time()
            if t > 900:
                continue
            else:
                print("TooManyRequests, wait 15min")
                time.sleep(900)
                continue
        try:
            h = 'null'
            path = 'null'
            d_update = {}
            with requests.request("GET", url, headers=headers, stream=True) as response:
                print(response.status_code)
                for response_line in response.iter_lines():
                    if response_line:
                        json_response = json.loads(response_line)
                        if json_response["data"]["lang"] == "ja":
                            datatime = json_response["data"]["created_at"]
                            # 初めてのデータだったら、日付とパスを入れてjsonデータを読み取る
                            # 今までの日付と違ったら、jsonデータをファイルに入れて新しいファイルからjsonデータを読み取る
                            if h != datatime[5:13]:
                                if path != 'null':
                                    write_json(d_update, path)
                                h = datatime[5:13]
                                path = "daydata/" + h + ".json"
                                if not os.path.exists(path):
                                    d_new = {"data_num": 0}
                                    write_json(d_new, path)
                                with open(path, encoding="utf-8_sig") as f:
                                    d_update = json.load(f)
                            d_data = {}
                            m = datatime[14:19]
                            for k, v in json_response["data"].items():
                                if k == "lang":
                                    continue
                                if k == "conversation_id" and json_response["data"]["id"] == v:
                                    v = -1
                                d_data[k] = v
                            # リクエスト時の時刻（日本時間）
                            d_data["requested_time"] = str(
                                datetime.datetime.now())
                            j = d_update["data_num"]
                            d_update[j] = d_data
                            d_update["data_num"] += 1
                            print('{0} {1} {2}' .format(
                                j, h, m))
                            # break  # テスト用

            if not response.status_code == 200:
                raise Exception(
                    "Request returned an error: {} {}".format(
                        response.status_code, response.text
                    )
                )
                write_json(d_update, path)
            count += 1

        except KeyboardInterrupt:
            print("Ctrl+Cで停止しました")
            write_json(d_update, path)
            break

        except Exception as e:
            print(e)
            write_json(d_update, path)
            pass

    # connect_to_endpoint(url, headers)  # テスト用　while文はコメントアウトせよ

    # timeout += 1


if __name__ == "__main__":
    main()
