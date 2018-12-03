# -*- coding: utf-8 -*-
# 爬取头条街拍的图片，存到相应的文件中

import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool


# url: https://www.toutiao.com/search_content/?offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&cur_tab=1&from=search_tab
def get_page(offset):
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }
    # urlencode():将params中的内容转为：offset=0&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20&cur_tab=1&from=search_tab这种格式
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)  # 请求页面
        if response.status_code == 200:  # 成功
            return response.json()  # 返回获取到的json数据
        return None  # 否则返回None
    except requests.ConnectionError:
        return None


# 获取图片的链接和标题
def get_images(json):
    if json.get('data'):  # 判断是否存在data项
        for item in json.get('data'):
            if item.get('title') and item.get('image_list'):  # 防止有空项，返回NoneType
                title = item.get('title')  # 标题
                images = item.get('image_list')  # 图片的链接
                for image in images:  # 构造一个生成器
                    yield {
                        'image_url': 'http:' + image.get('url'),
                        'title': title
                    }


# 保存图片
def save_image(item):
    if not os.path.exists(item.get('title')):  # 如果还不存在该文件夹
        os.mkdir(item.get('title'))  # 则创建相应的文件夹
    try:
        response = requests.get(item.get('image_url'))  # 根据url,请求相应的图片
        if response.status_code == 200:  # 请求成功
            file_path = '{0}/{1}.{2}'.format(item.get('title'), md5(response.content).hexdigest(), 'jpg')  # 文件路径，使用md5，去除重复图片
            if not os.path.exists(file_path):  # 如果不存在该文件路径
                with open(file_path, 'wb') as f:  # 以二进制形式写入文件
                    f.write(response.content)
            else:
                print("Already Downloaded", file_path)  # 已经下载过
    except requests.ConnectionError:  # 请求连接错误
        print('Failed to save image')


def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        save_image(item)


GROUP_START = 1
GROUP_END = 20

if __name__ == "__main__":
    groups = ([x*20 for x in range(GROUP_START, GROUP_END+1)])
    pool = Pool()
    pool.map(main, groups)
    pool.close()
    pool.join()