#!/bin/env python
# -*- coding:utf-8 -*-
# @Author     : kaliarch
# @File       : cloud_oper.py
# @Time       : 2018/11/13 9:46
import time

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client
from tencentcloud.cvm.v20170312 import models as cvm_models
from tencentcloud.vpc.v20170312 import vpc_client
from tencentcloud.vpc.v20170312 import models as vpc_models

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import json
import random
import os
import subprocess
import string
import sys


class CloudHelper(object):

    def __init__(self, config_dict):
        """
        读取配置文件，初始化变量
        config_dict:
            {
                "app_id": "1253329830",
                "secret_id": "AKIDZyGQXbErpY4MPDl7D4xxxxxxxxxxxxxxx",
                "secret_key": "kFUTDk38yZw4xc5JHzRdZFxxxxxxxxxx",
                "region_id": "ap-beijing",
                "image_name": "go2tencent-img",
                "system_disk_size": 50,
                "OsVersion":7,
                "OsType": "CentOS",
                "Architecture": "x86_64",
                "data_disks": [],
                "bandwidth_limit": 0,
                "bucket_name": "go2tencent"
            }
        """
        # 读入客户预定于的配置文件
        if isinstance(config_dict, dict) and len(config_dict.keys()) != 0:
            self.config_dict = config_dict
        else:
            print('input dict error! config_dict: {}'.format(config_dict))

        # 定义随机字符串
        self.random_char = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(5))

        try:
            # 实例化一个认证对象
            cred = credential.Credential(self.config_dict.get('secret_id'), self.config_dict.get('secret_key'))
            # 实例化cvm的client对象
            self.cvm_helper = cvm_client.CvmClient(cred, self.config_dict.get('region_id'))
            # 实例化vpc的client对象
            self.vpc_helper = vpc_client.VpcClient(cred, self.config_dict.get('region_id'))

            # 实例化cos对象
            cos_config = CosConfig(Appid=config_dict.get('app_id'), Region=config_dict.get('region_id'),
                                   Secret_id=config_dict.get('secret_id'),
                                   Secret_key=config_dict.get('secret_key'))
            # 实例化cos的client对象
            self.cos_helper = CosS3Client(cos_config)

        except TencentCloudSDKException as err:
            print(err)

    # 创建目录
    # def create_logdir(self):
    #     os.path.join(os.path.dirname(__file__), self.logdir)
    #     if not os.path.exists(self.logdir):
    #         os.mkdir(self.logdir)

    # 实现单例模式

    __instance = None

    @staticmethod
    def singleton(*args,**kwargs):
        if CloudHelper.__instance:
            return CloudHelper.__instance
        else:
            CloudHelper.__instance = CloudHelper(*args,**kwargs)
            return CloudHelper.__instance


    def des_zone(self, *args):
        """
        查询可用区
        :return 查询结果字典

        """
        # 实例化cvm地域查询对象
        try:
            des_req = cvm_models.DescribeZonesRequest()
            response = self.cvm_helper.DescribeZones(des_req)
            result_content = response.to_json_string()
            return json.loads(result_content)

        except TencentCloudSDKException as err:
            print(err)

    def cret_vpc(self, **kwargs):
        """
        创建vpc
        :return 创建vpc返回结果字典

        {
          "Response": {
            "RequestId": "354f4ac3-8546-4516-8c8a-69e3ab73aa8a",
            "Vpc": {
              "CidrBlock": "10.8.0.0/16",
              "EnableMulticast": false,
              "VpcId": "vpc-4tboefn3",
              "VpcName": "TestVPC"
            }
          }
        }
        """

        cret_req = vpc_models.CreateVpcRequest()
        # 定义vpcname
        cret_req.VpcName = kwargs.get('VpcName') if kwargs.get('VpcName') else 'go2tencent-vpc-' + self.random_char

        # 定义region
        cret_req.Region = self.config_dict.get('region_id')
        # 定义cidr
        cret_req.CidrBlock = kwargs.get('CidrBlock') if kwargs.get('CidrBlock') else '192.168.0.0/16'

        try:
            response = self.vpc_helper.CreateVpc(cret_req)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)

    def cret_subnet(self, vpc_id, zone, cidrblock='192.168.0.0/24', **kwargs):
        """
        创建子网
        :param VpcId:
        :param Zone:
        :return: 创建子网的返回内容

        {
          "Response": {
            "RequestID": "354f4ac3-8546-4516-8c8a-69e3ab73aa8a",
            "Subnet": {
              "AvailableIpAddressCount": 253,
              "CidrBlock": "10.8.255.0/24",
              "IsDefault": false,
              "SubnetId": "subnet-2qhl25io",
              "SubnetName": "TestSubnet",
              "VpcId": "vpc-m3ul053f",
              "Zone": "ap-guangzhou-1"
            }
          }
        }
        """

        cret_req = vpc_models.CreateSubnetRequest()
        # vpc_id
        cret_req.VpcId = vpc_id
        # zone
        cret_req.Zone = zone
        cret_req.SubnetName = kwargs.get('SubnetName') if kwargs.get('SubnetName') else 'go2tencent-subnet-' + self.random_char

        # 定义私网地址
        cret_req.CidrBlock = cidrblock

        try:
            response = self.vpc_helper.CreateSubnet(cret_req)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)

    def cret_secgroup(self,**kwargs):
        """
        创建安全组
        :param VpcId:
        :param Zone:
        :return: 创建子网的返回内容
        """
        cret_req = vpc_models.CreateSecurityGroupRequest()
        # 定义安全组名称
        cret_req.GroupName = kwargs.get('GroupName') if kwargs.get('GroupName') else 'go2tencent-sec-group' + self.random_char
        # 定义安全组描述信息
        cret_req.GroupDescription = kwargs.get('GroupDescription') if kwargs.get('GroupDescription') else 'go2tencent sec! ingress TCP/22,8703'

        try:
            response = self.vpc_helper.CreateSecurityGroup(cret_req)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)

    def cret_sec_inpolicy(self, secg_id):
        """
        创建安全组入方向规则
        :param secg_id: 安全组id
        :return: 创建规则信息
        """
        cret_req = vpc_models.CreateSecurityGroupPoliciesRequest()

        cret_req.SecurityGroupId = secg_id
        cret_req.SecurityGroupPolicySet = {
            "Ingress": [
                {
                    "Protocol": "TCP",
                    "Port": "8703",
                    "CidrBlock": "0.0.0.0/0",
                    "Action": "ACCEPT",
                    "PolicyDescription": "rsyncd"
                },
                {
                    "Protocol": "TCP",
                    "Port": "22",
                    "CidrBlock": "0.0.0.0/0",
                    "Action": "ACCEPT",
                    "PolicyDescription": "sshd"
                }
            ]
        }
        try:
            response = self.vpc_helper.CreateSecurityGroupPolicies(cret_req)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)


    def cret_sec_outpolicy(self, secg_id):
        """
        创建安全组出方向规则
        :param secg_id: 安全组id
        :return: 创建规则信息
        """
        cret_req = vpc_models.CreateSecurityGroupPoliciesRequest()
        cret_req.SecurityGroupId = secg_id
        cret_req.SecurityGroupPolicySet = {
            "Egress": [
                {
                    "Protocol": "ALL",
                    "CidrBlock": "0.0.0.0/0",
                    "Action": "ACCEPT",
                    "PolicyDescription": "rsyncd",
                },
            ]
        }
        try:
            response = self.vpc_helper.CreateSecurityGroupPolicies(cret_req)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)

    def cret_keypair(self,**kwargs):
        """
        创建密钥对
        :param config_dict:
        :return:
        """
        cret_req = cvm_models.CreateKeyPairRequest()
        cret_req.KeyName = kwargs.get('KeyName') if kwargs.get('KeyName') else 'go2tencent_keypair_' + self.random_char
        cret_req.ProjectId = kwargs.get('ProjectId') if kwargs.get('ProjectId') else 0

        try:
            response = self.cvm_helper.CreateKeyPair(cret_req)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)

    def des_insconfig(self, zone):
        """
        查询实例所至此的类型
        :param config_dict:
        :return:
        """

        des_req = cvm_models.DescribeInstanceTypeConfigsRequest()
        des_req.Filters = [{
            "Name": 'zone',
            "Values": [zone]
        }]
        try:
            response = self.cvm_helper.DescribeInstanceTypeConfigs(des_req)
            result_content = json.loads(response.to_json_string())
            return result_content
        except TencentCloudSDKException as err:
            print(err)


    def cret_cvm(self, cvm_info_dict,**kwargs):
        """
        创建INSTANCE_FOR_GOTOTECENT
        {
            Zone:'',
            InstanceType:'',
            ImageId:'',
            DataDisksSize:'',
            VpcId:'',
            SubnetId:'',
            SecurityGroupId:'',
            InstanceName
            InstanceName:'',
        }
        """
        # 创建request
        cret_req = cvm_models.RunInstancesRequest()

        # 通过列表数组获取实例类型
        cret_req.InstanceType = cvm_info_dict.get('InstanceType')

        # 定义创建的cvm创建的地域
        cret_req.Placement = {
            'Zone': cvm_info_dict.get('Zone'),
        }

        # 定义cvm付费类型，按量后付费：POSTPAID_BY_HOUR   预付费：PREPAID
        cret_req.InstanceChargeType = 'POSTPAID_BY_HOUR'

        # 如果外部传入imageid，则使用传入的imageid
        cret_req.ImageId = kwargs.get('ImageId') if kwargs.get('ImageId') else cvm_info_dict.get('ImageId')


        # 定义系统盘类型及大小
        if kwargs.get('DiskSize'):

            cret_req.SystemDisk = {
                "DiskType": 'CLOUD_PREMIUM',
                "DiskSize": kwargs.get('DiskSize'),
            }
        else:
            cret_req.SystemDisk = {
                "DiskType": 'CLOUD_PREMIUM',
                "DiskSize": '50',
            }

        # 定义数据盘的类型和，数据盘的大小
        cret_req.DataDisks = [{
            'DiskType': 'CLOUD_PREMIUM',
            'DiskSize': cvm_info_dict.get('DataDisksSize')
        }]

        # 定义指定vpc属性
        cret_req.VirtualPrivateCloud = {
            "VpcId": cvm_info_dict.get('VpcId'),
            "SubnetId": cvm_info_dict.get('SubnetId'),
            "AsVpcGateway": 'FALSE',
        }

        # 读取cvm_info.md文件，定义安全组
        cret_req.SecurityGroupIds = [cvm_info_dict.get('SecurityGroupId')]

        cret_req.InstanceName = kwargs.get('InstanceName') if kwargs.get('InstanceName') else 'go2tencent_tran_' + self.random_char

        # 读取cvm_info.md文件，定义主机名称

        cret_req.HostName = kwargs.get('HostName') if kwargs.get('HostName') else 'go2tencent-tran' + self.random_char

        # 公网带宽相关选项
        cret_req.InternetAccessible = {
            # 网络计费类型
            # BANDWIDTH_PREPAID：预付费按带宽结算
            # TRAFFIC_POSTPAID_BY_HOUR：流量按小时后付费
            # BANDWIDTH_POSTPAID_BY_HOUR：带宽按小时后付费
            # BANDWIDTH_PACKAGE：带宽包用户
            'InternetChargeType': 'TRAFFIC_POSTPAID_BY_HOUR',
            # 公网出带宽上限，单位：Mbps,默认为0
            'InternetMaxBandwidthOut': '5',
            # 'InternetMaxBandwidthOut': instance_list[14],
            # 是否分配公网IP
            # 当公网带宽大于0Mbps时，可自由选择开通与否，默认开通公网IP；当公网带宽为0，则不允许分配公网IP。
            'PublicIpAssigned': 'TRUE'
        }

        # 登陆设置
        if kwargs.get('Password'):
            cret_req.LoginSettings = {
                'Password': kwargs.get('Password'),
            }

        else:
            cret_req.LoginSettings = {
                # 'Password': 'WWW.51idc.com',
                'KeyIds': [cvm_info_dict.get('KeyId')]
                # 表示保持镜像的登录设置，不支持公有镜像
                # 'KeepImageLogin':'TRUE'
            }
        # 启用安全加固急监控
        cret_req.EnhancedService = {
            'SecurityService': {"Enabled": "TRUE"},
            'MonitorService': {"Enabled": "TRUE"},
        }
        # 标签
        cret_req.TagSpecification = [{
            "ResourceType": "instance",
            "Tags": [{
                "Key": "go2tencent_key",
                "Value": 'go2tencent_values'
            }]
        }]
        # 指定开机后执行DNS修改172.18.80.13/14，Base64编码格式，如需要修改，参照Readme中说明
        # create_req.UserData = "IyEvYmluL2Jhc2gKCiMgMjAxOC0xMC0xNgoKY2F0IDw8IEVPRiA+IC9ldGMvcmVzb2x2LmNvbmYKbmFtZXNlcnZlciAxNzIuMTguODAuMTMgCm5hbWVzZXJ2ZXIgMTcyLjE4LjgwLjE0CkVPRgo="
        # 创建的cvm数量
        cret_req.InstanceCount = 1
        # 置放群组id
        # create_req.DisasterRecoverGroupIds = [CvmOper.DisasterRecoverGroupIds_Dict[instance_list[9]]]

        try:
            response = self.cvm_helper.RunInstances(cret_req)

            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)


    def des_cvm(self, instance_id):
        """
        根据实例id查询cvm信息
        :return:
        """

        describe_req = cvm_models.DescribeInstancesRequest()
        describe_req.Filters = [
            {
                "Name": "instance-id",
                "Values": [instance_id]
            }
        ]
        try:
            response = self.cvm_helper.DescribeInstances(describe_req)
            result_content = response.to_json_string()

            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)


    def del_cvm(self, InstanceId):
        """
        通过instanceid查询实例信息
        :return:
        """

        del_req = cvm_models.TerminateInstancesRequest()
        del_req.InstanceIds = [InstanceId]
        try:
            response = self.cvm_helper.TerminateInstances(del_req)
            result_content = response.to_json_string()
            return True
        except TencentCloudSDKException as err:
            print(err)

    def des_impimgos(self):

        des_imgreq = cvm_models.DescribeImportImageOsRequest()

        try:
            response = self.cvm_helper.DescribeImportImageOs(des_imgreq)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)



    def import_img(self, imginfo_dict, Force=True,**kwargs):
        """
        OsType=CentOS
        OsVersion=6
        Architecture=x86_64
        ImageUrl=http://111-1251233127.cosd.myqcloud.com/Windows%20Server%202008%20R2%20x64a.vmdk
        :return:
        imginfo_dict
        ｛
            Architecture:'',
            OsType:'',
            OsVersion:'',
            ImageUrl:'',
            ImageName:'',
        ｝
        """

        impimg_req = cvm_models.ImportImageRequest()
        impimg_req.Architecture = imginfo_dict.get('Architecture')
        impimg_req.OsType = imginfo_dict.get('OsType')
        impimg_req.OsVersion = imginfo_dict.get('OsVersion')
        impimg_req.ImageUrl = kwargs.get('ImageUrl') if kwargs.get('ImageUrl') else imginfo_dict.get('ImageUrl')
        impimg_req.ImageUrl = imginfo_dict.get('ImageUrl')
        impimg_req.ImageName = imginfo_dict.get('ImageName')
        impimg_req.Force = Force
        try:
            response = self.cvm_helper.ImportImage(impimg_req)
            result_content = response.to_json_string()
            return True
        except TencentCloudSDKException as err:

            return False

    def des_imgid(self,imghub_type = 'PRIVATE_IMAGE',Offset=0,Limit=100):
        """
        查询镜像id
        :return:
        """
        des_req = cvm_models.DescribeImagesRequest()
        des_req.Offset = Offset
        des_req.Limit = Limit
        des_req.Filters = [
            {
                # 共有镜像：PUBLIC_IMAGE，私有镜像：PRIVATE_IMAGE
                "Name": "image-type",
                "Values": [imghub_type]
            },
            {
                "Name": "image-state",
                "Values": ["NORMAL"]
            }
        ]

        response = self.cvm_helper.DescribeImages(des_req)
        result_content = response.to_json_string()
        return json.loads(result_content)

    def des_cvm_status(self, instance_id):
        """
        通过instanceid查询实例状态
        :return:
        """

        des_req = cvm_models.DescribeInstancesStatusRequest()
        des_req.InstanceIds = [instance_id]
        try:
            response = self.cvm_helper.DescribeInstancesStatus(des_req)
            result_content = response.to_json_string()
            return json.loads(result_content)
        except TencentCloudSDKException as err:
            print(err)

    def del_vpc(self,vpc_id):
        """
        跟进vpcid删除vpc
        :param config_dict:
        :param VpcId:
        :return:
        """

        cret_req = vpc_models.DeleteVpcRequest()
        cret_req.VpcId = vpc_id
        try:
            response = self.vpc_helper.DeleteVpc(cret_req)
            result_content = response.to_json_string()
            return True
        except TencentCloudSDKException as err:
            print(err)

    def del_secg(self, SecurityGroupId):
        """
        通过instanceid删除安全组
        :return:
        """

        del_secg_req = vpc_models.DeleteSecurityGroupRequest()
        del_secg_req.SecurityGroupId = SecurityGroupId
        try:
            response = self.vpc_helper.DeleteSecurityGroup(del_secg_req)
            result_content = response.to_json_string()
            return True
        except TencentCloudSDKException as err:
            print(err)


    def del_keypair(self, KeyIds):
        """
        通过KeyIds删除key
        :return:
        """

        delete_req = cvm_models.DeleteKeyPairsRequest()
        delete_req.KeyIds = [KeyIds]
        try:
            response = self.cvm_helper.DeleteKeyPairs(delete_req)
            result_content = response.to_json_string()
            return True
        except TencentCloudSDKException as err:
            print(err)

    def __head_bucket(self,app_id,bucket_name):
        """
        判断bucket是否存在
        :param app_id:
        :param bucket_name:
        :return: True表示bucket不存在，False表示存在
        """
        try:
            self.cos_helper.head_bucket(
                Bucket=''.join([bucket_name, '-', app_id])
            )
            return False
        except Exception as err:
            return True

    def create_bucket(self,app_id,bucket_name):
        try:
            if CloudHelper.__head_bucket(self,app_id,bucket_name):

                response = self.cos_helper.create_bucket(
                    Bucket=bucket_name,
                    ACL='public-read',
                )
                time.sleep(2)
                if not CloudHelper.__head_bucket(self,app_id,bucket_name):
                    return True
        except Exception as err:
            print(err)

    def cos_upload_file(self, app_id,bucket_name,filename, partsize=10, maxthread=5):
        """
        根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
        :param filename:
        :param cos_client:
        :param partsize:
        :param maxthread:
        :return:
        """

        # 进行上传
        try:
            # 判断bucket是否存在
            if not CloudHelper.__head_bucket(self,app_id,bucket_name):
                response = self.cos_helper.upload_file(
                    Bucket=''.join([bucket_name, '-', app_id]),
                    LocalFilePath=filename,
                    Key=filename,
                    PartSize=partsize,
                    MAXThread=maxthread
                )
                return response
        except Exception as err:
            print(err)


    def get_obj_url(self, app_id,bucket_name,filename):
        """
        获取obj的下载url
        :param app_id:
        :param bucket_name:
        :param filename:
        :return:
        """
        try:
            response = self.cos_helper.get_presigned_download_url(
                Bucket=''.join([bucket_name, '-', app_id]),
                Key=filename,
                Expired=3600

            )
            return response
        except Exception as err:
            print('err')

    def __des_obj(self,app_id,bucket_name):
        """
        查询指定bucket内的object
        :param config_dict:desc
        :return:返回buclet下的obj list
        """

        try:
            response = self.cos_helper.list_objects(
                Bucket=''.join([bucket_name, '-', app_id]),
                MaxKeys=100,
                EncodingType='url'
            )

            file_list = [file['Key'] for file in response['Contents']]

            return file_list
        except Exception as err:
            print(err)

    def __del_obj(self, app_id,bucket_name):
        """
        返回指定bucket内的object
        :param config_dict:
        :return:
        """

        try:
            obj_dict_list = [ {'Key': file} for file in CloudHelper.__des_obj(self,app_id,bucket_name) ]
            response = self.cos_helper.delete_objects(
                Bucket=''.join([bucket_name, '-', app_id]),
                Delete={
                    'Object': obj_dict_list
                }
            )
            return response
        except Exception as err:
            print(err)

    def del_bucket(self,app_id,bucket_name):
        """
        删除bucket
        :param config_dict:
        :return:
        """
        try:
            if CloudHelper.__del_obj(self,app_id,bucket_name):
                response = self.cos_helper.delete_bucket(
                    Bucket=''.join([bucket_name, '-',app_id])
                )
                return True
        except Exception as err:
            print(err)


