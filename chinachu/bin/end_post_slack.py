#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 録画結果の内容について雑にSlackにPostするスクリプト(option化もめんどくさいくらいなのでこのまま使ってる)

import sys
import os
import re
import math
import slackweb
import ffmpeg
import datetime
from imgurpython import ImgurClient


# ==== function ====
# ファイルサイズの変換用関数
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


# 秒から時間を計算
def get_h_m_s(td):
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


# ==== Slack認証設定 ====
slack_webhook = os.environ['SLACK_WEBHOOK']

# ==== Imgur認証設定 ====
imgur_id = os.environ['IMGUR_ID']
imgur_secret = os.environ['IMGUR_SECRET']

# ==== 変数指定 ====
# 録画したデータの置き場所
recorded_dir = "/usr/local/chinachu/recorded/"
# thumbnail画像のPATH(めんどいからここで指定)
thumbnail_path = "/usr/local/chinachu/recorded/thumbnail.jpg"

# ==== メイン処理 ====
# 環境変数PATHにffmpeg等が含まれているDirectoryを追加
os.environ['PATH'] = os.environ['PATH'] + ":/usr/local/chinachu/usr/bin"

# 引数から要素を取得する
file_path = recorded_dir + sys.argv[1]
file_name = re.split('\]|\[', sys.argv[1], 6)
recorded_channel = file_name[3]
recorded_id = file_name[5]
recorded_title = file_name[6].split('.')[0]

# ファイルサイズを取得
recorded_size = os.path.getsize(file_path)

# 動画ファイルから要素を取得する
recorded_probe = ffmpeg.probe(file_path)
recorded_duration = recorded_probe['streams'][0]['duration']

# サムネイルファイルをimgurにアップロード
imgur = ImgurClient(imgur_id, imgur_secret)
recorded_image_url = imgur.upload_from_path(
    thumbnail_path, config=None, anon=True)

print(recorded_image_url)

# 動画の時間を計算
h, m, s = get_h_m_s(datetime.timedelta(seconds=float(recorded_duration)))
recorded_time = '{0}時間{1}分{2}秒'.format(h, m, s)

# SlackにPOSTするメッセージを生成
slact_text = 'Chinachuでの録画が終了しました。'
attachments = []
attachment = {
    'color': 'good',
    "image_url": recorded_image_url['link'],
    'fields': [
        {'title': 'チャンネル', 'value': recorded_channel, 'short': "true"},
        {'title': '番組名', 'value': recorded_title, 'short': "true"},
        {'title': 'ファイルサイズ',
         'value': convert_size(recorded_size),
         'short': "true"},
        {'title': '動画時間',
         'value': recorded_time,
         'short': "true"},
        {'title': 'Chinachuリンク',
         'value': 'https://' + os.environ['VIRTUAL_HOST'] + '/#!/program/view/id={0}/'.format(recorded_id),
         'short': "true"},
        {'title': 'Samba path',
         'value': 'smb://' + os.environ['VIRTUAL_HOST'] + '/Public/{0}'.format(sys.argv[1]),
         'short': "true"},
    ]
}
attachments.append(attachment)

# SlackにPOST
slack = slackweb.Slack(url=slack_webhook)
slack.notify(
    text=slact_text,
    attachments=attachments
)
