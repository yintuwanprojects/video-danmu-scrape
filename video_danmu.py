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


def write_dms_to_csv(vid, dms):
    page_url = f'https://v.qq.com/x/cover/mzc00200ivo12rf/{vid}.html'
    page_html = requests.get(page_url).content
    bs = BeautifulSoup(page_html, 'html.parser')
    title = bs.title.contents[0].split("_")[0]
    with open(f'dms/{title}_{datetime.now()}.csv', 'w') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=dms[0].keys())
        writer.writeheader()
        writer.writerows(dms)


async def main():
    vid = input('vid: ')
    is_content = input('just content?: ')
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
        write_dms_to_csv(vid, all_dms)
        return all_dms

if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    print("--- %s seconds ---" % (time.time() - start_time))
