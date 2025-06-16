import unittest
import os
import tempfile
import csv

from text_processing import (
    TextProcessingAPI,
    TextCleaner,
    TextTokenizer,
    WordCounter,
    KeywordExtractor,
    TextFileReader,
    CSVFileReader,
    CSVColumnExtractor,
    MatrixRowProcessor,
    MatrixColumnProcessor,
    MatrixElementProcessor,
    MatrixTransposeProcessor,
    MatrixConverter,
    TextProcessingError,
    UnsupportedFileTypeError,
    ProcessorNotFoundError,
    CompositeProcessor
)


class TestCoreTextProcessing(unittest.TestCase):
    """测试核心文本处理功能"""

    def setUp(self):
        self.sample_text = "Hello, World! This is a test. 12345"
        self.clean_text = "Hello World This is a test 12345"

    def test_text_cleaner(self):
        cleaner = TextCleaner()
        result = cleaner.process(self.sample_text)
        self.assertEqual(result, self.clean_text)

    def test_text_tokenizer(self):
        tokenizer = TextTokenizer()
        result = tokenizer.process(self.clean_text)
        self.assertEqual(result, ["Hello", "World", "This", "is", "a", "test", "12345"])

    def test_word_counter(self):
        counter = WordCounter()
        text = "apple banana apple orange banana apple"
        result = counter.process(text)
        self.assertEqual(result, {"apple": 3, "banana": 2, "orange": 1})

    def test_keyword_extractor(self):
        extractor = KeywordExtractor(top_k=2)
        text = "python is great and python is powerful"
        result = extractor.process(text)
        self.assertEqual(result, ["python", "is"])

        # 测试列表输入
        words = ["python", "is", "great", "python", "is", "powerful"]
        result = extractor.process(words)
        self.assertEqual(result, ["python", "is"])


class TestFileProcessing(unittest.TestCase):
    """测试文件处理功能"""

    def setUp(self):
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()

        # 创建文本文件
        self.text_file = os.path.join(self.temp_dir.name, "test.txt")
        with open(self.text_file, "w", encoding="utf-8") as f:
            f.write("Line 1\nLine 2\nLine 3")

        # 创建没有扩展名的文本文件
        self.no_ext_file = os.path.join(self.temp_dir.name, "no_extension")
        with open(self.no_ext_file, "w", encoding="utf-8") as f:
            f.write("No extension file content")

        # 创建CSV文件
        self.csv_file = os.path.join(self.temp_dir.name, "test.csv")
        with open(self.csv_file, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Age", "City"])
            writer.writerow(["Alice", "30", "New York"])
            writer.writerow(["Bob", "25", "London"])
            writer.writerow(["Charlie", "35", "Paris"])

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_text_file_reader(self):
        reader = TextFileReader()
        result = reader.process(self.text_file)
        self.assertEqual(result, "Line 1\nLine 2\nLine 3")

    def test_csv_file_reader(self):
        reader = CSVFileReader(has_header=True)
        result = reader.process(self.csv_file)
        self.assertEqual(result, [
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Charlie", "35", "Paris"]
        ])

    def test_csv_column_extractor(self):
        # 提取第二列
        extractor = CSVColumnExtractor(column_index=1, has_header=True, output_format='list')
        result = extractor.process(self.csv_file)
        self.assertEqual(result, ["30", "25", "35"])

        # 提取文本格式
        extractor_text = CSVColumnExtractor(column_index=1, has_header=True, output_format='text')
        result_text = extractor_text.process(self.csv_file)
        self.assertEqual(result_text, "30 25 35")

    def test_no_extension_file(self):
        reader = TextFileReader()
        result = reader.process(self.no_ext_file)
        self.assertEqual(result, "No extension file content")

    def test_unsupported_file_type(self):
        invalid_file = os.path.join(self.temp_dir.name, "test.invalid")
        with open(invalid_file, "w") as f:
            f.write("Test content")

        reader = TextFileReader()
        with self.assertRaises(UnsupportedFileTypeError):
            reader.process(invalid_file)


class TestMatrixProcessing(unittest.TestCase):
    """测试矩阵处理功能"""

    def setUp(self):
        self.matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

    def test_row_processor(self):
        # 获取行
        row_get = MatrixRowProcessor(operation="get", index=1)
        self.assertEqual(row_get.process(self.matrix), [4, 5, 6])

        # 添加行
        row_add = MatrixRowProcessor(operation="add", row=[10, 11, 12])
        result = row_add.process(self.matrix)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[3], [10, 11, 12])

        # 更新行
        row_update = MatrixRowProcessor(operation="update", index=0, row=[0, 0, 0])
        result = row_update.process(self.matrix)
        self.assertEqual(result[0], [0, 0, 0])

        # 删除行
        row_delete = MatrixRowProcessor(operation="delete", index=1)
        result = row_delete.process(self.matrix)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], [1, 2, 3])
        self.assertEqual(result[1], [7, 8, 9])

    def test_column_processor(self):
        # 获取列
        col_get = MatrixColumnProcessor(operation="get", index=1)
        self.assertEqual(col_get.process(self.matrix), [2, 5, 8])

        # 添加列
        col_add = MatrixColumnProcessor(operation="add", column=[10, 11, 12])
        result = col_add.process(self.matrix)
        self.assertEqual(len(result[0]), 4)
        self.assertEqual([row[3] for row in result], [10, 11, 12])

        # 更新列
        col_update = MatrixColumnProcessor(operation="update", index=0, column=[0, 0, 0])
        result = col_update.process(self.matrix)
        self.assertEqual([row[0] for row in result], [0, 0, 0])

        # 删除列
        col_delete = MatrixColumnProcessor(operation="delete", index=1)
        result = col_delete.process(self.matrix)
        self.assertEqual(len(result[0]), 2)
        self.assertEqual([row[0] for row in result], [1, 4, 7])
        self.assertEqual([row[1] for row in result], [3, 6, 9])

    def test_element_processor(self):
        # 获取元素
        elem_get = MatrixElementProcessor(operation="get", row=1, column=1)
        self.assertEqual(elem_get.process(self.matrix), 5)

        # 更新元素
        elem_update = MatrixElementProcessor(operation="update", row=0, column=0, value=10)
        result = elem_update.process(self.matrix)
        self.assertEqual(result[0][0], 10)

    def test_transpose_processor(self):
        transposer = MatrixTransposeProcessor()
        result = transposer.process(self.matrix)
        self.assertEqual(result, [
            [1, 4, 7],
            [2, 5, 8],
            [3, 6, 9]
        ])

    def test_matrix_converter(self):
        converter = MatrixConverter(output_format="text", row_separator="|", col_separator=",")
        result = converter.process(self.matrix)
        self.assertEqual(result, "1,2,3|4,5,6|7,8,9")

        converter_json = MatrixConverter(output_format="json")
        result = converter_json.process(self.matrix)
        self.assertEqual(result, '{"1": [1, 2, 3], "4": [4, 5, 6], "7": [7, 8, 9]}')


