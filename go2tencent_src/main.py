#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : main.py
# @Time       : 2018/11/13 9:46


import os
import sys
import json
import time
import datetime

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
sys.path.append(os.path.dirname(__file__))
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



# 日志目录
log_dir = settings.LOG_DIR


def time_decorator(func):
    """
    函数运行时长装饰器
    :param func:
    :return:
    """
    def inter(*args, **kwargs):
        start_time = datetime.datetime.now()
        func(*args, **kwargs)
        delta_time = (datetime.datetime.now() - start_time).total_seconds()
        print('\033[1;33;44m{:10} function totle use time: {:10}s \033[0m'.format(func.__name__,delta_time))
        print('*' * 55)
    return inter

@time_decorator
def resource_oper(logapp):
    # 实例化对象
    # app1 = cloud_oper.CloudHelper(user_config_dict)
    app1 = cloud_oper.CloudHelper.singleton(user_config_dict)


    cret_dict1 = {}
    # 查询地域
    des_zone_result = app1.des_zone()
    zone = ''
    if des_zone_result and len(des_zone_result.get('ZoneSet')) > 0:
        for zone_list in des_zone_result.get('ZoneSet'):
            if zone_list.get('ZoneState') == 'AVAILABLE':
                zone = cret_dict1.setdefault('Zone', zone_list.get('Zone'))

        print('创建地域为:{}'.format(zone))
        logapp.info('创建地域:{}'.format(zone))

    # 创建vpc
    cret_vpc_result = app1.cret_vpc()
    vpc_id = ''
    if cret_vpc_result:
        cret_dict1['VpcName'] = cret_vpc_result.get('Vpc').get('VpcName')
        vpc_id = cret_dict1.setdefault('VpcId', cret_vpc_result.get('Vpc').get('VpcId'))
        print('创建VPC ID:{}'.format(vpc_id))
        logapp.info('创建VPC ID:{}'.format(vpc_id))

    # 创建子网
    cret_subnet_result = app1.cret_subnet(vpc_id, zone)

    if cret_subnet_result:
        cret_dict1['CidrBlock'] = cret_subnet_result.get('Subnet').get('CidrBlock')
        subnet_id = cret_subnet_result.get('Subnet').get('SubnetId')
        cret_dict1['SubnetId'] = subnet_id
        print('创建子网ID:{}'.format(subnet_id))
        logapp.info('创建子网ID:{}'.format(subnet_id))

    # 创建安全组
    secg_id = ''
    cret_secg_ret = app1.cret_secgroup()
    if cret_secg_ret:
        secg_name = cret_dict1.setdefault('SecurityGroupName',
                                             cret_secg_ret.get('SecurityGroup').get('SecurityGroupName'))
        secg_id = cret_dict1.setdefault('SecurityGroupId', cret_secg_ret.get('SecurityGroup').get('SecurityGroupId'))

        print('创建安全组名称:{}'.format(secg_name))
        print('创建安全组ID:{}'.format(secg_id))
        logapp.info('创建安全组名称:{}'.format(secg_name))
        logapp.info('创建安全组ID:{}'.format(secg_id))

    # 创建安全组入方向规则
    if app1.cret_sec_inpolicy(secg_id):
        print('创建安全组入方向规则完成!')
        logapp.info('创建安全组入方向规则完成!')
    # 创建安全组出方向规则
    if app1.cret_sec_outpolicy(secg_id):
        print('创建安全组出方向规则完成!')
        logapp.info('创建安全组出方向规则完成!')

    # 查询支持的实例类型
    des_insconfig_result = app1.des_insconfig(zone)
    ins_type = ''
    if des_insconfig_result and len(des_insconfig_result.get('InstanceTypeConfigSet')) > 0:
        for instancetype in des_insconfig_result['InstanceTypeConfigSet']:
            if (instancetype['CPU'] == 1 and instancetype['Memory'] == 1) or (
                    instancetype['CPU'] == 1 and instancetype['Memory'] == 2):
                ins_type = cret_dict1.setdefault('InstanceType', instancetype['InstanceType'])

        print('实例类型:{}'.format(ins_type))
        logapp.info('实例类型:{}'.format(ins_type))

    # 创建密钥对
    cret_keypair_result = app1.cret_keypair()

    if cret_keypair_result:
        key_name = cret_dict1.setdefault('KeyName', cret_keypair_result.get('KeyPair').get('KeyName'))
        cret_dict1['PrivateKey'] = cret_keypair_result.get('KeyPair').get('PrivateKey')
        key_id = cret_dict1.setdefault('KeyId', cret_keypair_result.get('KeyPair').get('KeyId'))
        print('密钥对KEY ID:{}'.format(key_id))
        print('密钥对名称:{}'.format(key_name))
        logapp.info('密钥对KEY ID:{}'.format(key_id))
        logapp.info('密钥对名称:{}'.format(key_name))

    with open(cret_file, 'w') as f:
        json.dump(cret_dict1, f)


