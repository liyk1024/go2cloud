#!/bin/bash
# func: attach disk


DISK=/dev/vdb
LOG_FILE=$0-$(date +%F).log
OSTYPE=$(head -1 /etc/issue|awk '{print $1}')

# 如何腾讯云中转服务器为Ubuntu开启root密钥登陆
if [ ${OSTYPE} == 'Ubuntu' ];then
    sed -i 's/prohibit-password/yes/g' /etc/ssh/sshd_config
    service sshd restart
    cat /home/ubuntu/.ssh/authorized_keys > /root/.ssh/authorized_keys
fi

hash rsync
if [ $? -ne 0 ];then
apt-get update -y && apt-get install rsync -y &>>${LOG_FILE} || yum -y install rsync &>> ${LOG_FILE}
fi

attach_disk() {

fdisk ${DISK}<<EOF
n
p
1




w
EOF
mkfs.ext4 /dev/vdb1 >/dev/null
[ ! -d /data ] && mkdir /data || mount /dev/vdb1 /data
rm -rf /data/*
ls /data
[ $? -eq 0 ] && return 0 || return 1
}

attach_disk
[ $? -eq 0 ] && exit 0 || exit 1

OSTYPE = head -1 /etc/issue|awk '{print $1}'