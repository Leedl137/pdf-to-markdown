import os
import base64
import time
import logging
from typing import Callable

# 动态存储路径（用户目录下）
STORAGE_ROOT = os.path.join(os.path.expanduser("~"), "pdf2md_storage")
os.makedirs(STORAGE_ROOT, exist_ok=True)
logger = logging.getLogger(__name__)


def get_image_base64(image_path: str) -> str:
    """图片转base64编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def save_md(filename: str, content: str, output_dir: str = None) -> str:
    """保存Markdown结果（支持自定义输出目录）"""
    md_dir = output_dir or os.path.join(STORAGE_ROOT, "markdown")
    os.makedirs(md_dir, exist_ok=True)
    save_path = os.path.join(md_dir, f"{filename}.md")
    
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return save_path


def time_it(func: Callable) -> Callable:
    """计时装饰器"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} 耗时: {time.time() - start:.2f}秒")
        return result
    return wrapper
