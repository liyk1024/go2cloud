#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : settings.py.py
# @Time       : 2018/11/26 9:47

import os
import sys

# 用户配置json文件
USER_CONFIG = os.path.join(os.path.dirname(__file__),'user_config.json')

# 创建完成生成的json文件

CREATE_CONFIG = os.path.join(os.path.dirname(__file__),'create_info.json')


# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),'logs')

# ssh密钥目录
SSH_KEY_DIR = '/root/.ssh'


# rsync excludes文件
RSYNC_EXC_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)),'excludes','rsync_excludes_linux.txt')