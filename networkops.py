__author__ = 'Vasiliy'

import re
import subprocess
import socket
import paramiko
import argparse

def params():
    """Import parameters from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-lg', '--logfile', required=True, dest='logfile',
                        help='Enter log file to to use')
    parser.add_argument('-user', '--user', required=True, dest='user',
                        help='Enter user name')
    parser.add_argument('-pw', '--password', required=True, dest='password',
                        help='Enter password')
    args = parser.parse_args()
    location = args.logfile
    uname = args.user
    pwd = args.password
    return location, uname, pwd

what = params()[0]  # existing list hosts on network
who = params()[1]  # user name
why = params()[2]  # password

class SSHConnection(object):

    def __init__(self, host, username, password, port=22):
        # Initialize and setup connection
        self.sftp = None
        self.sftp_open = False

        # open SSH Transport stream
        self.transport = paramiko.Transport((host, port))
        self.transport.connect(username=username, password=password)

    def _openSFTPConnection(self):
        # Opens an SFTP connection if not already open
        if not self.sftp_open:
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            self.sftp_open = True

    def get(self, remote_path, local_path=None):
        # Copies a file from the remote host to the local host.
        self._openSFTPConnection()
        self.sftp.get(remote_path, local_path)

    def put(self, local_path, remote_path=None):
        # Copies a file from the local host to the remote host
        self._openSFTPConnection()
        self.sftp.put(local_path, remote_path)

    def close(self):
        # Close SFTP connection and ssh connection
        if self.sftp_open:
            self.sftp.close()
            self.sftp_open = False
        self.transport.close()

def checkhost(node):
    # check if current host on our existing list hosts
    logs = open(what, 'r')
    for line in logs:
        if node in line:
            logs.close()
            return True

def writehost(node):
    #add current host to log file list
    logs = open(what, 'a')
    logs.write(node + "\n")
    logs.close()
    return True

def setmark(node):
    # mark host in existing list hosts that received file
    with open(what, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in lines:
            if node in line:
                line = line.replace(line, line.rstrip("\n") + "-sent\n")
            f.write(line)
    return True

# Find active hosts on network
nodes = re.findall(r'\\(.+?)(?: .*)?\n', subprocess.check_output('net view'))

for each in nodes:
    node = each[1:]
    print node
    if checkhost(node):
        IP = socket.gethostbyname(node)

        host = IP
        username = who
        pwd = why
        # transfer file from origination host to destination
        origin = 'D:\test\F1\New Text Document.txt'
        dst = 'C:\New Text Document.txt'

        ssh = SSHConnection(host, username, pwd)
        ssh.put(origin, dst)
        ssh.close()
        setmark(node)
    else:
        writehost(node)



