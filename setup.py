from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="text_processing_lib",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive text processing library with file and matrix operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/text_processing_lib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "coverage>=5.0",
        ],
    },
    include_package_data=True,
)