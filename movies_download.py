import requests
import json
from m3u8_threads import M3u8

# 批处理文件.bat
# copy /b *.ts ceshi.mp4

class Mvs(object):

    def __init__(self):
        self.path = r'D:\电影'
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
                        "Upgrade-Insecure-Requests": "1"}

    def run(self):
        # 1.得到电视链接
        mvs = self.mvurl_get()
        for mv in mvs:
            url = mv['url']
            path = self.path + '\\' + mv['name']
            name = mv['name'] + '_' + mv['ji']
            M3u8(url, name=name, path=path)

    def mvurl_get(self):
        inp = input('输入要查找的电视/电影：\n')
        url = 'http://api.skyrj.com/api/movies?searchKey='+inp
        req = requests.get(url, headers=self.headers).text
        mvs = json.loads(req)
        i = 0
        for mv in mvs:
            print(i,end=' #')
            name = mv['Name']
            title = mv['MovieTitle']
            tags = mv['Tags']
            year = mv['Year']
            print('%s\n%s/%s/%s\n' % (name, title, year, tags) + '-' * 50)
            i+=1

        inpt = int(input("输入序列选择:\n"))
        path_name = mvs[inpt]['Name']
        id = mvs[inpt]['ID']
        url_info = 'http://api.skyrj.com/api/movies?id=' + str(id)
        mv_info = requests.get(url_info).text
        js_info = json.loads(str(mv_info))
        # print(js_info['Introduction'])
        n = 1
        ls_mv = []
        for i in js_info['MoviePlayUrls']:
            dic_mvs = {}
            dic_mvs['name'] = path_name
            dic_mvs['ji'] = i['Name']
            dic_mvs['url'] = i['PlayUrl']
            ls_mv.append(dic_mvs)
            print(str(n) + ' /' + dic_mvs['ji'])
            n += 1

        inp_j = input('输入（返回全部链接输入-1;可按列表方式切片）:\n')
        if inp_j == '-1':
            return ls_mv
        elif ":" in inp_j:
            indexs = inp_j.split(":")
            if indexs[1] == '':
                a = int(indexs[0]) - 1
                return ls_mv[a:]
            else:
                a = int(indexs[0]) - 1
                b = int(indexs[1])
                return ls_mv[a:b]
        else:
            mv_dic = ls_mv[int(inp_j)-1]
            ls_mv = []
            ls_mv.append(mv_dic)
            return ls_mv
    
if __name__ == '__main__':
    m = Mvs()
    m.run()
    # print(m.mvurl_get())