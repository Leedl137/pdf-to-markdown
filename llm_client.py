import os
import json
import requests
import base64
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional
from dotenv import load_dotenv
from exceptions import LLMError  # 导入路径更新

load_dotenv()
logger = logging.getLogger(__name__)


class ImageToMarkdownConverter:
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.system_prompt = ""
        self.user_prompt = ""

        # 增强重试策略（针对429限流）
        self.session = requests.Session()
        retry_strategy = Retry(
            total=5,  # 重试5次
            backoff_factor=2,  # 指数退避（1→2→4→8秒）
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
        self.timeout = 300  # 延长超时时间（5分钟）

    @classmethod
    def from_name(cls, api_key_name: str, model_name: str, base_url: Optional[str] = None):
        api_key = os.getenv(api_key_name)
        if not api_key:
            raise LLMError(f"未找到API密钥: {api_key_name}（请检查.env文件）")
        base_url = base_url or "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        return cls(api_key, base_url, model_name)

    def setup(self, system_prompt: str, user_prompt: str):
        self.system_prompt = system_prompt.strip()
        self.user_prompt = user_prompt.strip()

    def convert(self, image_path: str) -> str:
        try:
            # 图片编码
            with open(image_path, "rb") as f:
                base64_str = base64.b64encode(f.read()).decode("utf-8")
            image_url = f"data:image/png;base64,{base64_str}"

            # 构建请求
            messages = [
                {"role": "system", "content": [{"type": "text", "text": self.system_prompt}]},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": self.user_prompt}
                ]}
            ]

            response = self.session.post(
                url=self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                data=json.dumps({
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                }, ensure_ascii=False),
                timeout=self.timeout
            )

            if response.status_code != 200:
                logger.error(f"API响应异常: {response.text}")
                raise LLMError(f"API请求失败: {response.status_code} - {response.text}")

            result = response.json()
            if not result.get("choices"):
                raise LLMError("API返回为空")

            return result["choices"][0]["message"]["content"].strip()

        except Exception as e:
            raise LLMError(f"图片转Markdown失败: {str(e)}") from e
