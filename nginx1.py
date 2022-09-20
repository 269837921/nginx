from datetime import datetime
import json
import numpy as np
import os
from os import path
import time
import random

class Nginx:
    def __init__(self,nginx_path):
        '''
        :param nginx_path: nginx绝对路径
        :param stock_nginx_data: 存储格式
        :param full_list_nginx_info:nginx.conf的字段内容
        :param nginx_json:生成的json文件
        :param list_index_server:每个server开头和结尾的索引
        :param nginx_dir:创建文件夹的地址
        '''
        self.nginx_path=nginx_path
        self.random=random.randint(1,10)
        self.random_2=random.randint(1,100)
        self.stock_nginx_data={}
        self.full_list_nginx_info=[]
        self.stock_nginx_data["main"] = {}
        self.stock_nginx_data["events"] = {}
        self.stock_nginx_data["http"] = {}
        self.stock_nginx_data["servers"] = []
        self.list_index_server=[]
        self.nginx_dir = "C:/Users/Administrator/Desktop/nginx/nginx分析配置{0}_{1}".format(self.random, self.random_2)

    def main(self):
        '''
        程序的入口
        '''
        self.find_nginx_path()

    def find_nginx_path(self):
        '''
        寻找nginx的配置路径
        '''
        try:
            #创建文件夹
            os.mkdir(self.nginx_dir)
            if path.isfile(self.nginx_path):
                self.nginx_course()
            elif path.isdir(self.nginx_path):
                self.find_nginx_path_conf(self.nginx_path)
                self.nginx_course()


        except Exception as e:
            print(e)

    def nginx_course(self):
        '''找nginx主配置文件'''
        file = open(self.nginx_path, "r", encoding="utf-8")
        lines = file.readlines()
        self.resolve_nginx_conf_list_foramt(lines)
        self.include_case_analy(lines)
        file.close()

    def find_nginx_path_conf(self,item):
        '''找nginx目录'''
        file = os.listdir(item)
        for i in file:
            new_path=os.path.join(item,i)
            if os.path.isfile(new_path) and i!="nginx.conf":
                continue

            if i=="src":
                continue

            if os.path.isfile(new_path) and i == "nginx.conf":
                self.nginx_path=new_path
                break
            if os.path.isdir(new_path):
                self.find_nginx_path_conf(new_path)


    def nginx_path_case(self,nginx_include_path):
        '''对查找情况的分析是目录还是nginx.cof文件，前提是要有include
        nginx_include_path:include的目录
        '''
        if path.isdir(nginx_include_path):
            file=os.listdir(nginx_include_path)
            for f in file:
                if  f[-4:]=="conf":
                    nginx_son_conf=os.path.join(nginx_include_path,f)
                    self.son_config(nginx_son_conf)


        if nginx_include_path[-4:]=="conf":
            self.son_config(nginx_include_path)

    def son_config(self,nginx_include_path):
        '''重置数据'''
        self.list_index_server = []
        self.full_list_nginx_info = []
        self.stock_nginx_data["main"] = {}
        self.stock_nginx_data["events"] = {}
        self.stock_nginx_data["http"] = {}
        self.stock_nginx_data["servers"] = []
        self.stock_nginx_data["upstram"] = []
        file = open(nginx_include_path, "r", encoding="utf-8")
        lines = file.readlines()
        self.resolve_nginx_conf_list_foramt(lines)
        self.resolve_nginx_conf()
        file.close()

    def resolve_nginx_conf_list_foramt(self,lines):
        '''
        将配置文件的每行内容格式化成列表的形式
        :param lines:lines = file.readlines()
        '''
        try:
            for line in lines:
                for n in range(2, 13):
                    new_line = line.replace((" ") * n, " ")
                    line = new_line
                    if n == 12:
                        new_line = line.split(" ")
                        new_line[0] = new_line[0].strip()
                        new_line[-1] = new_line[-1].strip()
                        for i in range(len(new_line)-1,-1,-1):
                            if len(new_line) == 1:
                                break
                            if new_line[i]=="":
                                del new_line[i]
                        if len(new_line[-1])> 1 and new_line[-1][-1]!="{" and new_line[-1][-1]!=")":
                            new_line[-1]=new_line[-1][0:-1] #去除#号
                        #if new_line[0][0]=="#":
                            #new_line[0] =new_line[0][1:]
                        if len(new_line[0])>=1:
                            self.full_list_nginx_info.append(new_line)
        except Exception as e:
            print("resolve_nginx_conf_list_foramt,错误原因",e)

    def include_case_analy(self,lines):
        '''对include是否存在子配置文件的分析'''
        try:
            #主配置文件的分析
            crt_path=self.nginx_path[:-10] #当前文件路径
            include_list=[]
            for item in self.full_list_nginx_info:
                if len(item)>=2:
                    if item[0]=="include":
                        if "\\" not in item[1] and "/" not in item[1]:
                            continue
                        include_list.append(item[1])
                        break
            if len(include_list):
                # 先判断结尾路径是否存在通配符 *.conf
                if "*" in include_list[0]:
                    index=include_list[0].index("*")
                    include_list[0]=include_list[0][:index]
                    self.include_exists_case(include_list,crt_path)

                elif "*" not in include_list[0]:
                    self.include_exists_case(include_list,crt_path)
            else:
                self.resolve_nginx_conf()

        except Exception as e:
            print("文件不存在")

    def include_exists_case(self,include_list,crt_path):
        if os.path.exists(include_list[0]):
            self.nginx_path_case(include_list[0])
            return
        if crt_path[-1]=="\\" or  crt_path[-1]=="/":
            crt_path=crt_path[:-1]# 当前路径

        if include_list[0][0]=="\\" or include_list[0][0]=="/":
            include_list[0]=include_list[0][1:]

        new_crt_path=os.path.join(crt_path,include_list[0])
        if os.path.exists(new_crt_path):
            self.nginx_path_case(new_crt_path)
            return

        if "\\" in self.nginx_path:
            list_nginx_path = self.nginx_path.split("\\")
            if "\\" in include_list[0]:
                split_include_list = include_list[0].split("\\")
                path2 = "\\".join(split_include_list)
                self.path_join(path2, list_nginx_path, split_include_list)
            if "/" in include_list[0]:
                split_include_list = include_list[0].split("/")
                path2 = "/".join(split_include_list)
                self.path_join(path2, list_nginx_path,split_include_list)
            # 暂时只支持window的”\\“
        elif "/" in self.nginx_path:
            pass

    def path_join(self,path2,list_nginx_path,split_include_list):
        '''对include路径进行拼接 在通配符存在并且去除的情况下得到一个include目录'''
        for item in split_include_list:
            nginx_path_index = list_nginx_path.index(item)
            if nginx_path_index:
                list_nginx_path = list_nginx_path[:nginx_path_index]
                break
        path1 = "\\".join(list_nginx_path)
        nginx_include_path = os.path.join(path1, path2)  # 得到真正的include路径  因为去掉了通配符,所有尾部是目录
        self.nginx_path_case(nginx_include_path)

    def resolve_nginx_conf(self):
        '''
        解析nginx文件并读写保存的过程
        :param lines:
        :return:
        '''
        self.get_dict_nginx_info_main_event()

    def get_dict_nginx_info_main_event(self):
        '''
        获取主模块和事件模块的信息字段的条件判断
        '''
        try:
            list_str_nginx = []
            for item in self.full_list_nginx_info:
                list_str_nginx.append(" ".join(item))
            for i in self.full_list_nginx_info:
                if i[0]=="htt" or i[0]=="http":
                    index = self.full_list_nginx_info.index(i, 0, -1)
                    self.get_main_event_field(list_str_nginx, index)
                    break
                elif i[0]=="serve" or i[0]=="server":
                    index = self.full_list_nginx_info.index(i, 0, -1)
                    self.get_main_event_field(list_str_nginx,index)
                    break
            self.get_dict_nginx_info_server()
        except Exception as e:
            print("get_dict_nginx_info_main_event,错误原因",e)

    def get_main_event_field(self,list_str_nginx,index):
        '''
        获取主模块和事件模块的信息字段
        :param list_str_nginx:
        :param index:event或http或server的开头索引
        '''
        try:
            for key in self.full_list_nginx_info[:]:
                np_object = np.array(list_str_nginx)
                eq_letter = np.where(np_object == " ".join(key))
                for item in eq_letter[0]:
                    if item < index:
                        if key[0] == "user" or key[0] == "worker_processes" or key[0] == "pid" or key[0] == "error_log":
                            self.stock_nginx_data["main"][key[0]] = " ".join(key[1:])
                        if key[0] == "accept_mutex" or key[0] == "multi_accept" or key[0] == "worker_connections":
                            self.stock_nginx_data["events"][key[0]] = " ".join(key[1:])
        except Exception as e:
            print("get_main_event_field,错误原因",e)

    def get_dict_nginx_info_http(self):
        '''
        获取http的信息字段
        '''
        try:
            list_str_nginx = []
            for item in self.full_list_nginx_info:
                list_str_nginx.append(" ".join(item))
            self.stock_nginx_data["http"]["include"] = []
            for i in self.full_list_nginx_info:
                if i[0]=="htt" or i[0]=="http":
                    http_header=self.full_list_nginx_info.index(i,0,-1)
                    for key in self.full_list_nginx_info:
                        np_object = np.array(list_str_nginx)
                        eq_letter = np.where(np_object == " ".join(key))
                        for item in eq_letter[0]:
                            if http_header<item<len(self.full_list_nginx_info):
                                if item not in tuple(self.list_index_server):
                                    if key[0]=="access_log" or key[0]=="keepalive_timeout" or key[0]=="default_type" or key[0]=="error_page":
                                        self.stock_nginx_data["http"][key[0]]=" ".join(key[1:])
                                    if key[0]=="include":
                                        self.stock_nginx_data["http"]["include"].append(" ".join(key[1:]))
            self.get_dict_nginx_info_upstream()
        except Exception as e:
            print("get_dict_nginx_info_http,错误原因",e)

    def get_dict_nginx_info_server(self):
        '''
        对各种情况的server模板进行分析
        '''
        try:
            list_str_nginx=[]
            for item in self.full_list_nginx_info:
                list_str_nginx.append(" ".join(item))
            for key in list_str_nginx:
                if key=="serve" and len(key)<9:
                    self.get_eq_letter_index(list_str_nginx,key)
                    break
            for key in list_str_nginx:
                if key == "server {" and len(key) < 9:
                    self.get_eq_letter_index(list_str_nginx, key)
                    break
            for key in list_str_nginx:
                if key == "server{" and len(key) < 9:
                    self.get_eq_letter_index(list_str_nginx, key)
                    break
            self.get_dict_nginx_info_http()
        except Exception as e:
            print("get_dict_nginx_info_server,错误原因",e)

    def get_eq_letter_index(self,list_str_nginx,key):
        '''
        获取所有server模板的开头索引
        :param key: server的值
        '''
        np_obj=np.array(list_str_nginx)
        eq_letter = np.where(np_obj == key)
        for i in eq_letter[0]:
            dict_server={}
            header=i
            self.get_server_location_field(header,list_str_nginx,dict_server)

    def get_server_location_field(self,header,list_str_nginx,dict_server):
        '''
        获取server的主要字段和location的开头索引
        :param header: server开头索引
        :param dict_server: 空字典
        '''
        try:
            list_sym=[]
            for item in self.full_list_nginx_info[header:]:
                if  item[-1]=="}" or item[-1]=="{":
                    list_sym.append(item)
                if item[-1]!="{":
                    if item[-1][-1]=="{":
                        list_sym.append(item)
            count=0
            for i in range(0,len(list_sym)):
               if len(list_sym)<=2:
                   count=1
                   break
               if list_sym[i][-1]=="}":
                   count+=1
                   if len(list_sym[i]) > 1:
                       count -= 1
                   if list_sym[i+1][-1]=="}":
                       count+=1
                       break
            dict_server["location"] = [] #一个server location字段用列表表示
            for key in self.full_list_nginx_info[header:]:
                count01 = 0
                if key[0]=="}":
                    np_obj = np.array(list_str_nginx[header:])
                    eq_letter = np.where(np_obj == key[0])
                    tail=eq_letter[0][count-1]
                    for field in self.full_list_nginx_info[header:header+tail]:
                        np_object = np.array(list_str_nginx[header:header+tail])
                        eq_letter = np.where(np_object == " ".join(field))
                        for item in eq_letter[0]:
                            if 0<item<tail:
                                if field[0] == "listen":
                                    if count01<1:
                                        dict_server[field[0]]=[]
                                    dict_server[field[0]].append(" ".join(field[1:]))
                                    if len(dict_server[field[0]])>=2:
                                        if dict_server[field[0]][-1]==dict_server[field[0]][-2]:
                                            del dict_server[field[0]][-1]
                                    count01+=1
                                if field[0] == "server_name" or field[0] =="access_log" or field[0] == "error_page":
                                    dict_server[field[0]] = " ".join(field[1:])
                                if field[0] == "location":
                                    location_dict={}
                                    if "*" in field[-1] and field[-1][-1] != "{":
                                        field[-1] = field[-1] + "$"
                                    if "*" in field[-2]:
                                        field[-2] = field[-2] + "$"
                                    if field[-1] == "{":
                                        if "\\" in " ".join(field):
                                            new_location_path = " ".join(field).replace("\\", "/")
                                            location_dict["location_url"]=new_location_path[9:]
                                        else:
                                            location_dict["location_url"]= "".join(field[1:-1])

                                    elif field[-1] != "{":
                                        if "\\" in " ".join(field):
                                            new_location_path = " ".join(field).replace("\\", "/")
                                            if field[-1][-1] == "{":
                                                location_dict["location_url"]=new_location_path[9:-1]
                                            else:
                                                location_dict["location_url"] = new_location_path[9:]
                                        else:
                                            if field[-1][-1] == "{":
                                                field[-1] = field[-1].replace("{", "")
                                            location_dict["location_url"]=" ".join(field[1:])
                                    location_h = self.full_list_nginx_info[header:header+tail].index(field, 0, -1)
                                    list_location = self.full_list_nginx_info[location_h + header:-1]
                                    self.get_location_info(list_location,list_str_nginx,location_h,header,dict_server,location_dict)
                    self.stock_nginx_data["servers"].append(dict_server)
                    for i in range(header,header+tail):
                        self.list_index_server.append(i)
                    break
        except Exception as e:
            print("get_server_location_field,错误原因", e)

    def get_location_info(self,list_location,list_str_nginx,location_h,header,dict_server,location_dict):
        '''
        得到location 的信息
        :param list_location: nginx里的配置字段
        :param list_str_nginx: 列表,里面元素是通过join转化来的字符串
        :param location_h: 带有location信息的第一行
        :param header: server模块的第一行
        :param field: self.full_list_nginx_info里面的每个多维度列表
        :param dict_server: 空字典
        '''
        try:
            for l_item in list_location:
                if l_item[-1] == "}":
                    np_o = np.array(list_str_nginx[location_h + header:-1])
                    eq_letter = np.where(np_o == " ".join(l_item))
                    s_tail = eq_letter[0][0]
                    for next_field in self.full_list_nginx_info:
                        np_obj = np.array(list_str_nginx)
                        eq_letter = np.where(np_obj == " ".join(next_field))
                        for i in eq_letter[0]:
                            if location_h + header < i < location_h + header + s_tail:
                                if next_field[0] == "root" or next_field[0][0:5] == "index" or next_field[0] == "proxy_pass" or \
                                        next_field[0] == "allow" or next_field[0] == "expires":
                                    location_dict[next_field[0]]=" ".join(next_field[1:])
                    dict_server["location"].append(location_dict)
                    break
        except Exception as e:
            print("get_location_info,错误原因", e)

    def get_dict_nginx_info_upstream(self):
        '''
        得到upstream的信息
        :return:
        '''
        try:
            list_str_nginx = []
            for item in self.full_list_nginx_info:
                list_str_nginx.append(" ".join(item))
            for key in self.full_list_nginx_info:
                if key[0]=="upstream":
                    upstream= self.full_list_nginx_info.index(key, 0, -1) #开头索引
                    for item in self.full_list_nginx_info[upstream:-1]:
                        if item[-1]=="}": #取到的upstream要放到location里面
                            np_object = np.array(list_str_nginx[upstream:-1])
                            eq_letter = np.where(np_object ==" ".join(item))
                            upstream_index=eq_letter[0][0] #结尾索引
                            for i in range(0,len(self.stock_nginx_data["servers"])):
                                if self.stock_nginx_data["servers"][i]["location"]:
                                    for l in range(0,len(self.stock_nginx_data["servers"][i]["location"])):
                                        if self.stock_nginx_data["servers"][i]["location"][l]["proxy_pass"]:
                                            if self.stock_nginx_data["servers"][i]["location"][l]["proxy_pass"][7:]==key[1]:
                                                self.stock_nginx_data["servers"][i]["location"][l]["upstream"]={}
                                                self.stock_nginx_data["servers"][i]["location"][l]["upstream"]["server"]=[]
                                                for item in self.full_list_nginx_info[
                                                            upstream :upstream_index + upstream]:
                                                    if item[0]=="upstream":
                                                        self.stock_nginx_data["servers"][i]["location"][l]["upstream"]["upstream_url"]=item[1]
                                                    if item[0]=="server":
                                                        self.stock_nginx_data["servers"][i]["location"][l]["upstream"][
                                                            "server"].append(item[1])
                                                break
                            break
            self.save_nginx_data()
        except Exception as e:
            print("get_dict_nginx_info_upstream,错误原因", e)

    def save_nginx_data(self):
        try:
            datatime_str = datetime.now().strftime("%Y%m%d%H%M%S")
            nginx_json = "{0}".format(self.nginx_dir)+"/{0}.json".format(datatime_str)
            json.dump(self.stock_nginx_data,open(nginx_json,"w",encoding="utf-8"))
            time.sleep(1)
        except Exception as e:
            print("没有发现文件夹")

if __name__ == '__main__':
    print(os.getcwd())
    nginx=Nginx(nginx_path=r"C:\nginx\111\nginx.conf")
    nginx.main()