# 视频平台弹幕提取
* 支持平台（仅大陆版URL）
  * 腾讯视频 Tencent Video
  * 爱奇艺 iQiyi
* 需要Python 3.9
* 需要指令行

## 安装
1. 下载本项目`git clone https://github.com/yintuwanprojects/video-danmu-scrape.git`
2. 安装必要模块`pip3 install -r requirements.txt`

## 运行

### 腾讯视频
由于腾讯弹幕分段较多，请求发送是批量异步运行，请确保你的python版本支持asyncio
1. 进入根目录，在指令行中运行`python3 tencent_danmu.py`
2. 根据以下提示，在指令行中输入选项：
   * `run list?` 是否读取列表
     * `yes`:  
       * `file name: ` 输入在`series_list`目录下的文件名，例如`list1.txt`
     * `no`:
       * `video url: ` 输入单个视频URL，例如`https://v.qq.com/x/cover/mzc00200t7i1qwp/g0046in1rjb.html`
   * `is variety?: ` 视频是否为综艺，输入`yes`或者`no`
   * `just content?: ` 是否仅提取弹幕文字内容，输入`yes`或者`no`
3. 文件保存在根目录的`dms`文件夹里以视频系列命名的子文件夹内

### 爱奇艺
爱奇艺的弹幕请求返送为.z压缩包格式，需用zlib解压后方可读取
1. 进入根目录，在指令行中运行`python3 iqiyi_danmu.py`
2. 在指令行中输入答复
   * `video url: ` 输入视频URL，例如`https://www.iqiyi.com/v_20z4r9gvvko.html`
3. 文件保存在根目录的`iqiyi`文件夹里