@time_decorator
def instance_oper(logapp):

    with open(cret_file,'r') as f:
        cret_dict2 = json.load(f)
    # 扫描本地系统获取系统信息
    OsType, Architecture, OsVersion, ImageId, DataDisksSize,HostName= system_oper.sys_scan()
    num = 1
    while any([OsType,Architecture,OsVersion,ImageId,DataDisksSize,HostName]):
        OsType, Architecture, OsVersion, ImageId, DataDisksSize,HostName = system_oper.sys_scan()
        if all([OsType,Architecture,OsVersion,ImageId,DataDisksSize,HostName]) or num > 5:
            break
        time.sleep(5)



    InstanceName = cret_dict2.setdefault('InstanceName', ''.join(['go2tencent', '_', OsType, '_', Architecture]))

    cret_dict2['OsType'] = OsType
    cret_dict2['Architecture'] = Architecture
    cret_dict2['OsVersion'] = OsVersion
    cret_dict2['ImageId'] = ImageId
    cret_dict2['DataDisksSize'] = DataDisksSize
    cret_dict2['HostName'] = HostName

    print('实例名称:{}'.format(InstanceName))
    print('OS类型:{}'.format(OsType))
    print('Architecture:{}'.format(Architecture))
    print('OS版本:{}'.format(OsVersion))
    print('镜像ID:{}'.format(ImageId))
    print('数据盘大小:{}'.format(str(DataDisksSize)))
    print('Hostname:{}'.format(HostName))

    logapp.info('实例名称:{}'.format(InstanceName))
    logapp.info('OS类型:{}'.format(OsType))
    logapp.info('Architecture:{}'.format(Architecture))
    logapp.info('OS版本:{}'.format(OsVersion))
    logapp.info('镜像ID:{}'.format(ImageId))
    logapp.info('数据盘大小:{}'.format(str(DataDisksSize)))
    logapp.info('Hostname:{}'.format(HostName))

    # 创建cvm实例


    """
    {
        Zone: '',
        InstanceType: '',
        ImageId: '',
        DataDisksSize: '',
        VpcId: '',
        SubnetId: '',
        SecurityGroupId: '',
        InstanceName:''

    }
    """

    # app2 = cloud_oper.CloudHelper(user_config_dict)
    app2 = cloud_oper.CloudHelper.singleton(user_config_dict)

    cret_cvm_result = app2.cret_cvm(cret_dict2,InstanceName = HostName)

    cret_dict2['InstanceId'] = cret_cvm_result.get('InstanceIdSet')[0]
    instance_id = cret_cvm_result.get('InstanceIdSet')[0]
    print('创建实例完成，实例 ID:{}'.format(instance_id))
    logapp.info('创建实例完成，实例 ID:{}'.format(instance_id))

    while True:
        ip_result_list = app2.des_cvm(instance_id)['InstanceSet']
        print("正在获取中转服务器的公网IP...")

        if len(ip_result_list) != 0 and ip_result_list[0].get('PublicIpAddresses'):
            pub_ip = ip_result_list[0].get('PublicIpAddresses')[0]
            cret_dict2['PublicIpAddresses'] = pub_ip

            print('获取公网IP成功! 公网IP为:{}'.format(pub_ip))
            break
        else:
            time.sleep(6)

    with open(cret_file, 'w') as f:
        json.dump(cret_dict2, f)


