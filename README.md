# errbot-backend-lark

结合飞书机器人消息接口定制化的 Errbot 后端服务插件（backend）

## 目标

* 只要按照飞书上的机器人开发流程对接以及处理好相应的配置，就可以快速搭建一个运维聊天机器人；
* 利用Errbot本身框架提供的插件化特性，可以很便利，也很快速开发和集成所需要的运维功能。

## 飞书开发流程

可以参考开放平台提供的文档：https://open.feishu.cn/document/home/develop-a-bot-in-5-minutes/create-an-app

1. 目前申请需要的权限是：
   * 获取用户 userid
   * 获取用户基本信息
   * 获取与发送单聊、群组消息
   * 获取用户发给机器人的单聊消息
   * 获取用户在群聊中@机器人的消息
   * 以应用身份读取通讯录

2. 开通机器人功能
3. 订阅事件
   1.  接收消息

4. 配置请求网址 URL

## 安装

首先是要确保安装好 `python3`

1. 创建一个 errbot 的虚拟环境

   ```shell
   mkdir -p /opt/errbot/backend
   virtualenv --python=python3 /opt/errbot/virtualenv
   ```

2. 安装并初始化 errbot, 详情可以看[这里](https://errbot.readthedocs.io/en/latest/user_guide/setup.html)

   ```bash
   source /opt/errbot/virtualenv/bin/activate
   pip install errbot
   cd /opt/errbot
   errbot --init
   ```

3. 在 `/opt/errbot/config.py` 配置 `Lark` 的配置项

   ```bash
   BACKEND="Lark"
   BOT_EXTRA_BACKEND_DIR=/opt/errbot/backend
   ```

4. 克隆 `errbot-backend-lark` 到指定的目录下，并安装依赖文件

   ```bash
   cd /opt/errbot/backend
   git clone https://gitea.xintech.co/zhouzhihong/errbot-backend-lark
   pip install -r /opt/errbot/backend/errbot-backend-lark/requirements.txt
   ```

5. 接下来就是配置飞书机器人应用对应的 信息，给与相应的接口访问权限，服务监听的端口等

   ```python
   BOT_IDENTITY = {
       "app_id": "cli_xxxxxxxxxx",
       "app_secret": "sssssssssssss",
       "verification_token": "tttttttttttttttt",
       "encrypt_key": None,
       "host": "0.0.0.0",
       "port": 8000
   }
   ```

   * 服务默认接收消息的路径是 `/bot`

6. （可选）配置管理员，添加对应的 `open_id`

   ```bash
   ## lark admin
   BOT_ADMINS = ('ou_ooooooooooo')  # !! Don't leave that to "@CHANGE_ME" if you connect your errbot to a chat system !! 
   ```

   
