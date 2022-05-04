from setuptools import setup

from rahulscripts.__version__ import __version__

setup(
    name="RahulScripts",
    version=__version__,
    description="Some daily used scripts",
    author="Rahul Brahma",
    author_email="rahul@drugonix.com",
    url="https://www.drugonix.com",
    packages=["rahulscripts"],
    install_requires =["rich"],
    entry_points={
        "console_scripts": [
            "rahulscripts.cli = rahulscripts.cli:main",
        ],
    },
)
