import csv
import os
from io import StringIO
from typing import Any, List, Dict, Union

from .exceptions import (
    UnsupportedFileTypeError, FileReadError, TextProcessingError,
    InvalidInputError, ParameterError
)
from .core import TextProcessor


class FileProcessor(TextProcessor):
    """文件处理基类"""

    def process(self, input_data: str):
        pass

    SUPPORTED_EXTENSIONS = []  # 子类应重写此属性

    def validate_file(self, file_path: str):
        """验证文件类型是否受支持"""
        # 确保输入是字符串
        if not isinstance(file_path, str):
            raise TypeError(f"文件路径必须是字符串，实际类型: {type(file_path)}")
        file_ext = os.path.splitext(file_path)[1].lower()
        # 处理没有扩展名的情况
        if not file_ext:
            # 如果没有扩展名但处理器支持所有类型，允许通过
            if not self.SUPPORTED_EXTENSIONS:
                return

            # 否则检查文件是否存在且是文件
            if os.path.isfile(file_path):
                return
        if self.SUPPORTED_EXTENSIONS and file_ext not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                file_ext,
                supported_types=self.SUPPORTED_EXTENSIONS
            )
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 检查是否为文件
        if not os.path.isfile(file_path):
            raise FileReadError(f"路径不是文件: {file_path}")


class TextFileReader(FileProcessor):
    """文本文件读取处理器"""

    SUPPORTED_EXTENSIONS = ['.txt', '.md', '.log', '.json', '.xml', '.yml', '.yaml']

    def __init__(self, encoding: str = 'utf-8', errors: str = 'strict'):
        self.encoding = encoding
        self.errors = errors

    def process(self, file_path: str) -> str:
        """读取文本文件内容"""
        try:
            self.validate_file(file_path)
            with open(file_path, 'r', encoding=self.encoding, errors=self.errors) as file:
                return file.read()
        except UnsupportedFileTypeError as e:
            # 直接抛出原始异常，避免嵌套
            raise e
        except Exception as e:
            if isinstance(e, UnsupportedFileTypeError):
                raise e
            raise FileReadError(file_path, error=e)


class CSVFileReader(FileProcessor):
    """CSV文件读取处理器"""

    SUPPORTED_EXTENSIONS = ['.csv']

    def __init__(self, encoding: str = 'utf-8', delimiter: str = ',',
                 has_header: bool = False):
        """
        :param encoding: 文件编码
        :param delimiter: CSV分隔符
        :param has_header: 是否有表头
        """
        self.encoding = encoding
        self.delimiter = delimiter
        self.has_header = has_header

    def process(self, file_path: str) -> List[List[str]]:
        """读取CSV文件内容"""
        try:
            self.validate_file(file_path)
            with open(file_path, 'r', encoding=self.encoding) as file:
                reader = csv.reader(file, delimiter=self.delimiter)

                # 跳过表头
                if self.has_header:
                    next(reader, None)

                # 返回所有行
                return [row for row in reader]
        except Exception as e:
            if isinstance(e, UnsupportedFileTypeError):
                raise e
            raise FileReadError(file_path, error=e)


class CSVColumnExtractor(FileProcessor):
    """CSV列提取处理器"""

    SUPPORTED_EXTENSIONS = ['.csv']

    def __init__(self, column_index: int = 0, encoding: str = 'utf-8',
                 delimiter: str = ',', has_header: bool = False,
                 output_format: str = 'text'):
        """
        :param column_index: 要提取的列索引
        :param encoding: 文件编码
        :param delimiter: CSV分隔符
        :param has_header: 是否有表头
        :param output_format: 输出格式 ('text'或'list')
        """
        self.column_index = column_index
        self.encoding = encoding
        self.delimiter = delimiter
        self.has_header = has_header
        self.output_format = output_format

        if output_format not in ['text', 'list']:  # 将 'matrix' 改为 'list'
            raise ParameterError(
                "CSVColumnExtractor",
                "output_format",
                output_format,
                "'text' or 'list'"
            )

    def process(self, file_path: str) -> Union[str, List[str]]:
        """提取CSV文件的指定列"""
        try:
            self.validate_file(file_path)
            with open(file_path, 'r', encoding=self.encoding) as file:
                reader = csv.reader(file, delimiter=self.delimiter)

                # 跳过表头
                if self.has_header:
                    next(reader, None)

                # 提取指定列
                column_data = []
                for row in reader:
                    if not row:  # 跳过空行
                        continue
                    if self.column_index < len(row):
                        column_data.append(row[self.column_index])

                # 返回以空格分隔的列数据
                if self.output_format == 'text':
                    return ' '.join(column_data)
                return column_data  # 默认返回列表

        except Exception as e:
            raise FileReadError(file_path, error=e)


