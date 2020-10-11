#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import requests
import slackweb
from datetime import datetime, date, timedelta, time, timezone


# ==== function ====
# 秒から時間を計算
def get_h_m_s(td):
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


# ==== Slack認証設定 ====
slack_webhook = os.environ['SLACK_WEBHOOK']
slack = slackweb.Slack(url=slack_webhook)

# ==== Chinachu認証情報 ====
chinachu_host = 'http://127.0.0.1:10772/api'
chinachu_user = os.environ['CHINACHU_USER']
chinachu_pass = os.environ['CHINACHU_PASS']

# ==== 変数指定 ====
delete_days_ago = 28  # 指定された日より前のデータを削除する
warning_days_ago = delete_days_ago - 1  # 警告をSlackに出す日数
JST = timezone(timedelta(hours=+9), 'JST')  # タイムゾーン指定


# 削除処理の開始についてSlackに通知
slact_text_start = '定期削除処理を開始します。{0}日以上前の録画データを削除します。'.format(delete_days_ago)
slack.notify(
    text=slact_text_start
)


# ==== メイン処理 ====
# 録画済データのjsonを取得
recorded_json = requests.get(
    chinachu_host + '/recorded.json',
    auth=(chinachu_user, chinachu_pass)
)

# jsonに変換
recorded = json.loads(recorded_json.text)

# 削除する基準日を指定
delete_datetime_ago = datetime.combine(
    date.today()-timedelta(delete_days_ago), time(0, 0), tzinfo=JST)

# 警告する基準日を指定
warning_datetime_ago = datetime.combine(
    date.today()-timedelta(warning_days_ago), time(0, 0), tzinfo=JST)


# listを作成
delete_list = []  # 削除リスト
warning_list = []  # 明日削除する予定のため警告をするリスト

# レコードごとにチェック
for d in recorded:
    record_datetime = datetime.fromtimestamp(d['end']/1000, JST)

    # 警告基準日より前、削除基準日より後のデータをlistに追加
    if record_datetime < warning_datetime_ago and record_datetime > delete_datetime_ago:
        warning_list.append(d)

    # 削除基準日より前のデータを抽出しlistに追加
    if record_datetime < delete_datetime_ago:
        delete_list.append(d)


# 削除対象データについて、Slackに通知・削除処理実行
slact_text_delete = '以下のデータを削除しました。'
delete_attachments = []
for dd in delete_list:
    # 削除処理を実施(プログラム)
    requests.delete(
        chinachu_host + '/recorded/{0}.json'.format(dd['id']),
        auth=(chinachu_user, chinachu_pass)
    )

    # 削除処理を実施(ファイル)
    requests.delete(
        chinachu_host + '/recorded/{0}/file.json'.format(dd['id']),
        auth=(chinachu_user, chinachu_pass)
    )

    # slackのattachmentを作成
    h, m, s = get_h_m_s(timedelta(seconds=int(dd['seconds'])))
    recorded_time = '{0}時間{1}分{2}秒'.format(h, m, s)
    attachment = {
        'color': '#ffc0cb',
        'fields': [
            {'title': '録画開始時刻',
             'value': datetime.fromtimestamp(
                 dd['start']/1000, JST).strftime('%Y/%m/%d %H:%M:%S'),
             'short': "true"
             },
            {'title': '録画終了時刻',
             'value': datetime.fromtimestamp(
                 dd['end']/1000, JST).strftime('%Y/%m/%d %H:%M:%S'),
             'short': "true"
             },
            {'title': 'チャンネル',
             'value': dd['channel']['name'],
             'short': "true"
             },
            {'title': 'タイトル',
             'value': dd['fullTitle'],
             'short': "true"
             },
            {'title': '再生時間',
             'value': recorded_time,
             'short': "true"
             },
        ]
    }
    delete_attachments.append(attachment)

# 録画済データのjsonをクリーンアップ
recorded_json = requests.put(
    chinachu_host + '/recorded.json',
    auth=(chinachu_user, chinachu_pass)
)

if len(delete_list) > 0:
    slack.notify(
        text=slact_text_delete,
        attachments=delete_attachments
    )


# 警告対象データについて、Slackに通知
slack_text_warning = '明日、以下のデータが削除されます。'
warning_attachments = []
for wd in warning_list:
    h, m, s = get_h_m_s(timedelta(seconds=int(wd['seconds'])))
    recorded_time = '{0}時間{1}分{2}秒'.format(h, m, s)
    attachment = {
        'color': 'warning',
        'fields': [
            {'title': '録画開始時刻',
             'value': datetime.fromtimestamp(
                 wd['start']/1000, JST).strftime('%Y/%m/%d %H:%M:%S'),
             'short': "true"
             },
            {'title': '録画終了時刻',
             'value': datetime.fromtimestamp(
                 wd['end']/1000, JST).strftime('%Y/%m/%d %H:%M:%S'),
             'short': "true"
             },
            {'title': 'チャンネル',
             'value': wd['channel']['name'],
             'short': "true"
             },
            {'title': 'タイトル',
             'value': wd['fullTitle'],
             'short': "true"
             },
            {'title': '再生時間',
             'value': recorded_time,
             'short': "true"
             },
            {'title': 'Chinachuリンク',
             'value': 'https://' + os.environ['VIRTUAL_HOST'] + '/#!/program/view/id={0}/'.format(wd['id']),
             'short': "true"
             }
        ]
    }
    warning_attachments.append(attachment)

if len(warning_list) > 0:
    slack.notify(
        text=slack_text_warning,
        attachments=warning_attachments
    )


slack_text_end = '定期削除処理が完了しました。今日の削除は{0}件、明日の削除予定は{1}件です。'.format(
    len(delete_list), len(warning_list))

slack.notify(
    text=slack_text_end
)
