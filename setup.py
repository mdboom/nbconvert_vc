#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
nbconvert plugin for an experimental Jupyter notebook file format based on
YAML.

BSD 3-clause licensed.

Michael Droettboom <mdroettboom@mozilla.com>
"""

__author__ = "Michael Droettboom"
__email__ = "mdroettboom@mozilla.com"
__version__ = "0.1"
name = 'nbconvert_vc'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name=name,
    version=__version__,
    author=__author__,
    email=__email__,
    description='An experimental Jupyter notebook file format based on YAML',
    long_description=long_description,
    license='OSI Approved :: BSD License',
    url="TODO",
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 1 - Beta',
        'Natural Language :: English',
        'Framework :: Jupyter'
    ],
    entry_points={
        'nbconvert.exporters': [
            'vc = %s:VCExporter' % name,
            'vc_notebook = %s:VCImporter' % name
        ],
    },
    packages=[name],
    install_requires=['nbconvert'],
    python_requires='>=3.5'
)
