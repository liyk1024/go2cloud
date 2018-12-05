#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : system_oper.py
# @Time       : 2018/11/13 9:47

import os
import paramiko
import platform
from psutil import disk_usage
import time
from math import ceil
from re import findall
import socket


def func_retry(user_fun,retry_totle=6,sleep_time = 4):
    """
    函数重试次数装饰器
    :param user_fun:
    :param retry_totle:
    :param sleep_time:
    :return:
    """
    def inter(*args,**kwargs):
        retry_num = 0
        while retry_num < retry_totle:
            if user_fun(*args,**kwargs):
                print('{} complate!'.format(user_fun.__name__))
                return True
            print('{} retry!, count:{}'.format((user_fun.__name__), retry_num))
            time.sleep(sleep_time)
            retry_num += 1
    return inter

@func_retry
def rsync_file(hostname,keyfile,excfile,username = 'root'):
    """
    通过密钥进行rsync文件
    '`which rsync` -e "ssh -i /root/.ssh/id_rsa -o stricthostkeychecking=no" -avtzP --exclude-from=RSYNC_EXC_FILE / root@192.0.0.1:/data'
    :param hostname:
    :param keyfile:
    :param username:
    :param excfile:
    :return:
    """
    # 目的 'root@127.0.0.1:/data'
    des = ''.join([username,'@',hostname,':/data'])
    # ssh参数 "ssh -i /root/.ssh/id_rsa -o stricthostkeychecking=no"
    ssh_argv = '"' + 'ssh -i ' + keyfile + ' -o stricthostkeychecking=no' + '"'
    # '`which rsync` -e "ssh -i /root/.ssh/id_rsa -o stricthostkeychecking=no" -avtzP --exclude-from=RSYNC_EXC_FILE / root@192.0.0.1:/data'
    rsync_cmd = ' '.join(['`which rsync` -e',ssh_argv,'-avtzP --exclude-from=' + excfile,'/',des])
    print('rsync_cmd:{}'.format(rsync_cmd))
    # subprocess.Popen(cmd, shell=True)
    rsync_code = os.system(rsync_cmd)
    if rsync_code == 0:
        print('rsync file success!')
        return True


def wirte_keypair(prikey_content, prikey_name, keydir):
    """
    写入本地私钥
    :param prikey_content:
    :param prikey_name:
    :param keydir:
    :return:
    """
    # 创建目录
    prikey_file = keydir + os.sep + prikey_name
    if not os.path.exists(keydir):
        os.makedirs(keydir)
    # 写入私钥
    if not os.path.exists(prikey_file):
        with open(prikey_file, 'w') as f:
            f.write(prikey_content)
    else:
        with open(prikey_file, 'w') as f:
            f.write(prikey_content)
    if os.system(' '.join(['chmod', '600', prikey_file])) == 0:
        return True
    else:
        return False


# 返回
def __get_disksize(disksize):
    result_disksize = ''
    if disksize % 10 == 0:
        result_disksize = disksize
    else:
        for i in range(1,10):
            disksize += 1
            if disksize % 10 == 0:
                result_disksize = disksize
    return result_disksize


def remote_cmd(hostname, keyfile, cmd, port=22, username='root', timeout=60):
    """
    执行远程命令
    :param hostname:
    :param cmd:
    :param keyfile:
    :param port:
    :param username:
    :param timeout:
    :return:
    """
    # rsa_key = '/root/.ssh/id_rsa_go2tencent'
    rsa_key = keyfile
    private_key = paramiko.RSAKey.from_private_key_file(rsa_key)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, port=port, username=username, pkey=private_key)

        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        stdout_result = stdout.read()
        stderr_result = stderr.read()
        print("normal info:", stdout_result.decode())
        print("normal info:", stderr_result.decode())
        ssh.close()
        return stdout
    except Exception as err:
        print(err)

@func_retry
def sftp_upload_file(hostname, keyfile, local_path, server_path, username='root', port=22):
    """
    上传文件
    :param hostname:
    :param keyfile:
    :param local_path:
    :param server_path:
    :param port:
    :return:
    """
    rsa_key = keyfile

    private_key = paramiko.RSAKey.from_private_key_file(rsa_key)
    transport = paramiko.Transport((hostname, port))
    try:
        transport.connect(username=username, pkey=private_key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, server_path)
        # 判断文件是否存在
        if sftp.file(server_path):
            transport.close()
            return True
    except Exception as e:
        print(e)


