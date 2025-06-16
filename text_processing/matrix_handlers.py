import json
from typing import List, Any, Optional, Dict

from .core import TextProcessor
from .exceptions import (
    MatrixOperationError, DimensionMismatchError,
    IndexOutOfBoundsError, ParameterError, MatrixValidationError
)


class MatrixValidator:
    """矩阵验证工具类"""

    @staticmethod
    def validate_matrix(matrix: List[List[Any]]):
        """验证矩阵格式是否正确"""
        if not isinstance(matrix, list):
            raise MatrixOperationError("validate", "输入必须是列表")
        if not all(isinstance(row, list) for row in matrix):
            raise MatrixOperationError("validate", "矩阵的每一行必须是列表")
            # 检查行长度一致性
        if matrix:
            first_row_len = len(matrix[0])
            for i, row in enumerate(matrix[1:], start=1):
                if len(row) != first_row_len:
                    raise MatrixValidationError("validate",
                                                f"第{i}行的长度({len(row)})与第一行长度({first_row_len})不一致")

    @staticmethod
    def validate_row_index(matrix: List[List[Any]], index: int):
        """验证行索引是否有效"""
        if index < 0 or index >= len(matrix):
            raise IndexOutOfBoundsError(
                operation="row_access",
                index=index,
                max_index=len(matrix),
                dimension_type="row"
            )

    @staticmethod
    def validate_column_index(matrix: List[List[Any]], index: int):
        """验证列索引是否有效"""
        if not matrix:
            return
        if index < 0 or index >= len(matrix[0]):
            raise IndexOutOfBoundsError(
                operation="column_access",
                index=index,
                max_index=len(matrix[0]),
                dimension_type="column"
            )

    @staticmethod
    def validate_element_index(matrix: List[List[Any]], row_index: int, col_index: int):
        """验证元素索引是否有效"""
        MatrixValidator.validate_row_index(matrix, row_index)
        MatrixValidator.validate_column_index(matrix, col_index)

    @staticmethod
    def validate_row_length(matrix: List[List[Any]], row_data: List[Any]):
        if matrix and len(row_data) != len(matrix[0]):  # matrix 非空检查
            raise DimensionMismatchError(
                operation="row_operation",
                expected_dimension=len(matrix[0]),
                actual_dimension=len(row_data),
                dimension_type="column"
            )

    @staticmethod
    def validate_column_length(matrix: List[List[Any]], column_data: List[Any]):
        """验证列长度是否匹配矩阵行数"""
        if matrix and len(column_data) != len(matrix):
            raise DimensionMismatchError(
                operation="column_operation",
                expected_dimension=len(matrix),
                actual_dimension=len(column_data),
                dimension_type="row"
            )


