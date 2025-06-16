from abc import ABC, abstractmethod
from .exceptions import ProcessorNotFoundError, InvalidInputError


class TextProcessor(ABC):
    """文本处理器抽象基类"""

    @abstractmethod
    def process(self, input_data: str):
        pass


class LoggingDecorator(TextProcessor):
    """日志装饰器实现"""
    _logging_enabled = True

    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    @classmethod
    def enable_logging(cls, enabled: bool):
        cls._logging_enabled = enabled

    def process(self, input_data: str):
        if self._logging_enabled:
            print(f"[LOG] Entering: {type(self._wrapped).__name__}")
            print(f"[LOG] Input: {input_data[:50]}{'...' if len(input_data) > 50 else ''}")

        result = self._wrapped.process(input_data)

        if self._logging_enabled:
            print(f"[LOG] Result: {str(result)[:50]}{'...' if len(str(result)) > 50 else ''}")
            print(f"[LOG] Exiting: {type(self._wrapped).__name__}")
        return result


ProcessorDecorator = LoggingDecorator  # 保持别名兼容性


class CompositeProcessor(TextProcessor):
    """组合模式实现"""

    def __init__(self, enable_decorators=False):
        self.processors = []
        self.enable_decorators = enable_decorators

    def add(self, processor: TextProcessor):
        """添加处理器到处理链"""
        if self.enable_decorators:
            self.processors.append(LoggingDecorator(processor))
        else:
            self.processors.append(processor)

    def process(self, input_data: str):
        """执行处理链中的所有处理器"""
        current_data = input_data
        for processor in self.processors:
            current_data = processor.process(current_data)
        return current_data


class ProcessorFactory:
    _registry = {}
    _lazy_registry = {}

    @classmethod
    def register(cls, name: str, processor_cls):
        """注册新处理器类型"""
        cls._registry[name] = processor_cls

    @classmethod
    def lazy_register(cls, name: str, processor_cls):
        """延迟注册处理器类型"""
        cls._lazy_registry[name] = processor_cls

    @classmethod
    def create(cls, name: str, **kwargs) -> TextProcessor:
        """创建处理器实例"""
        if name in cls._lazy_registry:
            cls.register(name, cls._lazy_registry[name])
            del cls._lazy_registry[name]

        if name not in cls._registry:
            raise ProcessorNotFoundError(f"未知处理器: {name}")
        return cls._registry[name](**kwargs)

    @classmethod
    def get_registry(cls):
        """获取注册表字典副本"""
        return cls._registry.copy()

    @classmethod
    def is_registered(cls, name: str):
        """检查处理器是否已注册"""
        return name in cls._registry

    @property
    def registry(self):
        return self._registry


class TextCleaner(TextProcessor):
    def process(self, text: str):
        return ''.join(c for c in text if c.isalnum() or c.isspace())


class TextTokenizer(TextProcessor):
    def process(self, text: str):
        return text.split()


class WordCounter(TextProcessor):
    def process(self, text: str):
        words = text.split()
        return {word: words.count(word) for word in set(words)}


class KeywordExtractor(TextProcessor):
    def __init__(self, top_k=5):
        self.top_k = top_k

    def process(self, input_data):
        """处理字符串或单词列表"""
        if isinstance(input_data, str):
            words = input_data.split()
        elif isinstance(input_data, list):
            words = input_data
        else:
            raise InvalidInputError(
                "KeywordExtractor",
                "str or list",
                str(type(input_data))
            )

        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:self.top_k]]