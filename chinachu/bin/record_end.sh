#!/bin/bash

# 変数
recorded_dir="/usr/local/chinachu/recorded/"                # 録画したデータの置き場所
tmp_ts_file="${@##*\"recorded\":\"}.m2ts}"                  # 録画したtsファイル名(加工用)
ts_file="${tmp_ts_file%%.m2ts*}.m2ts"                       # 録画したtsファイル名
ts_dir="${AMATSUKAZE_SRC_DIR}"                              # Windows側から見たTSファイルの配置ディレクトリ
amatsukaze_host="${AMATSUKAZE_HOST}"                        # Amatsukazeを稼働しているWindowsマシンのホスト名(IPアドレス)
amatsukaze_port="32768"                                     # Amatsukazeを稼働しているWindowsマシンのport
amatsukaze_path="${AMATSUKAZE_PATH}"                        # Windows上でAmatsukazeの配置されているPATH
output_dir="${AMATSUKAZE_DST_DIR}"                          # CMカット・エンコードしたファイルの出力先PATH
ffmpeg_path="/usr/local/chinachu/usr/bin/ffmpeg"            # ffmpegのPATH
thumbnail_path="/usr/local/chinachu/recorded/thumbnail.jpg" # 生成するサムネイル画像のPATH(めんどいから決め打ち)

# SlackにPOSTするためのサムネイル生成
echo $(date "+%Y/%m/%d %H:%M:%S ")"${ts_file} サムネイル生成" >>/tmp/a.log
"${ffmpeg_path}" -y -i "${ts_file}" -ss 30 -t 1 -r 1 -s 1280x720 "${thumbnail_path}" 2>&1 >>/tmp/a.log

# SlackにPOST
echo $(date "+%Y/%m/%d %H:%M:%S ")"${ts_file} SlackにPOST" >>/tmp/a.log
/usr/local/chinachu/bin/end_post_slack.py "$(basename "${ts_file}")" 2>&1 >>/tmp/a.log

# サムネイルの削除
echo $(date "+%Y/%m/%d %H:%M:%S ")"${ts_file} サムネイル削除" >>/tmp/a.log
rm "${thumbnail_path}"

# Amatsukazeに変換対象を追加
echo Amatsukazeに追加 >>/tmp/a.log
mono /usr/local/chinachu/Amatsukaze/AmatsukazeAddTask.exe \
    -f "${ts_file}" \
    -ip "${amatsukaze_host}" \
    -p "${amatsukaze_port}" \
    --remote-dir "${ts_dir}" \
    -s "デフォルト" \
    --priority 2 \
    --no-move \
    -r "${amatsukaze_path}" \
    -o "${output_dir}"
