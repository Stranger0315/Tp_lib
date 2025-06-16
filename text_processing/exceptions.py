from typing import Any

class TextProcessingError(Exception):
    """
    文本处理通用异常基类

    所有特定异常都应继承自此基类。
    """

    def __init__(self, message: str, *args, **kwargs):
        super().__init__(message, *args)
        self.message = message

    def __str__(self):
        return f"文本处理错误: {self.message}"


class UnsupportedFileTypeError(TextProcessingError):
    """
    不支持的文件类型异常

    当尝试处理不支持的文件类型时抛出。
    """

    def __init__(self, file_type: str, supported_types: list = None):
        message = f"不支持的文件类型: {file_type}"
        if supported_types:
            message += f"。支持的类型: {', '.join(supported_types)}"
        super().__init__(message)
        self.file_type = file_type
        self.supported_types = supported_types or []

    def __str__(self):
        return super().__str__()


class ProcessorNotFoundError(TextProcessingError):
    """
    处理器未找到异常

    当尝试使用未注册的处理器类型时抛出。
    """

    def __init__(self, processor_name: str, available_processors: list = None):
        message = f"找不到处理器: '{processor_name}'"
        if available_processors:
            message += f"。可用处理器: {', '.join(available_processors)}"
        super().__init__(message)
        self.processor_name = processor_name
        self.available_processors = available_processors or []

    def __str__(self):
        return super().__str__()


class MatrixOperationError(TextProcessingError):
    """
    矩阵操作错误

    在执行矩阵操作时发生错误时抛出。
    """

    def __init__(self, message: str, operation: str = None,
                 row: int = None, column: int = None, value: Any = None):
        super().__init__(message)
        self.operation = operation
        self.row = row
        self.column = column
        self.value = value

    def __str__(self):
        base = f"矩阵操作错误: {self.message}"
        details = []
        if self.operation:
            details.append(f"操作: {self.operation}")
        if self.row is not None:
            details.append(f"行: {self.row}")
        if self.column is not None:
            details.append(f"列: {self.column}")
        if self.value is not None:
            details.append(f"值: {self.value}")
        if details:
            base += f" [{', '.join(details)}]"
        return base


class FileReadError(TextProcessingError):
    """
    文件读取错误

    在读取文件时发生错误时抛出。
    """

    def __init__(self, file_path: str, error: Exception = None):
        message = f"读取文件 '{file_path}' 失败"
        if error:
            message += f": {str(error)}"
        super().__init__(message)
        self.file_path = file_path
        self.error = error

    def __str__(self):
        return super().__str__()


class InvalidInputError(TextProcessingError):
    """
    无效输入错误

    当处理器的输入数据不符合预期时抛出。
    """

    def __init__(self, processor_name: str, expected_type: str, actual_type: str):
        message = (f"处理器 '{processor_name}' 收到无效输入。"
                   f"预期类型: {expected_type}, 实际类型: {actual_type}")
        super().__init__(message)
        self.processor_name = processor_name
        self.expected_type = expected_type
        self.actual_type = actual_type

    def __str__(self):
        return super().__str__()


class PipelineExecutionError(TextProcessingError):
    """
    管道执行错误

    在处理管道执行过程中发生错误时抛出。
    """

    def __init__(self, step_index: int, processor_name: str, error: Exception):
        message = (f"管道处理失败 (步骤 {step_index} - 处理器 '{processor_name}')"
                   f": {str(error)}")
        super().__init__(message)
        self.step_index = step_index
        self.processor_name = processor_name
        self.error = error

    def __str__(self):
        return super().__str__()


class ParameterError(TextProcessingError):
    """
    参数错误

    当处理器参数无效时抛出。
    """

    def __init__(self, processor_name: str, parameter: str, value: Any,
                 expected: str = None):
        message = (f"处理器 '{processor_name}' 的参数 '{parameter}' 无效: "
                   f"值 '{value}'")
        if expected:
            message += f"，预期: {expected}"
        super().__init__(message)
        self.processor_name = processor_name
        self.parameter = parameter
        self.value = value
        self.expected = expected

    def __str__(self):
        return super().__str__()


class DimensionMismatchError(MatrixOperationError):
    """
    维度不匹配错误

    在矩阵操作中维度不匹配时抛出。
    """

    def __init__(self, operation: str, expected_dimension: int,
                 actual_dimension: int, dimension_type: str = "row"):
        message = (f"维度不匹配: 预期 {dimension_type} 长度为 {expected_dimension}, "
                   f"实际为 {actual_dimension}")
        super().__init__(message, operation)
        self.expected_dimension = expected_dimension
        self.actual_dimension = actual_dimension
        self.dimension_type = dimension_type

    def __str__(self):
        return super().__str__()


class IndexOutOfBoundsError(MatrixOperationError):
    """
    索引越界错误

    在矩阵操作中索引超出范围时抛出。
    """

    def __init__(self, operation: str, index: int, max_index: int,
                 dimension_type: str = "row"):
        message = (f"索引越界: {dimension_type} 索引 {index} 超出范围 "
                   f"[0, {max_index - 1}]")
        super().__init__(message, operation)
        self.index = index
        self.max_index = max_index
        self.dimension_type = dimension_type

    def __str__(self):
        return super().__str__()


class MatrixValidationError(MatrixOperationError):
    def __init__(self, operation: str, message: str):
        super().__init__(f"矩阵验证失败: {message}", operation)
