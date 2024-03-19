#!/usr/bin/env python3
# coding: utf-8
import paramiko

from hdtools.user_specific.server import known_server


def connect_ssh(host, user, port, key_path, time_out=10):

    ssh = paramiko.SSHClient()
    ssh.banner_timeout = time_out
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    key = paramiko.RSAKey.from_private_key_file(key_path)

    ssh.connect(host, port, user, pkey=key, timeout=time_out)

    return ssh


def connect_sftp(server_name):

    server = known_server[server_name]

    host = server['host']
    user = server['user']
    port = server['port']
    key_path = server['key_path']

    key = paramiko.RSAKey.from_private_key_file(key_path)

    t = paramiko.Transport((host, port))
    t.connect(username=user, pkey=key)
    
    sftp=paramiko.SFTPClient.from_transport(t)

    return t, sftp


if __name__ == '__main__':

    pass