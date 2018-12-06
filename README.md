# go2cloud_v1.0.0

## 简介
go2cloud_v1.0.0是为了用户快速的迁移其他共有云厂商实例/虚拟机/IDC物理机到腾讯云的工具。

## 安装
#### 下载
```
yum install -y git || apt-get update && apt-get install git -y
git clone https://github.com/redhatxl/go2cloud_v1.0.0.git
cd go2cloud_v1.0.0
```
#### 配置

修改文件`go2cloud_v1.0.0/go2tencent_src/config/user_config.json`
```
{
    "app_id": "1253329830",
    "secret_id": "AKIDZyGQXbErpxxxxxxxxxxxxxxxxxxxxxx",
    "secret_key": "kFUTDk38yZw4xxxxxxxxxxxxxxxxx",
    "region_id": "ap-beijing",
    "image_name": "go2tencent-img",
    "bandwidth_limit": 0,
    "bucket_name": "go2tencent"
}

```
修改内部的app_id为腾讯目的端云账号的appid
添加腾讯云目的端的secretid/secretkey

可修改：目标地域/镜像名称/bucket名称

region_id可以参考：https://cloud.tencent.com/document/product/436/6224

#### 运行
* 开始迁移
注意：如若考虑shell当前终端异常中断，请放在系统后台执行

```chmod +x go2tencent.sh && nohup ./go2tencent.sh &```

在linux终端下运行强烈建议使用screen系统下运行,以防止网络异常波动导致当前shell终端影响迁移
`go2tencent.sh`

* 清理环境:
运行```chmod +x clean.sh && nohup ./clean.sh &```

#### 登陆目的端腾讯云账号查看
* 查看迁移镜像
* 查看cos内的镜像object
* 登录系统(如果之前未安装cloud-init需要利用之前系统密码登录，安装cloud-init后可在云控制台修改密码)

## 适用

* 适用系统x86：CentOS 6.x/7.x,Ubuntu x,RedHat 6.x/7.x,Debian x
* 腾讯云ak需要具备腾讯云资源开通权限（ECS/VPC/OSS)



