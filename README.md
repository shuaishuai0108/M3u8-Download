# M3U8简介
M3U8 是 Unicode 版本的 M3U，用 UTF-8 编码。"M3U" 和 "M3U8" 文件都是苹果公司使用的 HTTP Live Streaming（HLS） 协议格式的基础，这种协议格式可以在 iPhone 和 Macbook 等设备播放。  
m3u8 文件实质是一个播放列表（playlist），其可能是一个媒体播放列表（Media Playlist），或者是一个主列表（Master Playlist）。但无论是哪种播放列表，其内部文字使用的都是 utf-8 编码。  
## M3u8-Download
* 参数  
> 多进程下载m3u8视频，以mp4格式保存  
> :param url_m3u8:m3u8视频链接  
> :param name:视频文件保存名称  
> :param path:视频文件保存地址（地址不存在会自动创建）  
## 多进程下载M3U8视频
M3U8_prosess.py  
内存占用较大，下载较稳定  
## 多线程下载M3U8视频
M3U8_threads.py  
内存占用较小，cpu占用较大  

----------

## 视频下载
movies_download.py  
可以获取最新电影电视剧的M3U8视频下载链接。  
可在此模块中直接搜索电影名称，获取视频连接后自动下载。  
下载地址可在Mvs类中self.path属性指定下载地址  

----------
*联系方式：handsomemars@outlook.com*
