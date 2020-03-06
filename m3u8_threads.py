# 下载m3u8视频(多线程下载)
import re, requests, os, json, datetime
import threading
from threading import Thread
import queue
import ssl

requests.packages.urllib3.disable_warnings()

class M3u8(object):

    def __init__(self, url_m3u8, name, path):
        """
        多进程下载m3u8视频，以mp4格式保存
        :param url_m3u8:m3u8视频链接
        :param name:视频文件保存名称
        :param path:视频文件保存地址（地址不存在会自动创建）
        """
        self.url_m3u8 = url_m3u8
        self.path = path
        self.name = name
        # self.cpu_count = multiprocessing.cpu_count()   # cpu进程数，多进程使用
        self.thread_pool = 15 # 定义线程池数量
        self.start_time = datetime.datetime.now().replace(microsecond=0)
        self.error_file = self.path + '\\' + self.name + '_error.txt'  # 下载片段出错信息
        self.path_ts = self.path + '\\' + 'ts'  # 下载ts文件目录，下载完毕 后 合并删除文件
        try:
            os.makedirs(self.path_ts)
        except:
            print(self.path_ts + '：目录已存在')
        self.headers = {'Accept': '*/*',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.15 '
                                      '(KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1'}
        self.run()

    def run(self):
        # 可直接传入m3u8视频链接
        # 1.get到文件内容

        req = self.get(self.url_m3u8)

        # 2.解析出ts视频列表
        # 使用parse1返回ts列表
        ts_list = self.parse1(self.url_m3u8, req)
        if ts_list:
            print('parse1解析成功')
        if not ts_list:
            # 第一种parse1方法返回ts列表为空时，使用parse2方法
            ts_list = self.parse2(self.url_m3u8, req)
            if ts_list:
                print('parse2成功解析')
        if not ts_list:
            # 第二种parse2方法返回ts列表为空时，使用parse3方法
            ts_list = self.parse3(self.url_m3u8, req)
            if ts_list:
                print('parse3成功解析')
        if not ts_list:
            # 第二种parse3方法返回ts列表为空时，使用parse4方法
            ts_list = self.parse4(self.url_m3u8, req)
            if ts_list:
                print('parse4成功解析')

        # 3.传入ts文件列表，多进程下载ts
        self.download_process(ts_list)

        # 4. 下载出错的视频片段重新下载
        if os.path.exists(self.error_file):
            self.error()

        # 5.1 ts文件排序
        ls = os.listdir(self.path_ts)
        num_ls = []
        for i in ls:
            try:
                st = re.search(r'\d+', i).group(0)
                st = int(st)
                num_ls.append(st)
            except:
                pass
        num_ls = sorted(num_ls)
        new_ls = []

        for i in num_ls:
            new_str = str(i) + '.ts'
            new_ls.append(new_str)
        ls = new_ls
        # 5.2合并
        print('一共%d个文件' % len(ls))
        with open(self.path + '\\' + self.name + '.mp4', 'ab') as fp:
            for i in ls:
                with open(self.path_ts + '\\' + i, 'rb') as ts:
                    fp.write(ts.read())
        # 5.3删除ts文件
        for i in ls:
            os.remove(self.path_ts + '\\' + i)
        os.removedirs(self.path_ts)
        end = datetime.datetime.now().replace(microsecond=0)
        print("耗时：%s" % (end - self.start_time))

    def get(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.15 '
                                 '(KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1'}
        req = requests.get(url, headers=headers, verify=False)
        if req.status_code == 200:
            return req.text
        else:
            ex = Exception('请求状态为：',req.status_code)
            raise ex

    def parse1(self, url, req):
        # 重构方式是：链接地址去掉index.m3u8 + 匹配到的链接，不需要需要重新请求新的m3u8文件
        url_1 = url.replace(url.split('/')[-1], '')
        # 直接解析ts文件
        re_list = re.findall(r'\n(.+ts)', req)
        ts_list = []
        # 不是绝对路径的话
        if re_list:
            if 'http' not in re_list[0]:
                for i in re_list:
                    mv_url = url_1 + i
                    ts_list.append(mv_url)
                return ts_list
            # 是绝对路径的话
            else:
                ts_list = re_list
                return ts_list
        else:
            return ts_list

    def parse2(self, url, req):
        # 重构方式是：链接地址去掉index.m3u8 + 匹配到的链接，需要重新请求新的m3u8文件
        url_1 = url.replace(url.split('/')[-1], '')
        lines = req.split('\n')
        for line in lines:
            if (line[0] != '#') and (line[0] != ""):
                # print(line)
                url_2 = line
                new_url = url_1 + url_2
                # print('新链接',new_url)
                try: # 如果请求错误，返回空列表
                    req = self.get(new_url)
                    ts_list = self.parse1(new_url, req)
                    return ts_list
                except:
                    ts_list = []
                    return ts_list

    def parse3(self, url, req):
        # 构建方式为：主机名 + 匹配到的链接，需要重新请求新的m3u8文件
        url_1 = url.split('/')[0] + '//' + url.split('/')[2]
        lines = req.split('\n')
        ts_list = []
        for line in lines:
            if (line[0] != '#') and (line[0] != ""):
                url_2 = line
                new_url = url_1 + url_2
                # print('新链接',new_url)
                try: # 请求新连接正常时
                    req_new = self.get(new_url)
                    re_list = re.findall(r'\n(.+ts)', req_new)
                    if 'http' not in re_list[0]:
                        # 如果不是绝对地址的话，主机名 + 匹配到的链接重构url
                        for i in re_list:
                            mv_url = url_1 + i
                            ts_list.append(mv_url)
                        return ts_list
                    else:
                        # 如果是绝对地址的话，返回
                        ts_list = re_list
                        return ts_list
                except: # 请求新连接出错时返回空列表
                    return ts_list
                    
    def parse4(self, url, req):
        # 构建方式为：主机名 + 匹配到的链接，不需要重新请求新的m3u8文件
        url_1 = url.split('/')[0] + '//' + url.split('/')[2]
        # 直接解析ts文件
        ts_list = []
        re_list = re.findall(r'\n(.+ts)', req)
        try:
            if 'http' not in re_list[0]:
                # 如果不是绝对地址的话，主机名 + 匹配到的链接重构url
                for i in re_list:
                    mv_url = url_1 + i
                    ts_list.append(mv_url)
                return ts_list
            else:
                # 如果是绝对地址的话，返回
                ts_list = re_list
                return ts_list
        except:
            print('parse4解析出错，请检查链接是否正确，响应内容为：\n%s' % req)
            exit()

    def download_process(self, urls):
        q = queue.Queue()
        for num, url in enumerate(urls, 1):
            ts_flie_name = self.path_ts + "\\" + str(num) + '.ts'
            jindu = [num, len(urls)]
            q_dic={}
            q_dic['url'] = url
            q_dic['ts_flie_name'] = ts_flie_name
            q_dic['jindu'] = jindu
            q.put(q_dic)

        start_num = len(threading.enumerate())
        thread_pool = self.thread_pool + start_num
        while True:
            if threading.active_count() <= thread_pool:
                q_dic = q.get()
                Thread(target=self.download, args=(q_dic['url'], q_dic['ts_flie_name'], q_dic['jindu'])).start()
                if q.empty():
                    break
        while True:
            if threading.active_count() <= start_num:
                break
        print('---end---')

    def download(self, url, ts_flie_name, jindu):

        print(self.name + '：进度%d/%d' % (jindu[0] , jindu[1]), end= " ")
        print("下载:", url,'地址:',ts_flie_name)
        try:
            response = requests.get(url, stream=True, verify=False, timeout=20, headers=self.headers)
        except Exception as e:
            print("异常请求：%s" % e.args)
            error_dic = {}
            error_dic['url'] = url
            error_dic['ts_flie_name'] = ts_flie_name

            with open(self.error_file, 'a', encoding='utf-8') as fp:
                fp.write(json.dumps(error_dic, ensure_ascii=False) + "\n")
            return

        with open(ts_flie_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

    def error(self):
        print('重新下载出错视频')
        with open(self.error_file, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
        with open(self.error_file, 'a', encoding='utf-8') as fp:
            fp.write('\n' + '-' * 50 + '以上出错视频已下载' + '-' * 50)
        
        q = queue.Queue()
        for num, line in enumerate(lines, 1):
            line = line.strip()
            dic = json.loads(line)
            dic['jindu'] = [num, len(lines)]
            q.put(dic)
        
        start_num = len(threading.enumerate())
        thread_pool = self.thread_pool + start_num
        while True:
            if threading.active_count() <= thread_pool:
                q_dic = q.get()
                Thread(target=self.download, args=(q_dic['url'], q_dic['ts_flie_name'], q_dic['jindu'])).start()
                if q.empty():
                    break
        while True:
            if threading.active_count() <= start_num:
                break
        print('---end---')

if __name__ == '__main__':

    url = 'http://guihua.feifei-kuyun.com/20200112/28222_b17033ba/index.m3u8'
    name = '1'
    path = 'D:\爱情公寓5'
    m3u8 = M3u8(url, name, path)
