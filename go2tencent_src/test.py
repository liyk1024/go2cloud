#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : main.py
# @Time       : 2018/11/13 9:46


import os
import sys
import json


from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
sys.path.append(os.path.dirname(__file__))
print(sys.path)
from lib import cloud_oper
from lib import system_oper
from lib import mylogger
from config import settings

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# user_config 字典
with open(settings.USER_CONFIG, 'r') as f:
    user_config_dict = json.load(f)

# 用户创建信息文件名称
cret_file = settings.CREATE_CONFIG

if __name__ == '__main__':
    app = cloud_oper.CloudHelper(user_config_dict)
    result = app.des_imgid(imghub_type = 'PUBLIC_IMAGE')

    print(result['ImageSet'])

    # result = dict1.get('ImageName').split('.')[0].strip().split()[-1]
    # print(result)

