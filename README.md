# chatgpt-proxy-web
Flask reverse proxy ChatGPT website chat.openai.com/chat.

[中文](https://github.com/cooolr/chatgpt-proxy-web/blob/main/README_ZH.md) | [English](https://github.com/cooolr/chatgpt-proxy-web/blob/main/README.md)

## Prepare

You should log in to the [ChatGPT website](https://chat.openai.com/chat), find the cookie named `_puid`, and then copy its value.

**This project heavily relies on the Plus-exclusive _puid parameter. Without it, CloudFlare cannot be bypassed.**

Modify `config.py` to set the configuration.
``` python
# If you change this property, the `resource` directory needs to be manually deleted.
# Please configure a specific IP address for accessing the service, rather than using 0.0.0.0. If you are using a VPS, please configure the public IP address of the VPS's outbound traffic.
listen_addr = ("127.0.0.1", 8011)

# If using a domain name, need to configure `domain_url`, and `listen_addr` should be accessible from the public network. If it is an HTTPS service, need to configure nginx proxy_pass `listen_addr`.
# example1: domain_url = "http://chatgpt.chat:8011"; listen_addr = ("8.8.8.8", 8011)
# example2: domain_url = "http://chatgpt.chat"; listen_addr = ("8.8.8.8", 80)
# example3: domain_url = "https://chatgpt.chat"; listen_addr = ("127.0.0.1", 8011); nginx `location / {proxy_pass http://127.0.0.1:8011}`
domain_url = ""

# Enable account and password authentication for the webpage.
is_verify = False

# Proxy configuration, either HTTP or SOCKS5.
proxies = {"https": ""}

# Plus-exclusive cookie parameters. If you don't have them, ask a friend to share theirs.
puid = ""

'''
1. If using email login, only the `email_address` and `password` require.
2. If not email login, only the `session_token` require.
3. If not email login and also enable is_verify, the `user` needs to be rewritten.
   user = md5(('your_email' + 'your_password').encode()).hexdigest()
'''

password_list = [
    {"email_address": "", "password": "", "session_token": None, "user": None},
]
```

## Install dependencies

``` bash
pip install -r requirements.txt
```

## Quick start

``` bash
python3 main.py
```

browser open link: [http://127.0.0.1:8011/chat](http://127.0.0.1:8011/chat)

## Futures

1. Bypass the free account Cloudflare verification to achieve a response speed comparable to that of Plus members
2. Add the Plus member logo to the free account
3. Bypass the regional ban on chat.openai.com

## Note

1. relies on the Plus-exclusive _puid parameter. Without it, CloudFlare cannot be bypassed.
2. auto login `auth.py`, thank you [https://github.com/acheong08/OpenAIAuth](https://github.com/acheong08/OpenAIAuth).

## Renderings
![login](https://github.com/cooolr/chatgpt_plus_proxy_website/blob/main/templates/login.png)
![chat](https://github.com/cooolr/chatgpt_plus_proxy_website/blob/main/templates/chat.png)
