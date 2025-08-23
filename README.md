### YTdown - YouTube视频下载工具 视频搬运工的绝活

#### 项目描述
YTdown是一个功能强大的Python命令行工具，秉承效率至上的宗旨，专为高效下载YouTube视频而设计。它不仅能下载高清视频和封面，还能自动翻译标题、整理元数据，并提供直观的进度显示。支持Windows/macOS/Linux系统，特别适合内容创作者、研究人员和视频爱好者使用。
该项目完全由DeepSeek编写，若有功能补充，可以自行解决。
还有在我自己网站上的一个小介绍：https://hicatalpa.cn/posts/48381/

#### 核心功能
🎥 **智能视频下载**
- 自动选择最佳视频+音频格式组合
- 多格式备选方案确保下载成功率
- 实时进度条显示下载状态

🌍 **标题翻译**
- 集成硅基流动API实现专业级翻译
- 保留游戏术语和技术缩写
- 支持中英文标题自动生成

📁 **元数据管理**
- 自动生成视频信息文件(info.txt)
- 保存完整JSON元数据(metadata.json)
- 智能清理文件名特殊字符

🖼️ **封面获取**
- 自动下载高清视频封面
- 失败重试机制
- 封面与视频同目录保存

🔧 **自动化配置**
- 内置FFmpeg自动下载(Windows)
- 多平台兼容处理
- 智能解决403访问限制

#### 安装方法
```bash
# 克隆仓库
git clone https://github.com/yourusername/YTdown.git

# 安装依赖
pip install -r requirements.txt

# 主要依赖
yt-dlp requests tqdm pyyaml
```

#### 使用说明
1. **配置API密钥**：
   编辑脚本，将`SILICONFLOW_API_KEY`替换为您的[硅基流动API密钥](https://www.siliconflow.com/)

2. **运行程序**：
   ```bash
   python ytdown.py
   ```

3. **输入YouTube链接**：
   ```plaintext
   请输入YouTube视频URL: https://youtu.be/example_video
   ```

4. **查看下载结果**：
   - 视频文件: `视频标题/视频标题.mp4`
   - 视频封面: `视频标题/cover.jpg`
   - 元数据: `视频标题/info.txt` 和 `视频标题/metadata.json`

#### 配置选项
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `SILICONFLOW_API_KEY` | YOUR_API_KEY | 硅基流动API密钥 |
| `FFMPEG_DOWNLOAD_URL` | GitHub最新版 | FFmpeg下载地址 |
| `USER_AGENTS` | 5个常用UA | 防403封锁的用户代理列表 |

#### 注意事项
1. 首次运行时会自动下载FFmpeg(仅Windows)
2. 非Windows系统需[手动安装FFmpeg](https://ffmpeg.org/)
3. API密钥未配置时将跳过翻译功能
4. 建议使用Python 3.8+版本

#### 故障排除
- **下载失败**：尝试重新运行，程序会自动切换下载方案
- **翻译错误**：检查API密钥配额和网络连接
- **403错误**：程序会自动轮换User-Agent重试

---
> 💡 提示：下载完成后会自动打开`info.txt`文件，按Enter键可继续下载新视频
