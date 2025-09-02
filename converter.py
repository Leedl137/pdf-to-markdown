from utils import save_md, time_it, get_image_base64  # 导入路径更新
from llm_client import ImageToMarkdownConverter  # 导入路径更新
from pdf_to_image import PDF2Img  # 导入路径更新
from prompts import SYSTEM_PROMPT, USER_PROMPT
from exceptions import DataError  # 导入路径更新
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class PDF2Markdown:
    def __init__(self, pdf_path: str, model_name: str, api_key_name: str, api_base: str = None, max_workers: int = 2):
        self.pdf_path = pdf_path
        self.pdf2img = PDF2Img(pdf_path)
        self.converter = ImageToMarkdownConverter.from_name(
            api_key_name=api_key_name,
            model_name=model_name,
            base_url=api_base
        )
        self.converter.setup(SYSTEM_PROMPT, USER_PROMPT)
        self.total_pages = self.pdf2img.pdf_info().get('pages', 0)
        self.max_workers = max_workers  # 并发数
        self.save_path = None  # 保存路径

    @time_it
    def convert(self, start: int = 1, end: int = None, output_dir: str = None) -> str:
        end = end or self.total_pages
        if start < 1 or end > self.total_pages or start > end:
            raise DataError(f"无效页码范围: {start}-{end}（总页数：{self.total_pages}）")

        logger.info(f"开始处理 {self.pdf_path}（共{self.total_pages}页）...")
        full_content = [None] * (end - start + 1)  # 用索引对应页码
        page_range = range(start, end + 1)
        temp_cache = self._get_temp_cache(start, end)  # 断点缓存

        # 1. 生成所有页面图片（批量处理更高效）
        logger.info(f"批量转换第{start}-{end}页为图片...")
        self.pdf2img.convert_pdf_multiprocess(start, end)

        # 2. 并发转换图片为Markdown（带断点续传）
        logger.info("所有图片生成完成，开始转换为Markdown...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for page in page_range:
                if temp_cache.get(page):
                    full_content[page - start] = temp_cache[page]
                    logger.info(f"已加载缓存：第{page}/{end}页")
                    continue
                # 提交任务
                future = executor.submit(self._convert_single_page, page)
                futures[future] = page

            # 处理结果
            for future in as_completed(futures):
                page = futures[future]
                try:
                    result = future.result()
                    full_content[page - start] = result
                    self._save_temp_cache(page, result)  # 保存缓存
                    logger.info(f"已完成第{page}/{end}页的Markdown转换")
                except Exception as e:
                    raise DataError(f"第{page}页LLM转换失败: {str(e)}") from e

        # 合并内容并保存
        merged_content = "\n\n".join(filter(None, full_content))
        filename = os.path.splitext(os.path.basename(self.pdf_path))[0]  # 使用原PDF文件名
        self.save_path = save_md(filename, merged_content, output_dir)
        self._clean_temp_cache()  # 转换完成后清理缓存
        return merged_content

    def _convert_single_page(self, page: int) -> str:
        """转换单页图片为Markdown"""
        image_path = os.path.join(self.pdf2img.image_dir, f"{page}.png")
        if not os.path.exists(image_path):
            raise DataError(f"第{page}页图片不存在")
        return self.converter.convert(image_path)

    def _get_temp_cache(self, start: int, end: int) -> dict:
        """获取断点缓存（临时保存已转换的页面）"""
        cache_dir = os.path.join(self.pdf2img.image_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache = {}
        for page in range(start, end + 1):
            cache_file = os.path.join(cache_dir, f"{page}.md")
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache[page] = f.read()
        return cache

    def _save_temp_cache(self, page: int, content: str):
        """保存单页转换结果到缓存"""
        cache_dir = os.path.join(self.pdf2img.image_dir, "cache")
        with open(os.path.join(cache_dir, f"{page}.md"), "w", encoding="utf-8") as f:
            f.write(content)

    def _clean_temp_cache(self):
        """转换完成后清理缓存"""
        cache_dir = os.path.join(self.pdf2img.image_dir, "cache")
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                os.remove(os.path.join(cache_dir, file))
            os.rmdir(cache_dir)
