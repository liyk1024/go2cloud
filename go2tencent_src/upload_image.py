#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : upload_image.py.py
# @Time       : 2018/11/28 16:49



import os
import sys
import json
sys.path.append(os.path.dirname(__file__))
from lib import cloud_oper

from config import settings
# 用户创建信息文件名称
cret_file = settings.CREATE_CONFIG

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# user_config 字典
with open(settings.USER_CONFIG, 'r') as f:
    user_config_dict = json.load(f)

def upload_img():
    with open(cret_file, 'r') as f:
        cret_dict = json.load(f)

    app = cloud_oper.CloudHelper(user_config_dict)

    app_id = user_config_dict.get('app_id')
    bucket_name = cret_dict.get('bucket_name')
    file_name = '/images/go2tencent.qcow2'
    app.cos_upload_file(app_id,bucket_name,file_name)

if __name__ == '__main__':
    upload_img()