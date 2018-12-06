#!/bin/bash
# func: init system

DATE=$(date +%F)
LOG=$0-$(date +%F).log

NETCONFIG_FILE=/data/etc/sysconfig/network-scripts/ifcfg-eth0
ROUTE_FILE=/data/etc/sysconfig/network-scripts/route-eth0
SYS_FSTAB=/data/etc/fstab

echo "$(date '+%F %T') - tools check" >> ${LOG}
echo "" >> ${LOG}
hash lsb_release &>/dev/null
[ $? -ne 0 ] && yum -y install redhat-lsb &>>${LOG}
[ $? -ne 0 ] && apt-get install lsb-release -y &>>${LOG}

Distributor=$(lsb_release -a | awk '/Description/{print $2}')
Release=$(lsb_release -a |awk '/Release/{print $2}' |awk -F. '{print $1}')

echo "Distributor : ${Distributor}" >>${LOG}
echo "Release : ${Release}" >>${LOG}

mbr_grub_oper() {

    # repair mbr
    echo "$(date '+%F %T') - repair mbr" >> ${LOG}
    echo "" >> ${LOG}

    dd if=/dev/vda of=/tmp/mbr${DATE}.bak bs=446 count=1 &>> ${LOG}
    dd if=/tmp/mbr${DATE}.bak of=/dev/vdb bs=446 count=1 &>> ${LOG}

    # install grub

    echo "$(date '+%F %T') - install grub " >> ${LOG}
    echo "" >> ${LOG}

    if [ ${Distributor} == "CentOS" ];then
        if [ ${Release}  == "6" ] || [ ${Release} == "5" ];then
            echo "${Distributor}${Release} recheck grub" &>>${LOG}
            echo "(hd1)	/dev/vdb" >> /data/boot/grub/device.map
            echo "${Distributor}${Release} install grub" &>>${LOG}
            grub-install  --root-directory=/data /dev/vdb &>>${LOG}
        elif [ ${Release}  == "7" ];then
            grub2-install  --root-directory=/data /dev/vdb &>>${LOG}
        else
            echo "${Distributor} ${Release} install grub fail!no support system"  >> ${LOG}
        fi
    elif [ ${Distributor} == "Ubuntu" ];then
        if [ ${Release} == "18" ] ||  [ ${Release} == "16" ];then
            echo "(hd1)	/dev/vdb" >> /data/boot/grub/device.map
            grub-install --root-directory=/data /dev/vdb &>>${LOG}
        else
            echo "${Distributor} ${Release} install grub fail!no support system"  >> ${LOG}
        fi
    elif [ ${Distributor} == "Debian" ];then
        if [ ${Release} == "9" ] ||  [ ${Release} == "8" ];then
            echo "(hd1)	/dev/vdb" >> /data/boot/grub/device.map
            grub-install --root-directory=/data /dev/vdb &>>${LOG}
        else
            echo "${Distributor} ${Release} install grub fail!no support system"  >> ${LOG}
        fi
    elif [ ${Distributor} == "openSUSE" ];then
        if [ ${Release} == "42" ];then
            grub2-install --root-directory=/data /dev/vdb &>>${LOG}
        else
            echo "${Distributor} ${Release} install grub fail!no support system"  >> ${LOG}
        fi
    elif [ ${Distributor} == "SUSE" ];then
        if [ ${Release} == "12" ];then
            grub2-install --root-directory=/data /dev/vdb &>>${LOG}
        else
            echo "${Distributor} ${Release} install grub fail!no support system"  >> ${LOG}
        fi
    else
        echo echo "install grub fail!!!!! ${Distributor} ${Release}"  >> ${LOG}
    fi
}

