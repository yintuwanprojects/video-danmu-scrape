import os.path
import requests
import aiohttp
import asyncio
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup


async def get_dm_seg(session, url):
    print(f'getting dms: {url}')
    async with session.get(url) as resp:
        dm_seg = await resp.json()
        barrage_list = dm_seg['barrage_list']
        new_list = [
            {
                "id": dm['id'],
                "nickname": dm['nick'],
                "content": dm['content'],
                "time_offset": dm['time_offset'],
                "up_count": dm['up_count'],
                "create_time": dm['create_time']
            } for dm in barrage_list
        ]
        return sorted(new_list, key=lambda a: a['time_offset'])


async def get_dm_content(session, url):
    print(f'getting dms: {url}')
    async with session.get(url) as resp:
        dm_seg = await resp.json()
        barrage_list = dm_seg['barrage_list']
        new_list = [
            {'content': dm['content']} for dm in barrage_list
        ]
        return new_list


def write_dms_to_csv(vid, dms, is_var):
    page_url = f'https://v.qq.com/x/cover/mzc00200t7i1qwp/{vid}.html'
    r = requests.get(page_url)
    while not r.ok:
        print('... Fetching page HTML ...')
    page_html = r.content
    bs = BeautifulSoup(page_html, 'html.parser')
    title = bs.title.contents[0].split("_")[0]
    if is_var:
        folder_name = title.split("《")[1].split("》")[0]
    else:
        folder_name = title
    if not os.path.exists(f'dms/{folder_name}'):
        os.makedirs(f'dms/{folder_name}')
        print(f'--- New Folder dms/{folder_name} Created ---')
    with open(f'dms/{folder_name}/{title}_{datetime.now()}.csv', 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=dms[0].keys())
        writer.writeheader()
        writer.writerows(dms)


async def get_series_danmu():
    list_name = input('file name: ')
    is_variety = input('is variety?: ')
    is_variety = is_variety.lower() == 'yes'
    with open(f'series_list/{list_name}', 'r') as f:
        video_list = f.read().splitlines()
        video_list = list(filter(lambda a: not "#" == a[0], video_list))
    is_content = input('just content?: ')
    for url in video_list:
        vid = url.split("/")[-1].split(".")[0]
        print(f'--- Getting danmus for {vid} ---')
        seg_index_url = f'https://dm.video.qq.com/barrage/base/{vid}'
        r = requests.get(seg_index_url)
        segment_index = r.json()['segment_index']
        url_prefix = f'https://dm.video.qq.com/barrage/segment/{vid}/'
        url_list = [url_prefix + seg['segment_name'] for index, seg in segment_index.items()]
        async with aiohttp.ClientSession() as session:
            tasks = []
            if is_content == 'yes':
                for url in url_list:
                    tasks.append(asyncio.ensure_future(get_dm_content(session, url)))
            else:
                for url in url_list:
                    tasks.append(asyncio.ensure_future(get_dm_seg(session, url)))

            dms_seg_list = await asyncio.gather(*tasks)
            all_dms = []
            for dms_seg in dms_seg_list:
                all_dms = all_dms + dms_seg
            write_dms_to_csv(vid, all_dms, is_variety)
            print(f'--- Finished collection for {vid} ---')
    return 0


async def main():
    vid = input('video url: ').split("/")[-1].split(".")[0]
    is_variety = input('is variety?: ')
    is_variety = is_variety.lower()[0] == 'y'
    is_content = input('just content?: ').lower()[0] == 'y'
    seg_index_url = f'https://dm.video.qq.com/barrage/base/{vid}'
    r = requests.get(seg_index_url)
    segment_index = r.json()['segment_index']
    url_prefix = f'https://dm.video.qq.com/barrage/segment/{vid}/'
    url_list = [url_prefix + seg['segment_name'] for index, seg in segment_index.items()]

    async with aiohttp.ClientSession() as session:
        tasks = []
        if is_content == 'yes':
            for url in url_list:
                tasks.append(asyncio.ensure_future(get_dm_content(session, url)))
        else:
            for url in url_list:
                tasks.append(asyncio.ensure_future(get_dm_seg(session, url)))

        dms_seg_list = await asyncio.gather(*tasks)
        all_dms = []
        for dms_seg in dms_seg_list:
            all_dms = all_dms + dms_seg
        write_dms_to_csv(vid, all_dms, is_variety)
        return all_dms

if __name__ == '__main__':
    start_time = time.time()
    run_list = input('run list? ').lower()[0] == 'y'
    if run_list:
        asyncio.run(get_series_danmu())
    else:
        asyncio.run(main())
    print("--- %s seconds ---" % (time.time() - start_time))
