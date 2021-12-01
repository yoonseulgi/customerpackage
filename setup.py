from setuptools import setup, find_packages
from os import path
with open("README.md", "r") as fh:
    long_description = fh.read()
install_requires = [
    'PyYAML', 'SQLAlchemy', 'numpy', 'pandas', 'plotly'
]
setup(
    name="createcustomerinfo",
    version="0.0.1",
    author="seulgiyoon",
    description="create customer data in local database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    py_modules=['customer'],
    url="https://github.com/yoonseulgi/customerpackage.git",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=install_requires
)