modify_uuid() {

# modify_uuid

echo "$(date '+%F %T') - check uuid" >> ${LOG}
echo "" >> ${LOG}

echo "$(date '+%F %T') - modify uuid" >> ${LOG}
echo "" >> ${LOG}

NEWUUID=$(blkid  /dev/vdb1 |awk -F'"' '{print $2}')

NEWTYPE=$(blkid  /dev/vdb1 |awk -F'"' '{print $(NF-1)}')
OLDTYPE=$(awk '{if($2=="/") print $3}' ${SYS_FSTAB})


if [ ${Distributor} == "CentOS" ];then
    if [ ${Release}  == "6" ] || [ ${Release} == "5" ];then
        grubfile=/data/boot/grub/grub.conf
        OLDUUID=$(grep -e "root=UUID=[[:graph:]]*" -o ${grubfile} |awk -F'=' '{print $NF}' |head -1)
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${SYS_FSTAB}
        # 修改type
        $(which sed) -i "s/${OLDTYPE}/${NEWTYPE}/g" ${SYS_FSTAB}
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${grubfile}

    elif [ ${Release} == "7" ];then
        grubfile=/data/boot/grub2/grub.cfg
        OLDUUID=$(grep -e "search --no-floppy --fs-uuid --set=root [[:alnum:]]\+" ${grubfile} |awk '{print $NF}' |head -1)
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${SYS_FSTAB}
        # 修改type
        $(which sed) -i "s/${OLDTYPE}/${NEWTYPE}/g" ${SYS_FSTAB}
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${grubfile}
    else
        echo "${Distributor} ${Release} not support,modify uuid fail!"  >> ${LOG}
    fi
elif [ ${Distributor} == "Ubuntu" ];then
    if [ ${Release} == "18" ] ||  [ ${Release} == "16" ];then
        grubfile=/data/boot/grub/grub.cfg
        OLDUUID=$(grep -e "search --no-floppy --fs-uuid --set=root [[:alnum:]]\+" ${grubfile} |awk '{print $NF}' |head -1)
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${SYS_FSTAB}
        # 修改type
        $(which sed) -i "s/${OLDTYPE}/${NEWTYPE}/g" ${SYS_FSTAB}
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${grubfile}
    else
        echo "${Distributor} ${Release} not support,modify uuid fail!"  >> ${LOG}
    fi
elif [ ${Distributor} == "Debian" ];then
    if [ ${Release} == "9" ] ||  [ ${Release} == "8" ];then
        grubfile=/data/boot/grub/grub.cfg
        OLDUUID=$(grep -e "search --no-floppy --fs-uuid --set=root [[:alnum:]]\+" ${grubfile} |awk '{print $NF}' |head -1)
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${SYS_FSTAB}
        # 修改type
        $(which sed) -i "s/${OLDTYPE}/${NEWTYPE}/g" ${SYS_FSTAB}
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${grubfile}
    else
        echo "${Distributor} ${Release} not support,modify uuid fail!"  >> ${LOG}
    fi
elif [ ${Distributor} == "openSUSE" ];then
    if [ ${Release} == "42" ];then
        grubfile=/data/boot/grub2/grub.cfg
        OLDUUID=$(grep -e "search --no-floppy --fs-uuid --set=root [[:alnum:]]\+" ${grubfile} |awk '{print $NF}' |head -1)
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${SYS_FSTAB}
        # 修改type
        $(which sed) -i "s/${OLDTYPE}/${NEWTYPE}/g" ${SYS_FSTAB}
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${grubfile}
    else
        echo "${Distributor} ${Release} not support,modify uuid fail!"  >> ${LOG}
    fi
elif [ ${Distributor} == "SUSE" ];then
    if [ ${Release} == "12" ];then
        grubfile=/data/boot/grub2/grub.cfg
        OLDUUID=$(grep -e "search --no-floppy --fs-uuid --set=root [[:alnum:]]\+" ${grubfile} |awk '{print $NF}' |head -1)
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${SYS_FSTAB}
        # 修改type
        $(which sed) -i "s/${OLDTYPE}/${NEWTYPE}/g" ${SYS_FSTAB}
        $(which sed) -i "s/${OLDUUID}/${NEWUUID}/g" ${grubfile}
    else
        echo "${Distributor} ${Release} not support,modify uuid fail!"  >> ${LOG}
    fi
else
    echo echo "grub file not find!!!!!"  >> ${LOG}
fi


echo "NEWUUID:${NEWUUID}" >> ${LOG}
echo "OLDUUID:${OLDUUID}" >> ${LOG}


grep ${NEWUUID} ${SYS_FSTAB} >> ${LOG}

grep ${NEWUUID} ${grubfile} >> ${LOG}

}


install_cos_sdk() {

# install cos sdk
echo "$(date '+%F %T') - install cos sdk" >> ${LOG}
echo "" >> ${LOG}

wget -cq -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
python /tmp/get-pip.py &>>${LOG}
pip install -U cos-python-sdk-v5 &>>${LOG}

}

make_images() {

# install cos sdk
echo "$(date '+%F %T') - make image">> ${LOG}
echo "" >> ${LOG}

[ ! -d /images ] && mkdir /images
yum -y install qemu-img wget glibc.i686 &>> ${LOG}
apt-get install qemu-utils glibc.i686 -y &>> ${LOG}
$(which qemu-img) convert -f raw  -O qcow2 /dev/vdb /images/go2tencent.qcow2

if [ $? -eq 0 ];then
    echo "0"
else
    echo "1"
fi
}

config_network() {

# config network
echo "$(date '+%F %T') - config network">> ${LOG}
echo "" >> ${LOG}

if [ ${Distributor} == "CentOS" ];then
   if [ ${Release}  == "6" ] || [ ${Release} == "5" ];then
        echo "${Distributor} ,${Release}" >> ${LOG}

# 配置网卡
cat > ${NETCONFIG_FILE} <<EOF
# Created by cloud-init on instance boot automatically, do not edit.
#
BOOTPROTO=dhcp
DEVICE=eth0
#HWADDR=52:54:00:6f:1b:62
NM_CONTROLLED=no
ONBOOT=yes
TYPE=Ethernet
USERCTL=no
PERSISTENT_DHCLIENT=yes
EOF

# 配置路由
cat > ${ROUTE_FILE} <<EOF
# Created by cloud-init on instance boot automatically, do not edit.
#
ADDRESS0=0.0.0.0
GATEWAY0=192.168.0.1
NETMASK0=0.0.0.0
EOF

   elif [ ${Release} == "7" ];then
cat > ${NETCONFIG_FILE} <<EOF
# Created by cloud-init on instance boot automatically, do not edit.
#
BOOTPROTO=dhcp
DEVICE=eth0
#HWADDR=52:54:00:6f:1b:62
NM_CONTROLLED=no
ONBOOT=yes
TYPE=Ethernet
USERCTL=no
PERSISTENT_DHCLIENT=yes
EOF


cat > ${ROUTE_FILE} <<EOF
# Created by cloud-init on instance boot automatically, do not edit.
#
ADDRESS0=0.0.0.0
GATEWAY0=192.168.0.1
NETMASK0=0.0.0.0
EOF


   else
        echo "${Distributor} ${Release} network config fail!"  >> ${LOG}
   fi
elif [ ${Distributor} == "SUSE" ];then
    echo ""
else
    echo echo "config network fail!!!!! ${Distributor} ${Release}"  >> ${LOG}
fi

}



main() {

mbr_grub_oper
modify_uuid
config_network
#install_cos_sdk
make_images

}

main