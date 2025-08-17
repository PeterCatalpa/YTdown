import os
import re
import json
import requests
import yt_dlp
import shutil
import subprocess
import platform
import zipfile
import sys
import math
import time
import random
import traceback
from urllib.parse import quote
from tqdm import tqdm

# 配置硅基流动API - 请填写您的API密钥
SILICONFLOW_API_KEY = "YOUR_API_KEY_HERE"
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"

# FFmpeg下载配置
FFMPEG_DOWNLOAD_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
FFMPEG_BIN_NAME = "ffmpeg.exe"

# 全局进度条
progress_bar = None

# 用户代理列表 - 用于解决403错误
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def clean_filename(title):
    if not title:
        return "未知标题"
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    safe_title = safe_title.replace('…', '').replace('...', '')
    return safe_title[:100]

def clean_channel_name(channel_name):
    if not channel_name:
        return "未知频道"
    return re.sub(r'[\\/*?:"<>|]', "", channel_name)

def format_duration(seconds):
    if not seconds:
        return "未知"
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    return f"{int(minutes):02d}:{int(seconds):02d}"

def format_file_size(size_bytes):
    if not size_bytes or size_bytes <= 0:
        return "未知"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    exponent = min(int(math.log(size_bytes, 1024)), len(units) - 1)
    size = size_bytes / (1024 ** exponent)
    return f"{size:.2f} {units[exponent]}"

