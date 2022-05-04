from setuptools import setup

from rahulscripts.__version__ import __version__

install_requires = [
    'rich',
    'pip',
    'setuptools',
    
]


setup(
    name="RahulScripts",
    version=__version__,
    description="Some daily used scripts",
    author="Rahul Brahma",
    author_email="rahul@drugonix.com",
    download_url=f'https://github.com/Takshan/RahulScripts/{__version__}.tar.gz',
    url="https://www.drugonix.com",
    packages=["rahulscripts"],
    install_requires =install_requires,
    entry_points={
        "console_scripts": [
            "rahulscripts.cli = rahulscripts.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