class MatrixRowProcessor(TextProcessor):
    """矩阵行操作处理器"""

    def __init__(self, operation: str, index: Optional[int] = None,
                 row: Optional[List[Any]] = None):
        """
        :param operation: 操作类型 ('get', 'add', 'update', 'delete')
        :param index: 行索引（用于get, update, delete）
        :param row: 行数据（用于add, update）
        """

        # 验证操作类型
        valid_operations = ['get', 'add', 'update', 'delete']
        if operation not in valid_operations:
            raise ParameterError(
                "MatrixRowProcessor",
                "operation",
                "operation",
                f"one of {valid_operations}"
            )
        self.operation = operation
        self.index = index
        self.row = row

    def process(self, matrix: List[List[Any]]) -> Any:
        """执行行操作"""
        MatrixValidator.validate_matrix(matrix)

        if self.operation == 'get':
            return self._get_row(matrix)
        elif self.operation == 'add':
            return self._add_row(matrix)
        elif self.operation == 'update':
            return self._update_row(matrix)
        elif self.operation == 'delete':
            return self._delete_row(matrix)

    def _get_row(self, matrix: List[List[Any]]) -> List[Any]:
        """获取指定行"""
        if self.index is None:
            raise ParameterError(
                processor_name="MatrixRowProcessor",
                parameter="index",
                value=None,
                expected="non-None value for 'get' operation"
            )

        MatrixValidator.validate_row_index(matrix, self.index)
        return matrix[self.index]

    def _add_row(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """添加新行"""
        if self.row is None:
            raise ParameterError(
                processor_name="MatrixRowProcessor",
                parameter="row",
                value=None,
                expected="non-None value for 'add' operation"
            )

        if matrix:  # 非空矩阵才验证长度
            MatrixValidator.validate_row_length(matrix, self.row)

        # 创建新矩阵的副本（避免修改原始矩阵）
        new_matrix = [r[:] for r in matrix]  # 复制所有行
        new_matrix.append(self.row[:])  # 添加新行
        return new_matrix

    def _update_row(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """更新指定行"""
        if self.index is None or self.row is None:
            raise ParameterError(
                processor_name="MatrixRowProcessor",
                parameter="index or row",
                value=None,
                expected="non-None values for 'update' operation"
            )

        MatrixValidator.validate_row_index(matrix, self.index)
        MatrixValidator.validate_row_length(matrix, self.row)

        # 创建新矩阵的副本（避免修改原始矩阵）
        new_matrix = [r[:] for r in matrix]  # 复制所有行
        new_matrix[self.index] = self.row[:]  # 更新指定行
        return new_matrix

    def _delete_row(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """删除指定行"""
        if self.index is None:
            raise ParameterError(
                processor_name="MatrixRowProcessor",
                parameter="index",
                value=None,
                expected="non-None value for 'delete' operation"
            )

        MatrixValidator.validate_row_index(matrix, self.index)

        # 创建新矩阵的副本（避免修改原始矩阵）
        new_matrix = []
        for i, row in enumerate(matrix):
            if i != self.index:
                new_matrix.append(row[:])  # 复制行
        return new_matrix


class MatrixColumnProcessor(TextProcessor):
    """矩阵列操作处理器"""

    def __init__(self, operation: str, index: Optional[int] = None,
                 column: Optional[List[Any]] = None):
        """
        :param operation: 操作类型 ('get', 'add', 'update', 'delete')
        :param index: 列索引（用于get, update, delete）
        :param column: 列数据（用于add, update）
        """

        # 验证操作类型
        valid_operations = ['get', 'add', 'update', 'delete']
        if operation not in valid_operations:
            raise ParameterError(
                processor_name="MatrixColumnProcessor",
                parameter="operation",
                value=operation,
                expected=f"one of {valid_operations}"
            )
        self.operation = operation
        self.index = index
        self.column = column

    def process(self, matrix: List[List[Any]]) -> Any:
        """执行列操作"""
        MatrixValidator.validate_matrix(matrix)

        if self.operation == 'get':
            return self._get_column(matrix)
        elif self.operation == 'add':
            return self._add_column(matrix)
        elif self.operation == 'update':
            return self._update_column(matrix)
        elif self.operation == 'delete':
            return self._delete_column(matrix)

    def _get_column(self, matrix: List[List[Any]]) -> List[Any]:
        """获取指定列"""
        if self.index is None:
            raise ParameterError(
                processor_name="MatrixColumnProcessor",
                parameter="index",
                value=None,
                expected="non-None value for 'get' operation"
            )

        MatrixValidator.validate_column_index(matrix, self.index)
        return [row[self.index] for row in matrix]

    def _add_column(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """添加新列"""
        if self.column is None:
            raise ParameterError(
                processor_name="MatrixColumnProcessor",
                parameter="column",
                value=None,
                expected="non-None value for 'add' operation"
            )

        MatrixValidator.validate_column_length(matrix, self.column)

        # 创建新矩阵的副本（避免修改原始矩阵）
        new_matrix = []
        for i, row in enumerate(matrix):
            new_row = row[:]  # 复制行
            new_row.append(self.column[i])  # 添加新列值
            new_matrix.append(new_row)

        # 处理空矩阵的情况
        if not matrix:
            new_matrix = [[val] for val in self.column]

        return new_matrix

    def _update_column(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """更新指定列"""
        if self.index is None or self.column is None:
            raise ParameterError(
                processor_name="MatrixColumnProcessor",
                parameter="index or column",
                value=None,
                expected="non-None values for 'update' operation"
            )

        MatrixValidator.validate_column_index(matrix, self.index)
        MatrixValidator.validate_column_length(matrix, self.column)

        # 创建新矩阵的副本（避免修改原始矩阵）
        new_matrix = []
        for i, row in enumerate(matrix):
            new_row = row[:]  # 复制行
            new_row[self.index] = self.column[i]  # 更新列值
            new_matrix.append(new_row)
        return new_matrix

    def _delete_column(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """删除指定列"""
        if self.index is None:
            raise ParameterError(
                processor_name="MatrixColumnProcessor",
                parameter="index",
                value=None,
                expected="non-None value for 'delete' operation"
            )

        MatrixValidator.validate_column_index(matrix, self.index)

        # 创建新矩阵的副本（避免修改原始矩阵）
        new_matrix = []
        for row in matrix:
            new_row = []
            for j, val in enumerate(row):
                if j != self.index:
                    new_row.append(val)
            new_matrix.append(new_row)
        return new_matrix


class MatrixElementProcessor(TextProcessor):
    """矩阵元素操作处理器"""

    def __init__(self, operation: str, row: int, column: int,
                 value: Optional[Any] = None):
        """
        :param operation: 操作类型 ('get', 'update')
        :param row: 行索引
        :param column: 列索引
        :param value: 要设置的值（用于update）
        """
        self.operation = operation
        self.row = row
        self.column = column
        self.value = value

        # 验证操作类型
        valid_operations = ['get', 'update']
        if operation not in valid_operations:
            raise ParameterError(
                processor_name="MatrixElementProcessor",
                parameter="operation",
                value=operation,
                expected=f"one of {valid_operations}"
            )

    def process(self, matrix: List[List[Any]]) -> Any:
        """执行元素操作"""
        MatrixValidator.validate_matrix(matrix)

        if self.operation == 'get':
            return self._get_element(matrix)
        elif self.operation == 'update':
            return self._update_element(matrix)

    def _get_element(self, matrix: List[List[Any]]) -> Any:
        """获取指定元素"""
        MatrixValidator.validate_element_index(matrix, self.row, self.column)
        return matrix[self.row][self.column]

    def _update_element(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """更新指定元素"""
        if self.value is None:
            raise ParameterError(
                processor_name="MatrixElementProcessor",
                parameter="value",
                value=None,
                expected="non-None value for 'update' operation"
            )

        MatrixValidator.validate_element_index(matrix, self.row, self.column)

        # 创建新矩阵的副本（避免修改原始矩阵）
        new_matrix = [r[:] for r in matrix]  # 复制所有行
        new_matrix[self.row][self.column] = self.value  # 更新元素值
        return new_matrix


class MatrixTransposeProcessor(TextProcessor):
    """矩阵转置处理器"""

    def process(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """转置矩阵（行列互换）"""
        MatrixValidator.validate_matrix(matrix)

        # 如果矩阵为空，直接返回
        if not matrix:
            return []

        # 使用列表推导式进行转置
        num_rows = len(matrix)
        num_cols = len(matrix[0])

        # 创建转置后的矩阵
        transposed = [
            [matrix[j][i] for j in range(num_rows)]
            for i in range(num_cols)
        ]

        return transposed


class MatrixFilterProcessor(TextProcessor):
    """矩阵过滤处理器"""

    def __init__(self, filter_func: callable = None,
                 filter_condition: str = None,
                 filter_value: Any = None):
        """
        :param filter_func: 自定义过滤函数 (element -> bool)
        :param filter_condition: 预设过滤条件 ('equals', 'contains', 'greater', 'less')
        :param filter_value: 过滤条件的比较值
        """
        self.filter_func = filter_func
        self.filter_condition = filter_condition
        self.filter_value = filter_value

        # 验证参数
        if filter_func is None and filter_condition is None:
            raise ParameterError(
                processor_name="MatrixFilterProcessor",
                parameter="filter_func or filter_condition",
                value=None,
                expected="at least one filtering method"
            )

    def process(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """过滤矩阵，保留满足条件的行"""
        MatrixValidator.validate_matrix(matrix)

        # 如果没有过滤条件，返回原始矩阵
        if not matrix:
            return []

        filtered_matrix = []

        for row in matrix:
            if self._should_include_row(row):
                filtered_matrix.append(row)

        return filtered_matrix

    def _should_include_row(self, row: List[Any]) -> bool:
        """判断行是否应该包含在结果中"""
        if self.filter_func:
            # 使用自定义过滤函数
            return self.filter_func(row)

        # 使用预设过滤条件
        if self.filter_condition == 'equals':
            # 行中任意元素等于过滤值
            return any(element == self.filter_value for element in row)
        elif self.filter_condition == 'contains':
            # 行中任意元素包含过滤值（字符串）
            return any(self.filter_value in str(element) for element in row)
        elif self.filter_condition == 'greater':
            # 行中任意元素大于过滤值（数值）
            return any(element > self.filter_value for element in row)
        elif self.filter_condition == 'less':
            # 行中任意元素小于过滤值（数值）
            return any(element < self.filter_value for element in row)

        # 默认包含所有行
        return True


class MatrixSortProcessor(TextProcessor):
    """矩阵排序处理器"""

    def __init__(self, column_index: int = 0,
                 ascending: bool = True,
                 sort_func: callable = None):
        """
        :param column_index: 排序列索引
        :param ascending: 是否升序排序
        :param sort_func: 自定义排序函数 (element -> key)
        """
        self.column_index = column_index
        self.ascending = ascending
        self.sort_func = sort_func

    def process(self, matrix: List[List[Any]]) -> List[List[Any]]:
        """根据指定列对矩阵进行排序"""
        MatrixValidator.validate_matrix(matrix)

        # 如果矩阵为空或只有一行，直接返回
        if len(matrix) <= 1:
            return [r[:] for r in matrix]  # 返回副本

        # 验证列索引
        MatrixValidator.validate_column_index(matrix, self.column_index)

        # 创建矩阵的副本（避免修改原始矩阵）
        sorted_matrix = [r[:] for r in matrix]

        # 获取排序键
        if self.sort_func:
            key_func = lambda row: self.sort_func(row[self.column_index])
        else:
            key_func = lambda row: row[self.column_index]

        # 执行排序
        sorted_matrix.sort(key=key_func, reverse=not self.ascending)

        return sorted_matrix


class MatrixConverter(TextProcessor):
    """矩阵转换处理器"""

    def __init__(self, output_format: str = 'list',
                 row_separator: str = '\n',
                 col_separator: str = '\t'):
        """
        :param output_format: 输出格式 ('list', 'dict', 'json', 'csv', 'text')
        :param row_separator: 行分隔符（用于文本输出）
        :param col_separator: 列分隔符（用于文本输出）
        """
        self.output_format = output_format
        self.row_separator = row_separator
        self.col_separator = col_separator

        # 验证输出格式
        valid_formats = ['list', 'dict', 'json', 'csv', 'text']
        if output_format not in valid_formats:
            raise ParameterError(
                processor_name="MatrixConverter",
                parameter="output_format",
                value=output_format,
                expected=f"one of {valid_formats}"
            )

    def process(self, matrix: List[List[Any]]) -> Any:
        """将矩阵转换为指定格式"""
        MatrixValidator.validate_matrix(matrix)

        if self.output_format == 'list':
            return [r[:] for r in matrix]  # 返回副本

        elif self.output_format == 'dict':
            return self._to_dict(matrix)

        elif self.output_format == 'json':
            # 使用已导入的json模块
            return json.dumps(self._to_dict(matrix))

        elif self.output_format == 'csv':
            return self._to_csv(matrix)

        elif self.output_format == 'text':
            return self._to_text(matrix)

    def _to_dict(self, matrix: List[List[Any]]) -> Dict[Any, List[Any]]:
        """
        将矩阵转换为字典

        使用第一列作为键，整行作为值
        """
        if not matrix:
            return {}

        # 使用第一列作为键
        result = {}
        for row in matrix:
            if row:
                key = row[0]
                result[key] = row
        return result

    def _to_csv(self, matrix: List[List[Any]]) -> str:
        """将矩阵转换为CSV格式字符串"""
        rows = []
        for row in matrix:
            # 转义包含逗号的字段
            escaped_row = []
            for item in row:
                if isinstance(item, str) and (',' in item or '\n' in item or '"' in item):
                    escaped = '"' + item.replace('"', '""') + '"'
                    escaped_row.append(escaped)
                else:
                    escaped_row.append(str(item))
            rows.append(','.join(escaped_row))
        return '\n'.join(rows)

    def _to_text(self, matrix: List[List[Any]]) -> str:
        """将矩阵转换为文本格式"""
        rows = []
        for row in matrix:
            rows.append(self.col_separator.join(map(str, row)))
        return self.row_separator.join(rows)


class MatrixAggregator(TextProcessor):
    """矩阵聚合处理器 (示例实现)"""

    def process(self, matrix: List[List[Any]]) -> Any:
        raise NotImplementedError("MatrixAggregator 需要具体实现")


class MatrixReshaper(TextProcessor):
    """矩阵重塑处理器 (示例实现)"""

    def process(self, matrix: List[List[Any]]) -> Any:
        raise NotImplementedError("MatrixReshaper 需要具体实现")


class CSVToMatrixProcessor(TextProcessor):
    """CSV到矩阵转换器 (示例实现)"""

    def process(self, input_data: str) -> List[List[Any]]:
        raise NotImplementedError("CSVToMatrixProcessor 需要具体实现")
