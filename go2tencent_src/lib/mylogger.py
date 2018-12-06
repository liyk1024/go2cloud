#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : mylogger.py.py
# @Time       : 2018/11/26 15:47

import os
import time
import logging
import configparser

class LogHelper:
    """
    初始化logger，读取目录及文件名称
    """
    def __init__(self,logf_name,log_dir):
        self.logf_name = logf_name
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),log_dir)

    def __set_logdir(self,log_dir):
        self.log_dir = log_dir


    def cret_logger(self):
        """
        # 创建logger
        """
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        logtime = time.strftime('%Y-%m-%d', time.gmtime()) + '-'
        full_logf_name = logtime + self.logf_name
        full_logf_path = os.path.join(self.log_dir,full_logf_name)
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(full_logf_path)
        handler.setLevel(logging.INFO)
        formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formater)
        logger.addHandler(handler)
        return logger
