from os import path
from setuptools import setup

# the anchor version
__version__ = "0.0.1"

# get the absolute path of this project
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# the standard setup info
setup(
    name="anchor",
    version=__version__,
    description=("A Cosmic Ray Air Shower Creator for "
                 "the Antarctic Impulsive Transient Antenna"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rprechelt/anchor",
    author="Remy L. Prechelt",
    author_email="prechelt@hawaii.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords=["anita", "physics", "cosmic ray", "astronomy"],
    packages=["anchor"],
    python_requires=">=3.6*, <4",
    install_requires=['numpy',
                      'zhaires @ git+git://github.com/rprechelt/zhaires.py'],
    extras_require={
        "test": ["pytest", "black", "mypy",
                 "coverage", "pytest-cov", "flake8"],
    },
    scripts=["scripts/anchor"],
    project_urls={},
    include_package_data=True,
)