class TestAPI(unittest.TestCase):
    """测试API接口"""

    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.no_ext_file = None

    def setUp(self):
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()

        # 创建文本文件
        self.text_file = os.path.join(self.temp_dir.name, "api_test.txt")
        with open(self.text_file, "w", encoding="utf-8") as f:
            f.write("Hello, world! This is an API test.")

        # 创建CSV文件
        self.csv_file = os.path.join(self.temp_dir.name, "api_test.csv")
        with open(self.csv_file, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Value"])
            writer.writerow(["A1", "100"])
            writer.writerow(["B2", "200"])
            writer.writerow(["C3", "300"])

        # 添加没有扩展名的文件
        self.no_ext_file = os.path.join(self.temp_dir.name, "no_extension")
        with open(self.no_ext_file, "w", encoding="utf-8") as f:
            f.write("No extension API test content")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_text_processing_pipeline(self):
        # 文本处理管道：清洗 -> 分词 -> 关键词提取
        pipeline = ["clean", "tokenize", ("keywords", {"top_k": 3})]
        result = TextProcessingAPI.process_text("Python is great. I love Python programming.", pipeline)
        self.assertEqual(result, ["Python", "is", "great"])

    def test_file_processing_pipeline(self):
        # 文件处理管道：读取文件 -> 清洗 -> 分词
        pipeline = [
            ("text_file", {"encoding": "utf-8"}),
            "clean",
            "tokenize"
        ]

        # 测试带扩展名的文本文件
        result = TextProcessingAPI.process_file(self.text_file, pipeline)
        self.assertEqual(result, ["Hello", "world", "This", "is", "an", "API", "test"])

        # 测试没有扩展名的文件
        result = TextProcessingAPI.process_file(self.no_ext_file, pipeline)
        self.assertEqual(result, ["No", "extension", "API", "test", "content"])

    def test_csv_processing_pipeline(self):
        # CSV处理管道：读取CSV -> 提取第二列
        pipeline = [
            ("csv_extract", {"column_index": 1, "has_header": True, "output_format": "list"})
        ]
        result = TextProcessingAPI.process_file(self.csv_file, pipeline)
        self.assertEqual(result, ["100", "200", "300"])

        # 测试完整的CSV处理管道
        full_pipeline = [
            ("csv_file", {"has_header": True}),  # 读取CSV文件
            ("matrix_col", {"operation": "get", "index": 1})  # 获取第二列
        ]
        result = TextProcessingAPI.process_file(self.csv_file, full_pipeline)
        self.assertEqual(result, ["100", "200", "300"])

    def test_matrix_processing_pipeline(self):
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

        # 矩阵处理管道：转置 -> 获取第二行
        pipeline = [
            ("matrix_transpose", {}),
            ("matrix_row", {"operation": "get", "index": 1})
        ]

        result = TextProcessingAPI.process_matrix(matrix, pipeline)
        self.assertEqual(result, [2, 5, 8])

    def test_api_matrix_operations(self):
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

        # 测试行操作
        self.assertEqual(TextProcessingAPI.get_matrix_row(matrix, 1), [4, 5, 6])

        # 添加行
        added_matrix = TextProcessingAPI.add_matrix_row(matrix, [10, 11, 12])
        self.assertEqual(len(added_matrix), 4)
        self.assertEqual(added_matrix[3], [10, 11, 12])

        # 更新行
        updated_matrix = TextProcessingAPI.update_matrix_row(matrix, 0, [0, 0, 0])
        self.assertEqual(updated_matrix[0], [0, 0, 0])

        # 删除行
        deleted_matrix = TextProcessingAPI.delete_matrix_row(matrix, 1)
        self.assertEqual(len(deleted_matrix), 2)
        self.assertEqual(deleted_matrix[0], [1, 2, 3])
        self.assertEqual(deleted_matrix[1], [7, 8, 9])

        # 测试列操作
        self.assertEqual(TextProcessingAPI.get_matrix_column(matrix, 1), [2, 5, 8])

        # 添加列
        added_col_matrix = TextProcessingAPI.add_matrix_column(matrix, [10, 11, 12])
        self.assertEqual(len(added_col_matrix[0]), 4)
        self.assertEqual([row[3] for row in added_col_matrix], [10, 11, 12])

        # 更新列
        updated_col_matrix = TextProcessingAPI.update_matrix_column(matrix, 0, [0, 0, 0])
        self.assertEqual([row[0] for row in updated_col_matrix], [0, 0, 0])

        # 删除列
        deleted_col_matrix = TextProcessingAPI.delete_matrix_column(matrix, 1)
        self.assertEqual(len(deleted_col_matrix[0]), 2)
        self.assertEqual([row[0] for row in deleted_col_matrix], [1, 4, 7])
        self.assertEqual([row[1] for row in deleted_col_matrix], [3, 6, 9])

        # 测试元素操作
        self.assertEqual(TextProcessingAPI.get_matrix_element(matrix, 1, 1), 5)
        updated_element_matrix = TextProcessingAPI.update_matrix_element(matrix, 0, 0, 10)
        self.assertEqual(updated_element_matrix[0][0], 10)

    def test_create_pipeline(self):
        pipeline = TextProcessingAPI.create_pipeline([
            "clean",
            ("tokenize", {})
        ])
        self.assertIsInstance(pipeline, CompositeProcessor)
        self.assertEqual(len(pipeline.processors), 2)

        result = pipeline.process("Hello, world!")
        self.assertEqual(result, ["Hello", "world"])

    def test_processor_not_found(self):
        with self.assertRaises(ProcessorNotFoundError):
            TextProcessingAPI.process_text("test", ["invalid_processor"])

    def test_matrix_conversion(self):
        matrix = [
            ["Name", "Age"],
            ["Alice", 30],
            ["Bob", 25]
        ]
        csv_str = TextProcessingAPI.matrix_to_csv(matrix)
        self.assertEqual(csv_str, "Name,Age\r\nAlice,30\r\nBob,25\r\n")

    def test_list_processors(self):
        processors = TextProcessingAPI.list_available_processors()
        self.assertIn("clean", processors)
        self.assertIn("csv_file", processors)
        self.assertIn("matrix_transpose", processors)

    def test_register_new_processor(self):
        # 创建一个新的处理器
        class UppercaseProcessor:
            def process(self, text):
                return text.upper()

        # 注册新处理器
        TextProcessingAPI.register_processor("uppercase", UppercaseProcessor)

        # 验证注册成功
        self.assertIn("uppercase", TextProcessingAPI.list_available_processors())

        # 使用新处理器
        pipeline = ["uppercase"]
        result = TextProcessingAPI.process_text("hello", pipeline)
        self.assertEqual(result, "HELLO")

    def test_logging(self):
        # 启用日志
        TextProcessingAPI.set_logging(True)

        # 创建一个简单的管道
        pipeline = TextProcessingAPI.create_pipeline([
            "clean",
            "tokenize"
        ])

        # 处理文本（日志将输出到控制台）
        result = pipeline.process("Hello, world!")
        self.assertEqual(result, ["Hello", "world"])

        # 关闭日志
        TextProcessingAPI.set_logging(False)


class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""

    def test_invalid_matrix(self):
        invalid_matrix = [[1, 2, 3], [4, 5], [6, 7, 8]]  # 第二行只有2个元素

        with self.assertRaises(TextProcessingError):
            TextProcessingAPI.process_matrix(invalid_matrix, [("matrix_row", {"operation": "get", "index": 0})])

    def test_invalid_index(self):
        matrix = [[1, 2], [3, 4]]

        with self.assertRaises(TextProcessingError):
            TextProcessingAPI.get_matrix_row(matrix, 2)  # 索引越界

    def test_invalid_file_path(self):
        pipeline = [("text_file", {})]

        with self.assertRaises(TextProcessingError):
            TextProcessingAPI.process_file("invalid_path.txt", pipeline)


if __name__ == "__main__":
    unittest.main()