@time_decorator
def disk_oper(logapp):

    with open(cret_file, 'r') as f:
        cret_dict3 = json.load(f)

    # 写入本地私钥文件
    prikey_content = cret_dict3.get('PrivateKey')
    prikey_name = cret_dict3.get('KeyName')
    keydir = settings.SSH_KEY_DIR

    if system_oper.wirte_keypair(prikey_content, prikey_name, keydir):
        print('wirte keypair success!')
        logapp.info('wirte keypair success!')


    # 格式化脚本文件
    os_type = cret_dict3.get('OsType')
    if system_oper.dos2unix_shell(os_type):
        print('dos2unix shell success!')
        logapp.info('dos2unix shell success!')

    # 传输文件
    local_diskoper_file = os.path.join(os.path.dirname(__file__), 'shell', 'disk_oper.sh')
    local_initsys_file = os.path.join(os.path.dirname(__file__), 'shell', 'sys_init.sh')
    # 上传到目标的文件
    server_diskoper_file = '/tmp/disk_oper.sh'
    server_initsys_file = '/tmp/sys_init.sh'
    # 上传脚本
    publicip = cret_dict3.get('PublicIpAddresses')
    # 本地私钥
    keyfile = keydir + os.sep + prikey_name


    # system_oper.remote_cmd(publicip,keyfile,'/bin/bash /tmp/disk_oper.sh')
    if os_type == 'CentOS' or os_type == 'RedHatEnterpriseServer' or os_type == 'Debian':
        # 判断是否有转换工具，不存在则安装
        time.sleep(4)
        my_sftp_disfunc = system_oper.sftp_upload_file(publicip, keyfile, local_diskoper_file,server_diskoper_file)
        my_sftp_sysfunc = system_oper.sftp_upload_file(publicip, keyfile, local_initsys_file, server_initsys_file)

        if my_sftp_disfunc and my_sftp_sysfunc:
            print('upload file success!')
            logapp.info('upload file success!')



        # 操作格式化挂载磁盘
        disk_cmd = ' '.join(['ssh -o stricthostkeychecking=no -i', keyfile, publicip, '/bin/bash /tmp/disk_oper.sh'])
        disk_code = os.system(disk_cmd + "> /dev/null 2>&1")
        if disk_code == 0:
            print('operdisk success code: {}'.format(disk_code))

    elif os_type == 'Ubuntu':

        my_sftp_disfunc = system_oper.sftp_upload_file(publicip, keyfile, local_diskoper_file, server_diskoper_file, username='ubuntu')
        my_sftp_sysfunc = system_oper.sftp_upload_file(publicip, keyfile, local_initsys_file,server_initsys_file, username = 'ubuntu')

        if my_sftp_disfunc and my_sftp_sysfunc:
            print('upload file success!')
            logapp.info('upload file success!')


        # 操作格式化挂载磁盘
        disk_cmd = ' '.join(['ssh -o stricthostkeychecking=no -i', keyfile, 'ubuntu@' + publicip, 'sudo -s bash /tmp/disk_oper.sh'])
        # disk_code <class 'int'>
        disk_code = os.system(disk_cmd + "> /dev/null 2>&1")

        if disk_code == 0:
            print('operdisk success code: {}'.format(disk_code))
        else:
            print('operdisk error code:{}'.format(disk_code))
    else:
        'disk oper error'

    # 写入文件
    with open(cret_file, 'w') as f:
        json.dump(cret_dict3, f)


# rsync同步数据制作镜像，上传到cos
@time_decorator
def rsycn_oper(logapp):

    with open(cret_file, 'r') as f:
        cret_dict4 = json.load(f)



    prikey_name = cret_dict4.get('KeyName')

    keydir = settings.SSH_KEY_DIR
    publicip = cret_dict4.get('PublicIpAddresses')
    keyfile = keydir + os.sep + prikey_name
    excfile = settings.RSYNC_EXC_FILE

    # 进行rsync传输数据

    if system_oper.rsync_file(publicip, keyfile,excfile):
        logapp.info('rsync complate!')

