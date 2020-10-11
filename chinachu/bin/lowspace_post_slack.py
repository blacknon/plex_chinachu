#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psutil
import slackweb
import math
import os


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


# ==== Slack認証設定 ====
slack_webhook = os.environ['SLACK_WEBHOOK']

# ==== 変数指定 ====
target_dir = '/opt/data/recorded'

# ==== メイン処理 ====
# ディスクの情報を取得
dsk = psutil.disk_usage(target_dir)

# SlackにPOSTするメッセージを生成
slactText = '[TEST] ディスクの空き容量が減ってます'
attachments = []
attachment = {
    'color': 'warning',
    'fields': [
        {'title': 'ディスク容量', 'value': convert_size(dsk.total), 'short': "true"},
        {'title': 'ディスク使用量', 'value': convert_size(dsk.used), 'short': "true"},
        {'title': 'ディスク使用率', 'value': '{0}%'.format(
            dsk.percent), 'short': "true"}
    ]
}
attachments.append(attachment)

# SlackにPOST
slack = slackweb.Slack(url=slack_webhook)
slack.notify(
    text=slactText,
    attachments=attachments
)
