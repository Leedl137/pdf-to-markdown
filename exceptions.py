class PDF2MDError(Exception):
    """项目基础异常类"""
    pass


class DataError(PDF2MDError):
    """数据处理相关异常（如文件不存在、页码无效等）"""
    pass


class LLMError(PDF2MDError):
    """LLM调用相关异常（如API请求失败、返回格式错误等）"""
    pass


class ConfigError(PDF2MDError):
    """配置相关异常（如缺少API密钥、参数错误等）"""
    pass