@time_decorator
def migration_cvmoper(logapp):

    with open(cret_file, 'r') as f:
        cret_dict5 = json.load(f)

    prikey_name = cret_dict5.get('KeyName')
    keydir = settings.SSH_KEY_DIR
    publicip = cret_dict5.get('PublicIpAddresses')
    keyfile = keydir + os.sep + prikey_name

    # 中转服务器安装镜像修改mbr
    try:
        #
        sysinit_cmd = ' '.join(['ssh -o stricthostkeychecking=no -i', keyfile, 'root@' + publicip, 'nohup bash /tmp/sys_init.sh &'])
        # sysinit_code <class 'int'>
        # sysinit_code = os.system(sysinit_cmd + "> /dev/null 2>&1")
        print('系统脚本开始开始执行!大约需要15分钟,请您耐心等待...')
        sysinit_code = os.popen(sysinit_cmd).readlines()[0].strip()
        if sysinit_code == '0':
            print('中转服务器安装grub,修复mbr完成!')
            logapp.info('中转服务器安装grub,修复mbr完成!')
        else:
            print(sysinit_code,type(sysinit_code))

    except Exception as e:
        print('中转服务器执行脚本操作异常! 信息:'.format(e))
        logapp.info('中转服务器执行脚本操作异常! 信息:'.format(e))

@time_decorator
def sys_img_check(logapp):

    with open(cret_file, 'r') as f:
        cret_dict5 = json.load(f)


    prikey_name = cret_dict5.get('KeyName')
    keydir = settings.SSH_KEY_DIR
    publicip = cret_dict5.get('PublicIpAddresses')
    keyfile = keydir + os.sep + prikey_name


    # 确认qemu进程已经开始
    check_num = 0
    while check_num < 3:
        check_qemu = ' '.join(['ssh -o stricthostkeychecking=no -i', keyfile, 'root@' + publicip,'ps -ef |grep qemu-img |grep -v grep |wc -l'])
        check_qemu_status = os.popen(check_qemu).readlines()[0].strip()
        if check_qemu_status == '0':
            time.sleep(2)
            print('\rchek number:{}'.format(check_num),end='')
            check_num += 1
        else:
            print('')
            break

    # 检测是否镜像制作完成
    while True:
        check_qemu = ' '.join(['ssh -o stricthostkeychecking=no -i', keyfile, 'root@' + publicip,'ps -ef |grep qemu-img |grep -v grep |wc -l'])
        check_img = ' '.join(['ssh -o stricthostkeychecking=no -i', keyfile, 'root@' + publicip,'ls /images/go2tencent.qcow2 &>/dev/null && echo 0 || echo 1'])

        qemu_status = os.popen(check_qemu).readlines()[0].strip()
        img_status = os.popen(check_img).readlines()[0].strip()

        logapp.info('镜像制作中,qemu_proc code: {},check_img code: {}'.format(qemu_status,img_status))
        time.sleep(5)
        if qemu_status == '0' and img_status == '0':
            print('镜像制作完成!')
            logapp.info('镜像制作完成!')
            break

@time_decorator
def bucket_oper(logapp):

    with open(cret_file, 'r') as f:
        cret_dict6 = json.load(f)


    prikey_name = cret_dict6.get('KeyName')
    keydir = settings.SSH_KEY_DIR
    publicip = cret_dict6.get('PublicIpAddresses')
    keyfile = keydir + os.sep + prikey_name
    # 创建bucket
    app_id = user_config_dict.get('app_id')
    bucket_name = user_config_dict.get('bucket_name')

    # 实例化对象

    # app6 = cloud_oper.CloudHelper(user_config_dict)
    app6 = cloud_oper.CloudHelper.singleton(user_config_dict)

    if app6.create_bucket(app_id,bucket_name):
        print('bucket创建完成!,bucket名称:{}'.format(bucket_name))
        logapp.info('bucket创建完成!,bucket名称:{}'.format(bucket_name))
    else:
        logapp.info(app6.create_bucket(app_id,bucket_name))

    # 执行上传命令

    transfer_path = '/data'
    pythonenv_bin = transfer_path + os.sep + os.path.join(os.path.dirname(os.path.dirname(__file__)),'go2tencent_env','bin','python')

    cos_oper_file = transfer_path + os.sep + os.path.join(os.path.dirname(__file__),'upload_image.py')


    upload_cos_cmd = ' '.join(['nohup' ,pythonenv_bin , cos_oper_file , '&'])


    # oper_disk.remote_cmd(publicip, upload_cos_cmd)
    check_img = ' '.join(['ssh -o stricthostkeychecking=no -i', keyfile, 'root@' + publicip,upload_cos_cmd])
    upload_img_code = os.system(check_img)


    if upload_img_code == 0:
        print('上传镜像任务提交完成!')
        logapp.info('上传任务提交完成!')

