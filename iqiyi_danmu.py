import os
import requests
import xmltodict
import csv
import json
import bs4
from math import ceil
from datetime import datetime
from zlib import decompress


def get_tvid_duration_title(html_url):
    print("--- Fetching TVID and Duration ---")
    r = requests.get(html_url)
    soup = bs4.BeautifulSoup(r.content, 'html.parser')
    script_html = list(filter(lambda a: "window.QiyiPlayerProphetData" in a.text, soup.findAll('script')))[0]
    vid_script = json.loads(script_html.text.split("window.QiyiPlayerProphetData=")[1])
    tvid = str(vid_script['tvid'])
    video_duration = vid_script['a']['data']['showResponse']['videoInfo']['videoDuration']
    tl = vid_script['a']['data']['originRes']['vdi']['tl']
    print("--- DONE ---")
    return {'tvid': tvid, 'duration': video_duration, 'title': tl}


def get_iqiyi_danmus(vid, duration):
    print("--- Fetching Danmu ---")
    i_length = ceil(duration/300)  # iteration count for 300 second intervals
    dms = []
    for i in range(1, i_length+1):
        i_url = f"https://cmts.iqiyi.com/bullet/{vid[-4:-2]}/{vid[-2:]}/{vid}_300_{i}.z"
        try:
            dm_raw = requests.get(i_url).content
            dm_dc = decompress(dm_raw)
            dm = xmltodict.parse(dm_dc)['danmu']['data']['entry']
            for entry in dm:
                if not entry['list']:
                    continue
                if isinstance(entry['list']['bulletInfo'], dict):
                    record = [entry['list']['bulletInfo']]
                else:
                    record = entry['list']['bulletInfo']
                record = [{
                    'contentId': a['contentId'],
                    'content': a['content'],
                    'showTime': a['showTime'],
                    'likeCount': a['likeCount'],
                    'plusCount': a['plusCount'],
                    'dissCount': a['dissCount'],
                    'replyCount': a['replyCnt'],
                    'userName': a['userInfo']['name'],
                    'userUid': a['userInfo']['uid']
                } for a in record]
                dms = dms + record
        except Exception:
            print(f"*** ERROR: Could not get valid request for {i_url} ***")
    print("--- DONE ---")
    return dms


def write_danmu_to_file(danmus, filename):
    if not os.path.exists(f'dms/iqiyi/'):
        os.makedirs(f'dms/iqiyi/')
        print(f'--- New Folder dms/iqiyi/ Created ---')
    print(f"--- Writing to file {filename} ---")
    with open(f'dms/iqiyi/{filename}_{datetime.now()}.csv', 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=danmus[0].keys())
        writer.writeheader()
        writer.writerows(danmus)
    print("--- DONE ---")


if __name__ == '__main__':
    print("====== STARTING IQIYI DANMU EXTRACT PROCESS ======")
    index = 1
    url = input('video url: ')
    tvid_duration_title = get_tvid_duration_title(url)
    danmu = get_iqiyi_danmus(tvid_duration_title['tvid'], tvid_duration_title['duration'])
    title = tvid_duration_title['title']
    write_danmu_to_file(danmu, title)
    print("====== END PROCESS ======")
