#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : cloud_oper_test.py.py
# @Time       : 2018/11/26 9:51

import os
import sys
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from lib import cloud_oper
from lib import system_oper
from lib import mylogger
from config import settings

# user_config 字典
with open(settings.USER_CONFIG, 'r') as f:
    user_config_dict = json.load(f)

cret_file = settings.CREATE_CONFIG
cret_dictinfo = {}

with open(settings.CREATE_CONFIG, 'r') as f:
    cret_config_dict = json.load(f)

def go2tencent():
    app = cloud_oper.CloudHelper(user_config_dict)

    # 查询地域
    des_zone_result = app.des_zone()
    zone = ''
    if des_zone_result and len(des_zone_result.get('ZoneSet')) > 0:
        for zone_list in des_zone_result.get('ZoneSet'):
            if zone_list.get('ZoneState') == 'AVAILABLE':
                cret_dictinfo['Zone'] = zone_list.get('Zone')
                zone = zone_list.get('Zone')

    # 创建vpc
    cret_vpc_result = app.cret_vpc()
    vpc_id = ''
    if cret_vpc_result:
        cret_dictinfo['VpcId'] = cret_vpc_result.get('Vpc').get('VpcId')
        cret_dictinfo['VpcName'] = cret_vpc_result.get('Vpc').get('VpcName')
        vpc_id = cret_vpc_result.get('Vpc').get('VpcId')

    # 创建子网
    cret_subnet_result = app.cret_subnet(vpc_id, zone)

    if cret_subnet_result:
        cret_dictinfo['SubnetId'] = cret_subnet_result.get('Subnet').get('SubnetId')
        cret_dictinfo['CidrBlock'] = cret_subnet_result.get('Subnet').get('CidrBlock')

    # 创建安全组
    secg_id = ''
    cret_secg_ret = app.cret_secgroup()
    if cret_secg_ret:
        cret_dictinfo['SecurityGroupId'] = cret_secg_ret.get('SecurityGroup').get('SecurityGroupId')
        cret_dictinfo['SecurityGroupName'] = cret_secg_ret.get('SecurityGroup').get('SecurityGroupName')
        secg_id = cret_secg_ret.get('SecurityGroup').get('SecurityGroupId')
    # 创建安全组规则
    app.cret_sec_inpolicy(secg_id)

    app.cret_sec_outpolicy(secg_id)

    # 查询支持的实例类型
    des_insconfig_result = app.des_insconfig(zone)
    ins_type = ''
    if des_insconfig_result and len(des_insconfig_result.get('InstanceTypeConfigSet')) > 0:
        for instancetype in des_insconfig_result['InstanceTypeConfigSet']:
            if (instancetype['CPU'] == 1 and instancetype['Memory'] == 1) or (
                    instancetype['CPU'] == 1 and instancetype['Memory'] == 2):
                cret_dictinfo['InstanceType'] = instancetype['InstanceType']
                ins_type = instancetype['InstanceType']

    # 创建密钥对
    cret_keypair_result = app.cret_keypair()
    key_id = ''
    if cret_keypair_result:
        cret_dictinfo['KeyId'] = cret_keypair_result.get('KeyPair').get('KeyId')
        cret_dictinfo['KeyName'] = cret_keypair_result.get('KeyPair').get('KeyName')
        cret_dictinfo['PrivateKey'] = cret_keypair_result.get('KeyPair').get('PrivateKey')
        key_id = cret_keypair_result.get('KeyPair').get('KeyId')
    # 创建cvm实例

    print('dictinfo_dict is {}'.format(cret_dictinfo))

    cret_cvm_result = app.cret_cvm(cret_dictinfo)
    print(cret_cvm_result)

    with open(cret_file, 'w') as f:
        json.dump(cret_dictinfo, f)


def sys_scan():
    OsType, Architecture, OsVersion, ImageId, Disksize = system_oper.sys_scan()
    print(OsType,Architecture,OsVersion,ImageId,Disksize)

def upload():
    # 写入本地私钥文件
    # 写入本地私钥文件
    prikey_content = cret_config_dict.get('PrivateKey')
    prikey_name = cret_config_dict.get('KeyName')
    keydir = settings.SSH_KEY_DIR



    # 格式化脚本文件
    os_type = cret_config_dict.get('OsType')
    # 传输文件
    local_diskoper_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shell', 'disk_oper.sh')
    local_initsys_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'shell', 'sys_init.sh')
    # 上传到目标的文件
    server_diskoper_file = '/tmp/disk_oper.sh'
    server_initsys_file = '/tmp/sys_init.sh'
    # 上传脚本
    hostname = cret_config_dict.get('PublicIpAddresses')
    # 本地私钥
    keyfile = keydir + os.sep + prikey_name

    # system_oper.remote_cmd(hostname,keyfile,'/bin/bash /tmp/disk_oper.sh')
    if os_type == 'CentOS' or os_type == 'RedHatEnterpriseServer' or os_type == 'Debian':
        # 判断是否有转换工具，不存在则安装

        if system_oper.sftp_upload_file(hostname, keyfile, local_diskoper_file,
                                        server_diskoper_file) and system_oper.sftp_upload_file(hostname, keyfile,
                                                                                               local_initsys_file,
                                                                                               server_initsys_file):
            print('upload file success!')
            disk_cmd = ' '.join(
                ['ssh -o stricthostkeychecking=no -i', keyfile, hostname, '/bin/bash /tmp/disk_oper.sh'])
            disk_code = os.system(disk_cmd + "> /dev/null 2>&1")
            if disk_code == '0':
                print('operdisk success code: {}'.format(disk_code))

    elif os_type == 'Ubuntu':

        if system_oper.sftp_upload_file(hostname, keyfile, local_diskoper_file, server_diskoper_file,
                                        username='ubuntu') and system_oper.sftp_upload_file(hostname, keyfile,
                                                                                            local_initsys_file,
                                                                                            server_initsys_file,
                                                                                            username='ubuntu'):
            print('upload file success!')
            disk_cmd = ' '.join(
                ['ssh -o stricthostkeychecking=no -i', keyfile, 'ubuntu@' + hostname, 'sudo -s bash /tmp/disk_oper.sh'])
            # disk_code <class 'int'>
            disk_code = os.system(disk_cmd + "> /dev/null 2>&1")

            if disk_code == 0:
                print('operdisk success code: {}'.format(disk_code))
    else:
        'disk oper error'

    system_oper.remote_cmd(hostname,keyfile,'/bin/bash /tmp/disk_oper.sh')
def test():
    app = cloud_oper.CloudHelper(user_config_dict)

    app_id = user_config_dict.get('app_id')
    bucket_name = user_config_dict.get('bucket_name')
    while True:
        time.sleep(5)
        print("镜像上传中")
        image_url = app.get_img_url(app_id,bucket_name, '/images/go2tencent.qcow2')
        if image_url is not None:
            cret_dictinfo['ImageUrl'] = image_url
            print('镜像上传完成,获取导入镜像url:{}'.format(image_url))
            break


    # 设置导入ImageName
    cret_dictinfo['ImageName'] = user_config_dict.get('image_name')

    print('导入镜像dict:{}'.format(cret_dictinfo))
    response = app.import_img(cret_dictinfo)

    print(response)


if __name__ == '__main__':
    test()