class MultiColumnCSVReader(FileProcessor):
    """多列CSV读取处理器"""

    SUPPORTED_EXTENSIONS = ['.csv']

    def __init__(self, columns: List[int] = None, column_names: List[str] = None,
                 encoding: str = 'utf-8', delimiter: str = ',', has_header: bool = True):
        if columns is None and column_names is None:
            columns = []
        """
        :param columns: 要提取的列索引列表
        :param column_names: 要提取的列名列表
        :param encoding: 文件编码
        :param delimiter: CSV分隔符
        :param has_header: 是否有表头
        """
        if columns is None and column_names is None:
            columns = []  # 默认提取所有列

        self.columns = columns
        self.column_names = column_names
        self.encoding = encoding
        self.delimiter = delimiter
        self.has_header = has_header
        self.header_map = None

    def process(self, file_path: str) -> List[List[Any]]:
        """读取CSV文件并提取指定列"""
        try:
            self.validate_file(file_path)
            with open(file_path, 'r', encoding=self.encoding) as file:
                reader = csv.reader(file, delimiter=self.delimiter)
                rows = []

                # 处理表头
                if self.has_header:
                    header = next(reader, None)
                    if header:
                        self.header_map = {name: idx for idx, name in enumerate(header)}

                # 确定要提取的列
                target_indices = self._get_target_indices()

                # 读取并处理行
                for row in reader:
                    if not row:  # 跳过空行
                        continue

                    if target_indices:
                        # 提取指定列
                        selected_row = [row[i] for i in target_indices if i < len(row)]
                    else:
                        # 提取所有列
                        selected_row = row

                    rows.append(selected_row)

                return rows
        except Exception as e:
            raise FileReadError(file_path, error=e)

    def _get_target_indices(self) -> List[int]:
        """获取要提取的列索引列表"""
        if self.columns:
            return self.columns

        if self.column_names and self.header_map:
            indices = []
            for name in self.column_names:
                if name in self.header_map:
                    indices.append(self.header_map[name])
                else:
                    raise InvalidInputError("MultiColumnCSVReader", f"列名 '{name}' 不在文件中")
            return indices

        return []  # 返回空列表表示提取所有列


class FileContentToText(FileProcessor):
    """文件内容转文本处理器"""

    SUPPORTED_EXTENSIONS = ['.txt', '.md', '.log', '.csv', '.json', '.xml', '.yml', '.yaml']

    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding

    def process(self, file_path: str) -> str:
        """读取文件内容为文本"""
        try:
            self.validate_file(file_path)
            with open(file_path, 'r', encoding=self.encoding) as file:
                return file.read()
        except Exception as e:
            raise FileReadError(file_path, error=e)


class CSVToMatrix(FileProcessor):
    """CSV文件转矩阵处理器"""

    SUPPORTED_EXTENSIONS = ['.csv']

    def __init__(self, encoding: str = 'utf-8', delimiter: str = ',',
                 has_header: bool = False, skip_rows: int = 0):
        """
        :param encoding: 文件编码
        :param delimiter: CSV分隔符
        :param has_header: 是否有表头
        :param skip_rows: 跳过的行数
        """
        self.encoding = encoding
        self.delimiter = delimiter
        self.has_header = has_header
        self.skip_rows = skip_rows

    def process(self, file_path: str) -> List[List[str]]:
        """将CSV文件转换为二维矩阵"""
        try:
            self.validate_file(file_path)
            with open(file_path, 'r', encoding=self.encoding) as file:
                reader = csv.reader(file, delimiter=self.delimiter)

                # 跳过指定行数
                for _ in range(self.skip_rows):
                    next(reader, None)

                # 跳过表头
                if self.has_header:
                    next(reader, None)

                # 读取所有行
                return [row for row in reader]
        except Exception as e:
            raise FileReadError(file_path, error=e)


