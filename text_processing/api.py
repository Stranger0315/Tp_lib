import csv
import os
from io import StringIO
from typing import List, Any

from .core import ProcessorFactory, CompositeProcessor
from .exceptions import UnsupportedFileTypeError
from .file_handlers import FileProcessor
from .matrix_handlers import MatrixValidator


class TextProcessingAPI:
    """用户友好的文本处理API接口，支持文本处理、文件处理和矩阵操作"""

    @staticmethod
    def create_pipeline(operations: list, enable_logging: bool = False, ** kwargs) -> CompositeProcessor:
        """
        创建处理管道

        :param operations: 处理步骤列表，例如 ["text_file", "clean", "keywords"]
                          可以是字符串或元组 (processor_name, params_dict)
        :param enable_logging: 是否启用处理日志
        :param kwargs: 处理器配置参数
        :return: 可执行的处理管道
        """
        pipeline = CompositeProcessor(enable_decorators=enable_logging)
        for op in operations:
            # 检查操作是否是元组 (processor_name, params)
            if isinstance(op, (list, tuple)) and len(op) == 2:
                name, op_params = op
                # 合并全局参数和操作特定参数
                params = {**kwargs, **op_params}
            else:
                name = op
                params = kwargs

            # 创建处理器并添加到管道
            processor = ProcessorFactory.create(name, **params)
            pipeline.add(processor)

        return pipeline

    @staticmethod
    def process_text(text: str, pipeline: list, **kwargs) -> Any:
        """
        处理文本字符串

        :param text: 要处理的文本
        :param pipeline: 处理步骤列表
        :param kwargs: 处理器配置参数
        :return: 处理结果
        """
        pipe = TextProcessingAPI.create_pipeline(pipeline, **kwargs)
        return pipe.process(text)

    @staticmethod
    def process_file(file_path: str, pipeline: list, file_type: str = None, **kwargs) -> Any:
        """
        处理文件内容

        :param file_path: 文件路径
        :param pipeline: 处理步骤列表
        :param file_type: 文件类型 ('text', 'csv')，如果为None则自动检测
        :param kwargs: 处理器配置参数
        :return: 处理结果
        """
        if not file_path or not isinstance(file_path, str):
            raise ValueError("文件路径无效或为空")
        # 自动检测文件类型
        if file_type is None:
            if file_path.endswith('.csv'):
                file_type = 'csv'
            elif any(file_path.endswith(ext) for ext in ['.txt', '.md', '.log']):
                file_type = 'text'
            else:
                # 尝试获取文件扩展名
                try:
                    ext = os.path.splitext(file_path)[1].lower()
                    if ext in ['.json', '.xml', '.yml', '.yaml']:
                        file_type = 'text'
                    else:
                        # 尝试读取文件内容进行检测
                        with open(file_path, 'rb') as f:
                            header = f.read(1024)
                            if b',' in header and b'\n' in header:
                                file_type = 'csv'
                            else:
                                file_type = 'text'
                except Exception:
                    raise UnsupportedFileTypeError(f"无法识别的文件类型: {file_path}")

        # 根据文件类型创建处理链
        if file_type == 'csv':
            # 对于CSV，首先添加文件阅读器，然后添加列提取器
            full_pipeline = [('csv_file', kwargs), ('csv_extract', kwargs)] + pipeline
        else:
            # 对于文本文件，添加文件阅读器
            full_pipeline = [('text_file', kwargs)] + pipeline

        # 创建处理管道
        pipe = TextProcessingAPI.create_pipeline(pipeline, ** kwargs)
        return pipe.process(file_path)

    @staticmethod
    def process_matrix(matrix: List[List[Any]], pipeline: list, **kwargs) -> Any:
        """
        对矩阵执行一系列操作

        :param matrix: 输入的二维矩阵
        :param pipeline: 处理步骤列表
        :param kwargs: 处理器配置参数
        :return: 处理结果
        """
        # 验证矩阵格式
        MatrixValidator.validate_matrix(matrix)
        pipe = TextProcessingAPI.create_pipeline(pipeline, **kwargs)
        return pipe.process(matrix)

    @staticmethod
    def matrix_to_csv(matrix: List[List[Any]], delimiter: str = ',') -> str:
        """
        将矩阵转换为CSV字符串

        :param matrix: 二维矩阵
        :param delimiter: CSV分隔符，默认为逗号
        :return: CSV格式的字符串
        """
        output = StringIO()
        writer = csv.writer(output, delimiter=delimiter)
        writer.writerows(matrix)
        return output.getvalue()

    @staticmethod
    def list_available_processors() -> List[str]:
        """列出所有可用的处理器名称"""
        return list(ProcessorFactory._registry.keys())

    @staticmethod
    def register_processor(name: str, processor_cls):
        """注册新的处理器类型"""
        ProcessorFactory.register(name, processor_cls)

    @staticmethod
    def set_logging(enabled: bool):
        """全局设置日志开关"""
        from .core import ProcessorDecorator
        ProcessorDecorator.enable_logging(enabled)

    @staticmethod
    def get_matrix_row(matrix: List[List[Any]], row_index: int) -> List[Any]:
        """
        获取矩阵的指定行

        :param matrix: 二维矩阵
        :param row_index: 行索引
        :return: 指定行的数据
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_row", {"operation": "get", "index": row_index})]
        )

    @staticmethod
    def get_matrix_column(matrix: List[List[Any]], column_index: int) -> List[Any]:
        """
        获取矩阵的指定列

        :param matrix: 二维矩阵
        :param column_index: 列索引
        :return: 指定列的数据
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_col", {"operation": "get", "index": column_index})]
        )

    @staticmethod
    def add_matrix_row(matrix: List[List[Any]], row_data: List[Any]) -> List[List[Any]]:
        """
        向矩阵添加新行

        :param matrix: 二维矩阵
        :param row_data: 要添加的行数据
        :return: 添加行后的新矩阵
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_row", {"operation": "add", "row": row_data})]
        )

    @staticmethod
    def update_matrix_row(matrix: List[List[Any]], row_index: int, row_data: List[Any]) -> List[List[Any]]:
        """
        更新矩阵的指定行

        :param matrix: 二维矩阵
        :param row_index: 行索引
        :param row_data: 新的行数据
        :return: 更新后的矩阵
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_row", {"operation": "update", "index": row_index, "row": row_data})]
        )

    @staticmethod
    def delete_matrix_row(matrix: List[List[Any]], row_index: int) -> List[List[Any]]:
        """
        删除矩阵的指定行

        :param matrix: 二维矩阵
        :param row_index: 行索引
        :return: 删除行后的新矩阵
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_row", {"operation": "delete", "index": row_index})]
        )

    @staticmethod
    def add_matrix_column(matrix: List[List[Any]], column_data: List[Any]) -> List[List[Any]]:
        """
        向矩阵添加新列

        :param matrix: 二维矩阵
        :param column_data: 要添加的列数据
        :return: 添加列后的新矩阵
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_col", {"operation": "add", "column": column_data})]
        )

    @staticmethod
    def update_matrix_column(matrix: List[List[Any]], column_index: int, column_data: List[Any]) -> List[List[Any]]:
        """
        更新矩阵的指定列

        :param matrix: 二维矩阵
        :param column_index: 列索引
        :param column_data: 新的列数据
        :return: 更新后的矩阵
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_col", {"operation": "update", "index": column_index, "column": column_data})]
        )

    @staticmethod
    def delete_matrix_column(matrix: List[List[Any]], column_index: int) -> List[List[Any]]:
        """
        删除矩阵的指定列

        :param matrix: 二维矩阵
        :param column_index: 列索引
        :return: 删除列后的新矩阵
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_col", {"operation": "delete", "index": column_index})]
        )

    @staticmethod
    def get_matrix_element(matrix: List[List[Any]], row_index: int, column_index: int) -> Any:
        """
        获取矩阵的指定元素

        :param matrix: 二维矩阵
        :param row_index: 行索引
        :param column_index: 列索引
        :return: 指定位置的元素值
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_element", {"operation": "get", "row": row_index, "column": column_index})]
        )

    @staticmethod
    def update_matrix_element(matrix: List[List[Any]], row_index: int, column_index: int, value: Any) -> List[List[Any]]:
        """
        更新矩阵的指定元素

        :param matrix: 二维矩阵
        :param row_index: 行索引
        :param column_index: 列索引
        :param value: 新的元素值
        :return: 更新后的矩阵
        """
        return TextProcessingAPI.process_matrix(
            matrix,
            [("matrix_element", {"operation": "update", "row": row_index, "column": column_index, "value": value})]
        )
