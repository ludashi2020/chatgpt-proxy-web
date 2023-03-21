# chatgpt-proxy-web

Flask 反向代理 ChatGPT 网站 chat.openai.com/chat。


[中文](https://github.com/cooolr/chatgpt-proxy-web/blob/main/README_ZH.md) | [English](https://github.com/cooolr/chatgpt-proxy-web/blob/main/README.md)

## 准备

您应该登录 [ChatGPT 网站](https://chat.openai.com/chat)，找到名为 `_puid` 的 cookie，然后复制值。

**该项目严重依赖于专用于 Plus 的 `_puid` 参数。 没有它，就无法绕过 CloudFlare。**

修改 `config.py` 来设置配置

``` python
# 如果更改了此属性，需要手动删除资源目录
# 请配置具体的访问ip，而不是0.0.0.0，如果是vps，请配置vps的出口公网ip
listen_addr = ("127.0.0.1", 8011)

# 如果你打算使用域名访问，需要配置 `domain_url`，同时`listen_addr`公网可访问，如果是https，需要nginx配置proxy_pass `listen_addr`
# 示例1: domain_url = "http://chatgpt.chat:8011"; listen_addr = ("8.8.8.8", 8011)
# 示例2: domain_url = "http://chatgpt.chat"; listen_addr = ("8.8.8.8", 80)
# 示例3: domain_url = "https://chatgpt.chat"; listen_addr = ("127.0.0.1", 8011); nginx `location / {proxy_pass http://127.0.0.1:8011}`
domain_url = ""

# 开启页面的账号密码认证
is_verify = False

# 代理配置，http或socks5都可以
proxies = {"https": ""}

# Plus专属Cookie参数，如果没有，找朋友蹭一个
puid = ""

'''
1. 如果使用邮箱密码登录，则只需要填写email_address和password这两个参数
2. 如果使用Chrome或Microsoft登录，则只需要填写session_token这一个参数
3. 如果使用Chrome或Microsoft登录，并且同时开启了账号密码认证，则需要重写user参数
   user = md5(('your_email' + 'your_password').encode()).hexdigest()
'''

password_list = [
    {"email_address": "", "password": "", "session_token": None, "user": None},
]
```

## 安装依赖

``` bash
pip install -r requirements.txt
```

## 快速开始

``` bash
python3 main.py
```

浏览器打开链接：[http://127.0.0.1:8011/chat](http://127.0.0.1:8011/chat)

## 特性

1. 绕过免费账号Cloudflare验证，达到媲美Plus会员的响应速度
2. 免费账号增加Plus会员标识
3. 绕过地区对chat.openai.com的封禁

## 注意

1. 依赖于专用于 Plus 的 `_puid` 参数。 没有它，就无法绕过 CloudFlare。
2. 自动登录部分 `auth.py` ,感谢[https://github.com/acheong08/OpenAIAuth](https://github.com/acheong08/OpenAIAuth)

## 效果图
![登录](https://github.com/cooolr/chatgpt_plus_proxy_website/blob/main/templates/login.png)
![聊天](https://github.com/cooolr/chatgpt_plus_proxy_website/blob/main/templates/chat.png)
