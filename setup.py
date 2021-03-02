from setuptools import setup, find_packages
import glob
import os

this_directory = os.path.abspath(os.path.dirname(__file__))

def read_file(filename):
    with open(os.path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

setup(
    name="showdata",
    version="1.3.1",
    author="Dechao Meng",
    url="https://github.com/silverbulletmdc/showdata",
    author_email="dechao.meng@vipl.ict.ac.cn",
    description="Large scale image dataset visiualization tool.",
    long_description_content_type="text/markdown",
    long_description=open("README.rst").read(),
    packages=find_packages(exclude=('examples', 'examples.*')),
    scripts=glob.glob('scripts/*'),
    install_requires=['click', 'pandas']
)
