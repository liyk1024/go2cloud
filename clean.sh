#!/bin/bash

BASEPATH=$(cd `dirname $0`;pwd)

PY_CMD=${BASEPATH}/go2tencent_env/bin/python
REQUIRE_FILE=${BASEPATH}/requirements.txt

MAIN_APP=${BASEPATH}/go2tencent_src/main.py 

# 安装环境

#${PY_CMD} -m pip install -r ${REQUIRE_FILE} 

# 运行脚本
${PY_CMD} ${MAIN_APP} clean
