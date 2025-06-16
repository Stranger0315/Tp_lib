"""
文本处理库 - 核心功能

此库提供文本处理、文件处理和矩阵操作功能，包括：
- 文本清洗、分词、词频统计和关键词提取
- 文件读取、CSV处理和元数据提取
- 矩阵操作（行、列、元素操作）、转置、过滤、排序和转换
"""

# 导入核心功能
from .core import (
    TextProcessor,
    ProcessorDecorator,
    LoggingDecorator,
    CompositeProcessor,
    ProcessorFactory,
    TextCleaner,
    TextTokenizer,
    WordCounter,
    KeywordExtractor
)

# 导入文件处理器
from .file_handlers import (
    TextFileReader,
    CSVFileReader,
    CSVColumnExtractor,
    MultiColumnCSVReader,
    FileContentToText,
    CSVToMatrix,
    FileMetadataExtractor,
    CSVContentToMatrix,
    FileBatchProcessor
)

# 导入矩阵处理器
from .matrix_handlers import (
    MatrixRowProcessor,
    MatrixColumnProcessor,
    MatrixElementProcessor,
    MatrixTransposeProcessor,
    MatrixFilterProcessor,
    MatrixSortProcessor,
    MatrixConverter,
    MatrixAggregator,
    MatrixReshaper,
    CSVToMatrixProcessor
)

# 导入异常类
from .exceptions import (
    TextProcessingError,
    UnsupportedFileTypeError,
    ProcessorNotFoundError,
    MatrixOperationError,
    FileReadError,
    InvalidInputError,
    PipelineExecutionError,
    ParameterError,
    DimensionMismatchError,
    IndexOutOfBoundsError,
    MatrixValidationError
)

# 导入API接口
from .api import TextProcessingAPI

# 注册核心文本处理器
ProcessorFactory.register("clean", TextCleaner)
ProcessorFactory.register("tokenize", TextTokenizer)
ProcessorFactory.register("word_count", WordCounter)
ProcessorFactory.register("keywords", KeywordExtractor)

# 注册文件处理器
ProcessorFactory.register("text_file", TextFileReader)
ProcessorFactory.register("csv_file", CSVFileReader)
ProcessorFactory.register("csv_extract", CSVColumnExtractor)
ProcessorFactory.register("multi_column_csv", MultiColumnCSVReader)
ProcessorFactory.register("file_to_text", FileContentToText)
ProcessorFactory.register("csv_to_matrix_file", CSVToMatrix)
ProcessorFactory.register("file_metadata", FileMetadataExtractor)
ProcessorFactory.register("csv_content_to_matrix", CSVContentToMatrix)
ProcessorFactory.register("batch_processor", FileBatchProcessor)

# 注册矩阵处理器
ProcessorFactory.register("matrix_row", MatrixRowProcessor)
ProcessorFactory.register("matrix_col", MatrixColumnProcessor)
ProcessorFactory.register("matrix_element", MatrixElementProcessor)
ProcessorFactory.register("matrix_transpose", MatrixTransposeProcessor)
ProcessorFactory.register("matrix_filter", MatrixFilterProcessor)
ProcessorFactory.register("matrix_sort", MatrixSortProcessor)
ProcessorFactory.register("matrix_convert", MatrixConverter)
ProcessorFactory.register("matrix_aggregate", MatrixAggregator)
ProcessorFactory.register("matrix_reshape", MatrixReshaper)
ProcessorFactory.register("csv_to_matrix", CSVToMatrixProcessor)

# 设置库版本
__version__ = "1.0.0"

# 提供简化的导入
__all__ = [
    "TextProcessingAPI",
    "TextProcessor",
    "ProcessorFactory",
    "TextCleaner",
    "TextTokenizer",
    "WordCounter",
    "KeywordExtractor",
    "TextFileReader",
    "CSVFileReader",
    "CSVColumnExtractor",
    "MultiColumnCSVReader",
    "FileContentToText",
    "CSVToMatrix",
    "FileMetadataExtractor",
    "CSVContentToMatrix",
    "FileBatchProcessor",
    "MatrixRowProcessor",
    "MatrixColumnProcessor",
    "MatrixElementProcessor",
    "MatrixTransposeProcessor",
    "MatrixFilterProcessor",
    "MatrixSortProcessor",
    "MatrixConverter",
    "MatrixAggregator",
    "MatrixReshaper",
    "TextProcessingError",
    "UnsupportedFileTypeError",
    "ProcessorNotFoundError",
    "MatrixOperationError",
    "FileReadError",
    "InvalidInputError",
    "PipelineExecutionError",
    "ParameterError",
    "DimensionMismatchError",
    "IndexOutOfBoundsError",
    "MatrixValidationError"
]

# 初始化日志设置
ProcessorDecorator.enable_logging(False)  # 默认关闭日志
