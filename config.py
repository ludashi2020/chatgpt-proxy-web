# -*- coding: utf-8 -*-

# 如果更改了此属性，需要手动删除资源目录 [If you change this property, the `resource` directory needs to be manually deleted.]
# 请配置具体的访问ip，而不是0.0.0.0，如果是vps，请配置vps的出口公网ip [Please configure a specific IP address for accessing the service, rather than using 0.0.0.0. If you are using a VPS, please configure the public IP address of the VPS's outbound traffic.]
listen_addr = ("127.0.0.1", 8011)

# 如果你打算使用域名访问，需要配置 `domain_url`，同时`listen_addr`公网可访问，如果是https，需要nginx配置proxy_pass `listen_addr` [If using a domain name, need to configure `domain_url`, and `listen_addr` should be accessible from the public network. If it is an HTTPS service, need to configure nginx proxy_pass `listen_addr`.]
# 示例example1: domain_url = "http://chatgpt.chat:8011"; listen_addr = ("8.8.8.8", 8011)
# 示例example2: domain_url = "http://chatgpt.chat"; listen_addr = ("8.8.8.8", 80)
# 示例example3: domain_url = "https://chatgpt.chat"; listen_addr = ("127.0.0.1", 8011); nginx `location / {proxy_pass http://127.0.0.1:8011}`
domain_url = ""

# 开启页面的账号密码认证 [Enable account and password authentication for the webpage.]
is_verify = False

# 代理配置，http或socks5都可以 [Proxy configuration, either HTTP or SOCKS5.]
proxies = {"https": ""}

# Plus专属Cookie参数，如果没有，找朋友蹭一个 [Plus-exclusive cookie parameters. If you don't have them, ask a friend to share theirs.]
puid = ""

'''
1. 如果使用邮箱密码登录，则只需要填写email_address和password这两个参数 [If using email login, only the `email_address` and `password` require.]
2. 如果使用Chrome或Microsoft登录，则只需要填写session_token这一个参数 [If not email login, only the `session_token` require.]
3. 如果使用Chrome或Microsoft登录，并且同时开启了账号密码认证，则需要重写user参数 [If not email login and also enable is_verify, the `user` needs to be rewritten.]
   user = md5(('your_email' + 'your_password').encode()).hexdigest()
'''

password_list = [
    {"email_address": "", "password": "", "session_token": None, "user": None},
]