@time_decorator
def image_oper(logapp):
    app_id = user_config_dict.get('app_id')
    bucket_name = user_config_dict.get('bucket_name')
    with open(cret_file, 'r') as f:
        cret_dict7 = json.load(f)

    # app7 = cloud_oper.CloudHelper(user_config_dict)
    app7 = cloud_oper.CloudHelper.singleton(user_config_dict)


    while True:
        time.sleep(5)
        print("镜像上传中...")
        # region_id = user_config_dict.get('region_id')
        obj_url = app7.get_obj_url(app_id,bucket_name, '/images/go2tencent.qcow2')
        if obj_url is not None:
            obj_url_img = app7.get_obj_url(app_id,bucket_name,'/images/go2tencent.qcow2')

            # obj_url_img = ''.join(['https://', bucket_name, '-', app_id, '.cos.',region_id, '.myqcloud.com', '/images/go2tencent.qcow2'])

            cret_dict7['ImageUrl'] = obj_url_img
            print('镜像上传完成,获取导入镜像url:{}'.format(obj_url))
            logapp.info('镜像上传完成,获取导入镜像url:{}'.format(obj_url))
            break


    # 设置导入ImageName
    cret_dict7['ImageName'] = user_config_dict.get('image_name')

    with open(cret_file, 'w') as f:
        json.dump(cret_dict7, f)



@time_decorator
def upload_img(logapp):


    with open(settings.CREATE_CONFIG, 'r') as f:
        cret_dict8 = json.load(f)



    # app8 = cloud_oper.CloudHelper(user_config_dict)
    app8 = cloud_oper.CloudHelper.singleton(user_config_dict)
    print('导入镜像dict:{}'.format(cret_dict8))

    OsType = cret_dict8.get('OsType')
    # sup_imglist = app8.des_impimgos()['ImportImageOsListSupported']['Linux']
    # if OsType not in sup_imglist:
    #     OsType = 'Other Linux'
    if OsType == 'RedHatEnterpriseServer':
        OsType = 'CentOS'
        cret_dict8['OsType'] = OsType

    print('导入镜像dict:{}'.format(cret_dict8))

    ImageUrl = cret_dict8['ImageUrl']
    print('imageURL:{}'.format(ImageUrl))

    # 检查导入镜像是否提交成功
    img_num = 1
    while img_num <= 20:

        if app8.import_img(cret_dict8):
            print('')
            print('导入镜像成功,number:{}'.format(img_num))
            logapp.info('导入镜像成功!')
            break

        time.sleep(5)
        print('\rcheck image...,number:{}'.format(img_num),end='')
        logapp.info('check image...,number:{}'.format(img_num))
        img_num += 1


    # 查询导入镜像的id
    number = 1
    while True:
        image_list = app8.des_imgid()['ImageSet']
        print("\r检查镜像导入中,预计需要5分钟,请耐心等待...,chechk number:{}".format(number),end='')
        logapp.info("检查镜像导入中...")
        if len(image_list) == 0:
            time.sleep(15)
            number += 1
            continue

        for img_content in image_list:
            if img_content.get('ImageName') == user_config_dict.get('image_name'):

                ImageId = img_content.get('ImageId')
                cret_dict8['ImageId'] = ImageId
                print('获取导入镜像id:{}'.format(ImageId))
                logapp.info('获取导入镜像id:{}'.format(ImageId))
            else:
                continue
        break

    # 创建最终服务器信息

    with open(cret_file, 'w') as f:
        json.dump(cret_dict8, f)