def sys_scan():
    """
    sanc local system
    "OsVersion":7,
    "OsType": "CentOS",
    "Architecture": "x86_64",
    :return:OsType,Architecture,OsVersion,ImageId
    """
    OsType, OsVersion, Architecture = '', '', ''
    print('检查软件rsync/lsb_release')
    os.system('yum -y install rsync redhat-lsb' + "> /dev/null 2>&1" )
    os.system('apt-get update &>/dev/null && apt-get install rsync lsb-release -y '+ "> /dev/null 2>&1")
    time.sleep(5)
    cmd_code = os.system('hash lsb_release'+ "> /dev/null 2>&1")

    if cmd_code != 0:
        os_type = platform.linux_distribution()[0].split()[0]
        if os_type == 'CentOS' or os_type == 'Red':
            os.system('yum -y install redhat-lsb'+ "> /dev/null 2>&1" )
        elif os_type == 'debian':
            os.system('sudo apt-get update && sudo apt-get install lsb-release -y'+ " > /dev/null 2>&1")
        else:
            print('system install lsb-release error')
    elif cmd_code == 0:
        # 获取系统类型
        OsType = os.popen('lsb_release -a').read().split('\n')[1].split('\t')[-1].split()[0]
        # 获取系统版本
        OsVersion = findall('(\d+)', os.popen('lsb_release -a').read().split('\n')[2].split('\t')[1])[0]
    else:
        print('occer error,code:{}'.format(cmd_code))

    # 获取架构
    Architecture = platform.uname().machine

    # 获取数据盘大小
    datadiskssize = ceil(disk_usage('/').total / 1024 / 1024 / 1024 + 1)
    DataDisksSize = 50 if datadiskssize < 50 else __get_disksize(datadiskssize) + 10

    # 中转服务器的镜像
    ImageId = ''
    if OsType == 'CentOS' or OsType == 'RedHatEnterpriseServer':
        if OsVersion == '7':
            # CentOS 7.3 64位
            ImageId = 'img-dkwyg6sr'

        elif OsVersion == '6':
            if Architecture == 'i386':
                # CentOS 6.9 32位
                ImageId = 'img-060ov1xz'

            else:
                # CentOS 6.9 64位
                ImageId = 'img-jhhcsd4h'
        else:
            'occer error, OsType:{} , OsVersion:{}'.format(OsType, OsVersion)
    elif OsType == 'Ubuntu':
        if Architecture == 'i386':
            # Ubuntu Server 16.04.1 LTS 32位
            ImageId = 'img-8u6dn6p1'
        else:
            # Ubuntu Server 16.04.1 LTS 64位
            ImageId = 'img-pyqx34y1'

    elif OsType == 'Debian':
        if Architecture == 'i386':
            # Debian 8.2 32位
            ImageId = 'img-ez7jwngr'
        else:
            # Debian 8.2 64位
            ImageId = 'img-hi93l4ht'
    else:
        'occer error, OsType:{} , OsVersion:{}'.format(OsType, OsVersion)

    HostName = socket.gethostname()

    return OsType, Architecture, OsVersion, ImageId, DataDisksSize, HostName


def dos2unix_shell(ostype, shell_dir='shell', **kwargs):
    """
    进行shell脚本文件转化格式
    :param ostype:
    :param shell_dir:
    :param kwargs:
    :return:
    """
    shell_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), shell_dir)
    # 判断系统版本进行本地shell脚本转换
    if ostype == 'CentOS' or ostype == 'RedHatEnterpriseServer':
        # 判断是否有转换工具，不存在则安装
        cmd_code = os.system('hash dos2unix &>/dev/null')
        if cmd_code != 0:
            install_cmd = kwargs.get('cmd') if kwargs.get('cmd') else 'yum -y install dos2unix'
            install_code = os.system(install_cmd + "> /dev/null 2>&1")
            print('install {} success! status_code : {}'.format('dos2unix', install_code))
            if install_code == 0:
                # dos2unix_code = os.system('`which dos2unix` ' + shell_file + '/*')
                dos2unix_code = os.system(' '.join(['`which dos2unix`', shell_file + '/*']) + "> /dev/null 2>&1")
                if dos2unix_code == 0:
                    print('dos2unix {} success! status_code : {}'.format(shell_file + '/*', dos2unix_code))
                    return True
        elif cmd_code == 0:
            # 进行shell脚本转换
            dos2unix_code = os.system(' '.join(['`which dos2unix`', shell_file + '/*']) + "> /dev/null 2>&1")
            if dos2unix_code == 0:
                print('dos2unix {} success! status_code : {}'.format(shell_file + '/*', dos2unix_code))
                return True
        else:
            print('dos2unix error')

    elif ostype == 'Ubuntu' or ostype == 'Debian':
        cmd_code = os.system('hash fromdos'+ "> /dev/null 2>&1" )
        if cmd_code != 0:
            install_cmd = kwargs.get('cmd') if kwargs.get('cmd') else 'sudo apt-get install tofrodos -y &>/dev/null'
            install_code = os.system(install_cmd)
            if install_code == 0:
                dos2unix_code = os.system(' '.join(['sudo', '`which fromdos`', shell_file + '/*']) + "> /dev/null 2>&1")
                if dos2unix_code == 0:
                    print('fromdos {} success! status_code : {}'.format(shell_file + '/*', dos2unix_code))
                    return True

        elif cmd_code == 0:

            # 进行shell脚本转换
            dos2unix_code = os.system(' '.join(['sudo', '`which fromdos`', shell_file + '/*']) + "> /dev/null 2>&1")
            if dos2unix_code == 0:
                print('fromdos {} success! status_code : {}'.format(shell_file + '/*', dos2unix_code))
                return True

        else:
            print('fromdos error')
    else:
        print('{} is not support do2unix'.format(ostype))
