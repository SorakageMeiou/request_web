import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re

def is_valid_url(url):
    """检查URL是否有效"""
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_resource_type(url):
    """根据URL判断资源类型"""
    # 获取文件扩展名
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    
    # 图片类型
    image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']
    # 媒体类型
    media_exts = ['.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']
    # 文本类型
    text_exts = ['.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
    
    if ext in image_exts:
        return '图像'
    elif ext in media_exts:
        return '媒体'
    elif ext in text_exts:
        return '文本'
    else:
        return '其他'

def download_resource(url, folder):
    """下载资源到指定文件夹"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            # 从URL中提取文件名
            filename = os.path.basename(urlparse(url).path)
            if not filename:
                filename = f"resource_{hash(url)}.tmp"
            
            filepath = os.path.join(folder, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"下载成功: {filename}")
            return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
    return False

def crawl_website(url, selected_types):
    """爬取指定网站并下载选定类型的资源"""
    if not is_valid_url(url):
        print("无效的URL，请确保包含http://或https://")
        return
    
    print(f"开始爬取: {url}")
    print(f"选择的资源类型: {', '.join(selected_types)}")
    
    try:
        # 获取网页内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有资源链接
        resources = set()
        for tag in soup.find_all(['a', 'img', 'script', 'link', 'source', 'audio', 'video']):
            if tag.name == 'a' and 'href' in tag.attrs:
                resources.add(tag['href'])
            elif tag.name == 'img' and 'src' in tag.attrs:
                resources.add(tag['src'])
            elif tag.name in ['script', 'iframe'] and 'src' in tag.attrs:
                resources.add(tag['src'])
            elif tag.name == 'link' and 'href' in tag.attrs:
                resources.add(tag['href'])
            elif tag.name in ['source', 'audio', 'video'] and 'src' in tag.attrs:
                resources.add(tag['src'])
        
        # 处理并下载资源
        downloaded_count = 0
        for resource_url in resources:
            try:
                # 转换为绝对URL
                absolute_url = urljoin(url, resource_url)
                
                # 获取资源类型
                resource_type = get_resource_type(absolute_url)
                
                # 检查是否在选定的类型中
                if resource_type in selected_types:
                    print(f"找到 {resource_type} 资源: {absolute_url}")
                    if download_resource(absolute_url, resource_type):
                        downloaded_count += 1
            except Exception as e:
                print(f"处理资源 {resource_url} 时出错: {e}")
        
        print(f"爬取完成! 共下载 {downloaded_count} 个资源")
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def main():
    print("=== 网络资源爬虫 ===")
    print("请选择要爬取的资源类型:")
    print("1. 媒体 (视频/音频)")
    print("2. 图像 (图片)")
    print("3. 文本 (文档)")
    print("4. 其他")
    print("输入数字选择，多个选项用逗号分隔 (例如: 1,2,3)")
    
    type_choices = input("选择资源类型: ").strip().split(',')
    type_mapping = {
        '1': '媒体',
        '2': '图像',
        '3': '文本',
        '4': '其他'
    }
    
    selected_types = []
    for choice in type_choices:
        choice = choice.strip()
        if choice in type_mapping:
            selected_types.append(type_mapping[choice])
    
    if not selected_types:
        print("未选择任何资源类型，程序退出")
        return
    
    url = input("请输入要爬取的URL地址: ").strip()
    crawl_website(url, selected_types)

if __name__ == "__main__":
    main()