@time_decorator
def create_tocvm(logapp):


    with open(settings.CREATE_CONFIG, 'r') as f:
        cret_dict9 = json.load(f)

    # app9 = cloud_oper.CloudHelper(user_config_dict)
    app9 = cloud_oper.CloudHelper.singleton(user_config_dict)
    print('实例创建中...')
    DiskSize = cret_dict9.get('DataDisksSize')
    InstanceName = cret_dict9.get('HostName')
    app9.cret_cvm(cret_dict9,Password='WWW.51idc.com',DiskSize = DiskSize,InstanceName=InstanceName)

    with open(cret_file, 'w') as f:
        json.dump(cret_dict9, f)


@time_decorator
def clean_env(logapp):
    # 实例化对象

    with open(settings.CREATE_CONFIG, 'r') as f:
        cret_config_dict = json.load(f)

    # app_clean = cloud_oper.CloudHelper(user_config_dict)
    app_clean = cloud_oper.CloudHelper.singleton(user_config_dict)
    app_id = user_config_dict.get('app_id')

    bucket_name = user_config_dict.get('bucket_name')

    # 从创建字典中获取信息
    instance_id = cret_config_dict.get('InstanceId')

    securitygroup_id = cret_config_dict.get('SecurityGroupId')
    key_id = cret_config_dict.get('KeyId')
    vpc_id = cret_config_dict.get('VpcId')

    try:
        app_clean.del_cvm(instance_id)
    except Exception as e:
        print(e)

    number = 1
    while True:
        print('cvm正在退还中! instance_id: {}, check number:{}'.format(instance_id,number))
        logapp.info('cvm正在退还中! instance_id: {}'.format(instance_id))
        ins_status_list = app_clean.des_cvm_status(instance_id).get('InstanceStatusSet')
        if len(ins_status_list) == 0:
            break
        time.sleep(8)
        number += 1
    try:
        # 清理vpc
        if app_clean.del_vpc(vpc_id):
            print('删除VPC成功！VPC id:{}'.format(vpc_id))
            logapp.info('删除VPC成功！VPC id:{}'.format(vpc_id))

        # 清理安全组
        if app_clean.del_secg(securitygroup_id):
            print('删除安全组成功！SECG id:{}'.format(securitygroup_id))
            logapp.info('删除安全组成功！SECG id:{}'.format(securitygroup_id))
        # 清理ssh密钥
        if app_clean.del_keypair(key_id):
            print('删除密钥对成功！keypair id:{}'.format(key_id))
            logapp.info('删除密钥对成功！keypair id:{}'.format(key_id))
        # 删除bucket
        if app_clean.del_bucket(app_id, bucket_name):
            print('删除bucket对成功！bucket_name:{}'.format(''.join([bucket_name, '-', app_id])))
            logapp.info('删除bucket对成功！bucket_name:{}'.format(''.join([bucket_name, '-', app_id])))

    except Exception as e:
        print(e)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('usage: {} [option] ...'.format(sys.argv[0]))
        print('Options and arguments (and corresponding environment variables):')
        print('-h |    : print this help message and exit (also --help)')
        print('-run    : begin run go2tencent')
        print('-clean  : clean tencent resource')
    else:
        if sys.argv[1] == 'run':
            goto_logapp = mylogger.LogHelper('go2tencent.log', log_dir).cret_logger()
            resource_oper(goto_logapp)
            instance_oper(goto_logapp)
            disk_oper(goto_logapp)
            rsycn_oper(goto_logapp)
            migration_cvmoper(goto_logapp)
            sys_img_check(goto_logapp)
            bucket_oper(goto_logapp)
            image_oper(goto_logapp)
            time.sleep(20)
            upload_img(goto_logapp)
            time.sleep(2)
            create_tocvm(goto_logapp)

        elif sys.argv[1] == 'clean':
            # 清理云环境
            clean_logapp = mylogger.LogHelper('cleancloud.log', log_dir).cret_logger()
            clean_env(clean_logapp)
        elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
            print('usage: {} [option] ...'.format(sys.argv[0]))
            print('Options and arguments (and corresponding environment variables):')
            print('-h |    : print this help message and exit (also --help)')
            print('-run    : begin run go2tencent')
            print('-clean  : clean tencent resource')
        else:
            print('unknown option {}'.format(sys.argv[1]))
            print('Try {} -h for more information.'.format(sys.argv[0]))
