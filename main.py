import os
import argparse
from dotenv import load_dotenv
from converter import PDF2Markdown  # 导入路径更新
from exceptions import DataError, LLMError  # 导入路径更新
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="PDF转Markdown工具（基于豆包API）")
    parser.add_argument("--input", required=True, help="PDF文件路径或包含PDF的文件夹路径")
    parser.add_argument("--output", help="自定义输出目录（默认：用户目录/pdf2md_storage/markdown）")
    parser.add_argument("--start", type=int, default=1, help="起始页码（默认：1）")
    parser.add_argument("--end", type=int, help="结束页码（默认：最后一页）")
    parser.add_argument("--model", help="模型名称（默认：.env中的DEFAULT_MODEL）")
    parser.add_argument("--max-workers", type=int, default=2, help="并发处理数量（默认：2，避免API限流）")
    args = parser.parse_args()

    # 加载环境变量
    load_dotenv()

    # 处理输入路径（支持单文件和文件夹）
    input_paths = []
    if os.path.isdir(args.input):
        # 遍历文件夹中的PDF文件
        for filename in os.listdir(args.input):
            if filename.lower().endswith(".pdf"):
                input_paths.append(os.path.join(args.input, filename))
        if not input_paths:
            logger.error(f"未在文件夹中找到PDF文件：{args.input}")
            return
        logger.info(f"找到 {len(input_paths)} 个PDF文件，开始批量转换...")
    else:
        if not args.input.lower().endswith(".pdf") or not os.path.exists(args.input):
            logger.error(f"无效PDF文件：{args.input}")
            return
        input_paths = [args.input]

    # 批量转换
    for idx, pdf_path in enumerate(input_paths, 1):
        logger.info(f"\n===== 处理第 {idx}/{len(input_paths)} 个文件 =====")
        try:
            # 初始化转换器
            converter = PDF2Markdown(
                pdf_path=pdf_path,
                model_name=args.model or os.getenv("DEFAULT_MODEL", "doubao-seed-1-6-250615"),
                api_key_name="DOUBAO_API_KEY",
                api_base=os.getenv("DOUBAO_BASE_URL"),
                max_workers=args.max_workers
            )
            # 执行转换
            md_content = converter.convert(start=args.start, end=args.end, output_dir=args.output)
            
            # 输出结果信息
            logger.info("\n转换完成！")
            logger.info(f"结果保存路径：{converter.save_path}")
            logger.info(f"转换结果预览（前300字符）：\n{md_content[:300]}...")

        except (DataError, LLMError) as e:
            logger.error(f"{os.path.basename(pdf_path)} 转换失败: {str(e)}")
        except Exception as e:
            logger.error(f"意外错误: {str(e)}（建议检查网络或API密钥）")


if __name__ == "__main__":
    print("=" * 60)
    print("          批量PDF转Markdown工具（基于豆包API）")
    print("=" * 60)
    main()
