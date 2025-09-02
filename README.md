# PDF to Markdown Converter

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

一个较为完善的PDF转Markdown工具，基于豆包API实现，支持批量转换、格式保留和断点续传，适合处理学术论文、技术文档等包含复杂格式的PDF文件。

## 功能特点

- **批量处理**：支持单个PDF文件和文件夹内所有PDF批量转换
- **格式精准**：保留标题层级、公式、表格、列表等复杂格式
- **断点续传**：转换中断后可从上次进度继续，避免重复工作
- **并发控制**：可调节并发数，平衡转换速度与API限流
- **自定义输出**：支持指定页码范围和输出目录
- **跨平台兼容**：完美支持Windows、macOS和Linux系统

## 安装指南

### 前置要求
- Python 3.8 及以上版本
- 网络连接（用于调用豆包API）
- Poppler（PDF转图片依赖）

### 步骤1：获取代码# 克隆仓库
git clone https://github.com/your-username/pdf2markdown-converter.git
cd pdf2markdown-converter

# 或直接下载ZIP压缩包并解压
### 步骤2：安装Python依赖# 创建并激活虚拟环境（推荐）
python -m venv venv

# Windows激活虚拟环境
venv\Scripts\activate

# macOS/Linux激活虚拟环境
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
### 步骤3：安装Poppler
Poppler是PDF转图片的必要依赖，不同系统安装方法如下：

- **Windows**：
  1. 从 [Poppler官网](https://github.com/oschwartz10612/poppler-windows/releases/) 下载最新版本
  2. 解压到任意目录（如 `C:\poppler`）
  3. 将 `poppler-xx\bin` 目录添加到系统环境变量PATH中
  4. 重启命令行工具使配置生效

- **macOS**：
  ```bash
  brew install poppler
  ```

- **Linux**：
  ```bash
  sudo apt-get install poppler-utils
  ```

### 步骤4：配置API密钥
1. 复制环境变量示例文件：
   ```bash
   # Windows (cmd)
   copy .env.example .env
   
   # Windows (PowerShell)
   Copy-Item .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

2. 编辑 `.env` 文件，填入你的豆包API密钥：
   ```env
   DOUBAO_API_KEY=你的豆包API密钥
   DEFAULT_MODEL=doubao-seed-1-6-250615
   # 可选：自定义API地址
   # DOUBAO_BASE_URL=https://api.example.com/v3/chat/completions
   ```


## 使用方法

### 基本命令格式python main.py --input "输入路径" [可选参数]
### 示例1：转换单个PDF文件# 转换整个PDF文件
python main.py --input "C:\Documents\论文.pdf"

# 转换PDF的第1-10页
python main.py --input "C:\Documents\论文.pdf" --start 1 --end 10

# 转换并指定输出目录
python main.py --input "C:\Documents\论文.pdf" --output "C:\Output\Markdown"
### 示例2：批量转换文件夹中的PDF# 转换文件夹中所有PDF
python main.py --input "C:\Documents\所有论文"

# 批量转换并调整并发数（API限流时使用）
python main.py --input "C:\Documents\所有论文" --max-workers 1
### 所有支持的参数
| 参数 | 说明 | 必需 |
|------|------|------|
| `--input` | PDF文件路径或包含PDF的文件夹路径 | 是 |
| `--output` | 自定义输出目录路径 | 否 |
| `--start` | 起始页码（默认为1） | 否 |
| `--end` | 结束页码（默认为最后一页） | 否 |
| `--model` | 指定使用的豆包模型 | 否 |
| `--max-workers` | 并发处理数量（默认为2） | 否 |

## 输出说明

- 转换后的Markdown文件默认保存位置：
  - Windows: `C:\Users\你的用户名\pdf2md_storage\markdown`
  - macOS/Linux: `~/pdf2md_storage/markdown`
  
- 临时图片文件会自动保存在：
  - `pdf2md_storage/pdf_images` 目录，转换完成后会自动清理

## 常见问题

### 1. 运行时提示"缺少--input参数"
这表示你没有指定需要转换的PDF文件或文件夹，解决方法：python main.py --input "你的PDF路径"
### 2. API限流错误（429错误）
豆包API有调用频率限制，可通过以下方法解决：
- 降低并发数：`--max-workers 1`
- 等待一段时间后再试
- 登录豆包平台调整模型调用限额

### 3. 图片生成失败
- 检查Poppler是否正确安装并添加到环境变量
- 确认PDF文件未损坏且可以正常打开
- 尝试重启电脑使环境变量配置生效

### 4. 公式或表格转换异常
- 尝试使用更高版本的模型：`--model "doubao-pro"`
- 提高PDF转图片的清晰度（修改`pdf_to_image.py`中的`dpi`参数为300）

## 许可证
本项目采用MIT许可证开源，详情参见 [LICENSE](LICENSE) 文件。

## 致谢
- 基于 [豆包API](https://www.doubao.com/) 实现图片转Markdown功能
- 使用 [pdf2image](https://github.com/Belval/pdf2image) 处理PDF转图片