def translate_text(text, api_key):
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("未配置硅基流动API密钥，跳过翻译")
        return text
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的游戏和技术领域翻译专家，请遵守以下规则："
                               "\n1. 保留所有数字缩写（如9B、10M、100K）不变"
                               "\n2. 保留所有游戏术语（如Spider Slayer、HYPERMAXED）不变"
                               "\n3. 只翻译句子结构和普通词汇"
                               "\n4. 保持原意准确"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        
        print(f"正在翻译文本: {text[:50]}...")
        response = requests.post(SILICONFLOW_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()
        
        print(f"翻译完成: {text} -> {translated_text}")
        return translated_text
    
    except Exception as e:
        print(f"翻译失败: {str(e)}")
        return text

def open_file_in_default_editor(file_path):
    try:
        system = platform.system()
        
        if system == "Windows":
            os.startfile(file_path)
            print(f"已在默认编辑器中打开: {file_path}")
        elif system == "Darwin":
            subprocess.run(["open", file_path], check=True)
            print(f"已在默认编辑器中打开: {file_path}")
        elif system == "Linux":
            subprocess.run(["xdg-open", file_path], check=True)
            print(f"已在默认编辑器中打开: {file_path}")
        else:
            print(f"文件路径: {file_path}")
    
    except Exception as e:
        print(f"请手动打开文件: {file_path}")

def download_ffmpeg():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_zip_path = os.path.join(script_dir, "ffmpeg.zip")
    ffmpeg_exe_path = os.path.join(script_dir, FFMPEG_BIN_NAME)
    
    try:
        print(f"开始下载FFmpeg")
        response = requests.get(FFMPEG_DOWNLOAD_URL, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024
        temp_progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, desc="下载FFmpeg")
        
        with open(ffmpeg_zip_path, 'wb') as f:
            for data in response.iter_content(block_size):
                temp_progress_bar.update(len(data))
                f.write(data)
        temp_progress_bar.close()
        
        if total_size != 0 and temp_progress_bar.n != total_size:
            print("下载不完整，请重试")
            return None
        
        print("FFmpeg下载完成")
        print("解压FFmpeg...")
        
        with zipfile.ZipFile(ffmpeg_zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith(FFMPEG_BIN_NAME):
                    zip_ref.extract(file_info, script_dir)
                    extracted_path = os.path.join(script_dir, file_info.filename)
                    if extracted_path != ffmpeg_exe_path:
                        if os.path.exists(ffmpeg_exe_path):
                            os.remove(ffmpeg_exe_path)
                        os.rename(extracted_path, ffmpeg_exe_path)
                    break
        
        os.remove(ffmpeg_zip_path)
        return ffmpeg_exe_path
    
    except Exception as e:
        print(f"FFmpeg下载失败: {str(e)}")
        return None

def get_ffmpeg_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    local_ffmpeg = os.path.join(script_dir, FFMPEG_BIN_NAME)
    if os.path.isfile(local_ffmpeg):
        return local_ffmpeg
    
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    
    if platform.system() == "Windows":
        downloaded_ffmpeg = download_ffmpeg()
        if downloaded_ffmpeg and os.path.isfile(downloaded_ffmpeg):
            return downloaded_ffmpeg
    
    print("未找到FFmpeg，视频合并功能可能受限")
    return None

def print_video_info(info):
    title = info.get('title', '未知标题')
    duration = info.get('duration', 0)
    uploader = info.get('uploader', '未知上传者')
    view_count = info.get('view_count', 0)
    upload_date = info.get('upload_date', '未知日期')
    
    if upload_date != '未知日期' and len(upload_date) == 8:
        upload_date = f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    
    best_video = None
    for fmt in info.get('formats', []):
        if fmt.get('vcodec') != 'none' and fmt.get('acodec') == 'none':
            if best_video is None or (fmt.get('width', 0) or 0) > (best_video.get('width', 0) or 0):
                best_video = fmt
    
    best_audio = None
    for fmt in info.get('formats', []):
        if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
            if best_audio is None or (fmt.get('abr', 0) or 0) > (best_audio.get('abr', 0) or 0):
                best_audio = fmt
    
    video_size = best_video.get('filesize') or best_video.get('filesize_approx') if best_video else None
    audio_size = best_audio.get('filesize') or best_audio.get('filesize_approx') if best_audio else None
    total_size = (video_size or 0) + (audio_size or 0) if video_size or audio_size else None
    
    print("\n" + "=" * 50)
    print(f"标题: {title}")
    print(f"时长: {format_duration(duration)}")
    print(f"上传者: {uploader}")
    print(f"观看次数: {view_count:,}")
    
    if best_video:
        print(f"分辨率: {best_video.get('width', '未知')}x{best_video.get('height', '未知')}")
    
    if best_audio:
        print(f"音频质量: {best_audio.get('format_note', '未知')}")
    
    print(f"估计大小: {format_file_size(total_size)}")
    print("=" * 50 + "\n")

def download_progress_hook(d):
    global progress_bar
    
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes']:
            if progress_bar is None:
                progress_bar = tqdm(
                    total=d['total_bytes'],
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="下载进度",
                    leave=False
                )
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if downloaded_bytes > progress_bar.n:
                progress_bar.update(downloaded_bytes - progress_bar.n)
    
    elif d['status'] == 'finished':
        if progress_bar:
            progress_bar.close()
            progress_bar = None

def download_with_retry(url, save_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': get_random_user_agent(),
                'Referer': 'https://www.youtube.com/'
            }
            
            response = requests.get(url, stream=True, timeout=15, headers=headers)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            temp_progress_bar = tqdm(
                total=total_size, 
                unit='iB', 
                unit_scale=True, 
                desc=f"下载封面 (尝试 {attempt+1}/{max_retries})",
                leave=False
            )
            
            with open(save_path, 'wb') as f:
                for data in response.iter_content(1024):
                    temp_progress_bar.update(len(data))
                    f.write(data)
            
            temp_progress_bar.close()
            return True
        except Exception:
            time.sleep(2)
    
    return False

def download_youtube_data():
    global progress_bar
    
    while True:
        try:
            url = input("请输入YouTube视频URL: ").strip()
            if not url:
                continue
                
            print(f"开始处理: {url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'http_headers': {'User-Agent': get_random_user_agent()}
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            print_video_info(info)
                
            original_title = info.get('title', '未知标题')
            safe_title = clean_filename(original_title)
            description = info.get('description', '无描述')
            video_id = info.get('id', '未知ID')
            
            channel_name = info.get('uploader', '未知频道')
            clean_channel = clean_channel_name(channel_name)
            
            translated_title = translate_text(original_title, SILICONFLOW_API_KEY)
            
            thumbnail_url = info.get('thumbnail', '')
            
            os.makedirs(safe_title, exist_ok=True)
            
            print("开始下载视频...")
            
            ffmpeg_path = get_ffmpeg_path()
            
            format_options = [
                'bestvideo[ext=mp4]+bestaudio/best',
                'bestvideo+bestaudio/best',
                'best[ext=mp4]',
                'best'
            ]
            
            video_downloaded = False
            for i, format_str in enumerate(format_options):
                print(f"尝试格式方案 {i+1}/{len(format_options)}: {format_str}")
                
                video_ydl_opts = {
                    'format': format_str,
                    'outtmpl': os.path.abspath(os.path.join(safe_title, f'{safe_title}.%(ext)s')),
                    'quiet': True,
                    'merge_output_format': 'mp4',
                    'ignoreerrors': True,
                    'retries': 5,
                    'fragment_retries': 5,
                    'skip_unavailable_fragments': True,
                    'progress_hooks': [download_progress_hook],
                    'http_headers': {
                        'User-Agent': get_random_user_agent(),
                        'Referer': 'https://www.youtube.com/'
                    },
                    'socket_timeout': 30
                }
                
                if ffmpeg_path:
                    video_ydl_opts['ffmpeg_location'] = ffmpeg_path
                
                progress_bar = None
                
                try:
                    with yt_dlp.YoutubeDL(video_ydl_opts) as ydl:
                        result = ydl.download([url])
                        if result == 0:
                            video_downloaded = True
                            print(f"视频下载完成 (使用方案 {i+1})")
                            break
                except Exception:
                    pass
                
                if progress_bar:
                    progress_bar.close()
                    progress_bar = None
                
                time.sleep(1)
            
            if not video_downloaded:
                print("所有格式方案均失败，无法下载视频")
                continue
            
            if thumbnail_url:
                print("开始下载封面...")
                cover_path = os.path.abspath(os.path.join(safe_title, "cover.jpg"))
                if not download_with_retry(thumbnail_url, cover_path):
                    print(f"封面下载失败，请手动下载: {thumbnail_url}")
                else:
                    print(f"封面下载完成")
            
            info_path = None
            try:
                info_path = os.path.abspath(os.path.join(safe_title, "info.txt"))
                with open(info_path, "w", encoding="utf-8") as f:
                    f.write(f"标题: {original_title}\n")
                    f.write(f"翻译标题: [{clean_channel}/转载]{translated_title}\n\n")
                    f.write(f"频道名称: {channel_name}\n")
                    f.write(f"视频ID: {video_id}\n\n")
                    f.write(f"URL: {url}\n\n")
                    f.write(f"原视频简介：\n{description}")
                print(f"元数据保存完成")
            except Exception as e:
                print(f"元数据保存失败: {str(e)}")
            
            try:
                json_path = os.path.abspath(os.path.join(safe_title, "metadata.json"))
                with open(json_path, "w", encoding="utf-8") as f:
                    info['translated_title'] = translated_title
                    json.dump(info, f, indent=2, ensure_ascii=False)
                print(f"JSON元数据保存完成")
            except Exception as e:
                print(f"JSON元数据保存失败: {str(e)}")
            
            print(f"所有内容已保存到文件夹: {os.path.abspath(safe_title)}")
            
            if info_path and os.path.exists(info_path):
                print("正在打开info.txt文件...")
                open_file_in_default_editor(info_path)
            
            print("下载任务已完成！按Enter继续下载其他视频，或按Ctrl+C退出")
            
        except Exception as e:
            print(f"发生错误: {str(e)}")
            if progress_bar:
                progress_bar.close()
                progress_bar = None

def display_ytdown_logo():
    """显示YTdown字符艺术并应用YouTube配色（红白配色）"""
    # 检查系统是否支持ANSI颜色代码
    if platform.system() == 'Windows':
        # 启用Windows ANSI支持
        os.system('color')
    
    # YouTube品牌色：红色(#FF0000)和白色(#FFFFFF)
    # 使用ANSI转义序列设置颜色
    RED = "\033[91m"    # 亮红色
    WHITE = "\033[97m"  # 亮白色
    RESET = "\033[0m"   # 重置颜色
    
    # 欢迎提示语
    welcome_message = f"{WHITE}欢迎使用YTdown！{RESET}"
    
    # 字符艺术（使用原始字符串避免转义序列警告）
    logo = rf"""{RED}
,--.   ,--. ,--------. {WHITE}   ,--.                              {RED}
 \  `.'  /  '--.  .--' {WHITE} ,-|  |  ,---.  ,--.   ,--. ,--,--,  {RED}
  '.    /      |  |    {WHITE}' .-. | | .-. | |  |.'.|  | |      \ {RED}
    |  |       |  |    {WHITE}\ `-' | ' '-' ' |   .'.   | |  ||  | {RED}
    `--'       `--'    {WHITE} `---'   `---'  '--'   '--' `--''--' 
{RESET}"""
    
    # 显示欢迎提示和字符艺术
    print(welcome_message)
    print(logo)

if __name__ == "__main__":
    # 显示欢迎提示和YTdown字符艺术
    display_ytdown_logo()
    
    try:
        from tqdm import tqdm
    except ImportError:
        print("安装tqdm库以显示下载进度...")
        subprocess.run([sys.executable, "-m", "pip", "install", "tqdm"], check=True)
        from tqdm import tqdm
    
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        print(f"FFmpeg可用: {ffmpeg_path}")
    
    if SILICONFLOW_API_KEY == "YOUR_API_KEY_HERE":
        print("未设置硅基流动API密钥，跳过翻译功能")
    
    try:
        download_youtube_data()
    except KeyboardInterrupt:
        print("\nBye!")
    except Exception as e:
        print(f"\n发生未处理的错误: {str(e)}")