__author__ = 'Hugee'
import sys,os
import re
import threading
import  paramiko


PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PATH)

from conf import host_list

class Batch_cmd():

    def __init__(self,ip,username,password,cmd,port):
        self.ip = ip
        self.username = username
        self.password = password
        self.cmd = cmd
        self.port = port

    def run(self):
        cmd_str = self.cmd.split()[0]
        if hasattr(self, cmd_str):
            func = getattr(self,cmd_str)
            func()
        else:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.ip,username=self.username,password=self.password)
            stdin,stdou,stderr = ssh.exec_command(self.cmd)
            result = stdou if stdou else stderr
            print(result.read().decode())
            ssh.close()

    def put(self):
        """上传文件"""
        print(1)
        filename = self.cmd.split()[1]  #要上传的文件
        transport = paramiko.Transport((self.ip, self.port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(filename, filename)
        print("put sucesss")
        transport.close()


def show_host_list():


    last_layer=[host_list.msg_dic,] # 列表记录当前层

    host_new_dic = {} # 定义一个新字典用于存储用户选择的主机

    while 1:
        # print(last_layer)
        if len(last_layer) == 1:
            print(" Name ","DeviceCount")
            for key in host_list.msg_dic:
                print(key,"\t",len(host_list.msg_dic[key]))
        else:
            for key in last_layer[len(last_layer)-1]: #打印当前层下的数据信息
                print(key,last_layer[-1][key])
        # print(num)
        choose_host_list = input("\n>>>:  ").strip() #选择当前层下的key值
        if len(choose_host_list) == 0: continue
        if choose_host_list in last_layer[-1]: # 如果key值存在
            if re.match(r"^h\d",choose_host_list):
                if choose_host_list in host_new_dic:
                    count=1
                    host_new_dic[choose_host_list,count] = last_layer[-1][choose_host_list]
                    count+=1
                else:
                    host_new_dic[choose_host_list] = last_layer[-1][choose_host_list]

            else:
                last_layer.append(last_layer[len(last_layer)-1][choose_host_list]) # 把该key加入到记录列表
            # print(last_layer)


        if choose_host_list ==  "b":
            print(host_new_dic)
            return host_new_dic

        if choose_host_list ==  "q":
            if last_layer:
                last_layer.pop() # 保存列表的最后一个弹出，使切换到上一层


def interactive(seleted_list):
    thread_list = []

    while True:
        cmd = input(">>cmd: ").strip()
        if cmd:
            for key in selected_list:
                ip,username,password,cmd,port = selected_list[key]["IP"],selected_list[key]["username"],selected_list[key]["password"],cmd,selected_list[key]["port"]
                func = Batch_cmd(ip,username,password,cmd,port)
                th = threading.Thread(target=func.run)
                th.start()
                thread_list.append(th)

                for l in thread_list:
                    l.join()
        else:
            continue






selected_list = show_host_list()
interactive(selected_list)

