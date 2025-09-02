import os
import logging
import multiprocessing
from pdf2image import convert_from_path, pdfinfo_from_path
from utils import STORAGE_ROOT  # 导入路径更新

logger = logging.getLogger(__name__)


class PDF2Img:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        self.image_dir = os.path.join(STORAGE_ROOT, "pdf_images", self.pdf_name)
        os.makedirs(self.image_dir, exist_ok=True)

    def pdf_info(self) -> dict:
        """获取PDF基本信息（页数等）"""
        try:
            info = pdfinfo_from_path(self.pdf_path)
            return {"pages": info.get("Pages", 0)}
        except Exception as e:
            logger.error(f"获取PDF信息失败: {str(e)}")
            raise

    def convert_pdf(self, start_page: int, end_page: int) -> str:
        """转换指定页码范围为图片（单进程）"""
        try:
            images = convert_from_path(
                self.pdf_path,
                dpi=150,  # 分辨率（可调整清晰度）
                first_page=start_page,
                last_page=end_page,
                fmt='png',
                output_folder=self.image_dir,
                output_file=f"{start_page}-{end_page}",
                thread_count=multiprocessing.cpu_count() // 2  # 使用一半CPU核心
            )
            if not images:
                raise Exception("图片生成失败")
            return os.path.join(self.image_dir, f"{start_page}-{end_page}-0.png")
        except Exception as e:
            logger.error(f"PDF转图片失败（页码{start_page}-{end_page}）: {str(e)}")
            raise

    def convert_pdf_multiprocess(self, start: int, end: int, chunk_size: int = 5):
        """多进程批量转换PDF为图片"""
        # 生成分页任务（按chunk_size拆分）
        pages = list(range(start, end + 1))
        chunks = [pages[i:i + chunk_size] for i in range(0, len(pages), chunk_size)]
        
        # 多进程处理
        with multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(chunks))) as pool:
            # 每个进程处理一个页码块
            for chunk in chunks:
                pool.apply_async(
                    self._process_chunk,
                    args=(chunk[0], chunk[-1]),
                    error_callback=lambda e: logger.error(f"进程错误: {str(e)}")
                )
            pool.close()
            pool.join()

    def _process_chunk(self, start: int, end: int):
        """处理单个页码块的转换"""
        try:
            images = convert_from_path(
                self.pdf_path,
                dpi=150,
                first_page=start,
                last_page=end,
                fmt='png',
                thread_count=1  # 单进程内单线程避免冲突
            )
            # 保存图片（按页码命名）
            for i, image in enumerate(images, start=start):
                image_path = os.path.join(self.image_dir, f"{i}.png")
                image.save(image_path, "PNG")
            logger.debug(f"已生成第{start}-{end}页图片")
        except Exception as e:
            logger.error(f"批量转换失败（{start}-{end}页）: {str(e)}")
            raise