class FileMetadataExtractor(FileProcessor):
    """文件元数据提取处理器"""

    SUPPORTED_EXTENSIONS = []  # 支持所有文件类型

    def __init__(self, metadata_fields: List[str] = None):
        """
        :param metadata_fields: 要提取的元数据字段列表
                                (size, modified, created, extension, type)
        """
        self.metadata_fields = metadata_fields or ['size', 'modified']

    def process(self, file_path: str) -> Dict[str, Any]:
        """提取文件元数据"""
        try:
            self.validate_file(file_path)
            stats = os.stat(file_path)
            metadata = {}

            # 获取请求的元数据字段
            for field in self.metadata_fields:
                if field == 'size':
                    metadata['size'] = stats.st_size  # 文件大小（字节）
                elif field == 'modified':
                    metadata['modified'] = stats.st_mtime  # 最后修改时间
                elif field == 'created':
                    metadata['created'] = stats.st_ctime  # 创建时间
                elif field == 'extension':
                    metadata['extension'] = os.path.splitext(file_path)[1]  # 文件扩展名
                elif field == 'type':
                    metadata['type'] = 'file' if os.path.isfile(file_path) else 'directory'
                else:
                    metadata[field] = None  # 未知字段

            return metadata
        except Exception as e:
            raise FileReadError(file_path, error=e)


class FileContentProcessor:
    """文件内容处理器基类（非文件路径处理器）"""

    def process(self, content: str) -> Any:
        """处理文件内容"""
        raise NotImplementedError("子类必须实现此方法")


class CSVContentToMatrix(FileContentProcessor):
    """CSV内容转矩阵处理器"""

    def __init__(self, delimiter: str = ',', has_header: bool = False):
        """
        :param delimiter: CSV分隔符
        :param has_header: 是否有表头
        """
        self.delimiter = delimiter
        self.has_header = has_header

    def process(self, content: str) -> List[List[str]]:
        """将CSV内容转换为二维矩阵"""
        try:
            # 使用StringIO将字符串转换为类文件对象
            csv_file = StringIO(content)
            reader = csv.reader(csv_file, delimiter=self.delimiter)

            # 跳过表头
            if self.has_header:
                next(reader, None)

            # 读取所有行
            return [row for row in reader]
        except Exception as e:
            raise TextProcessingError(f"CSV内容转换失败: {str(e)}")


class FileBatchProcessor(FileProcessor):
    """文件批量处理器"""

    SUPPORTED_EXTENSIONS = []  # 支持所有文件类型

    def __init__(self, content_processor: FileContentProcessor = None,
                 file_filter: callable = None):
        """
        :param content_processor: 内容处理器
        :param file_filter: 文件过滤器函数 (file_path -> bool)
        """
        self.content_processor = content_processor
        self.file_filter = file_filter or (lambda x: True)

    def process(self, directory_path: str) -> Dict[str, Any]:
        """处理目录中的所有文件"""
        try:
            # 验证输入是否为目录
            if not os.path.isdir(directory_path):
                raise NotADirectoryError(f"不是目录: {directory_path}")

            results = {}

            # 遍历目录中的所有文件
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)

                # 跳过目录
                if not os.path.isfile(file_path):
                    continue

                # 应用文件过滤器
                if not self.file_filter(file_path):
                    continue

                # 处理文件内容
                try:
                    if self.content_processor:
                        # 读取文件内容
                        with open(file_path, 'r', encoding='utf-8') as file:
                            content = file.read()

                        # 处理内容
                        processed = self.content_processor.process(content)
                        results[file_path] = processed
                    else:
                        # 如果没有内容处理器，只记录文件路径
                        results[file_path] = None
                except Exception as e:
                    results[file_path] = {
                        "error": f"处理文件失败: {str(e)}"
                    }

            return results
        except Exception as e:
            raise FileReadError(directory_path, error=e)


# 注册处理器到工厂的辅助函数
def register_file_handlers(factory):
    """注册所有文件处理器到工厂"""
    handlers = [
        ('text_file', TextFileReader),
        ('csv_file', CSVFileReader),
        ('csv_extract', CSVColumnExtractor),
        ('multi_column_csv', MultiColumnCSVReader),
        ('file_to_text', FileContentToText),
        ('csv_to_matrix_file', CSVToMatrix),
        ('file_metadata', FileMetadataExtractor),
        ('csv_content_to_matrix', CSVContentToMatrix),
        ('batch_processor', FileBatchProcessor)
    ]

    for name, handler in handlers:
        if not factory.is_registered(name):
            factory.register(name, handler)
