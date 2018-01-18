#!/usr/bin/env python3

"""
To convert the entire history of a git branch, invoke as follows::

    git reset --hard HEAD
    git clean -fxd
    git filter-branch --tree-filter "/path/to/convert_repo.py" HEAD
"""

import os
import subprocess
from subprocess import DEVNULL


def convert_notebook(path):
    cwd = os.path.abspath(os.getcwd())
    try:
        os.chdir(os.path.dirname(path))
        subprocess.check_call(
            'jupyter nbconvert --to vc "{}"'.format(
                os.path.basename(path)),
            shell=True, stdout=DEVNULL)
    finally:
        os.chdir(cwd)


def convert_tree(input_dir):
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            basename, ext = os.path.splitext(filename)
            path = os.path.join(root, filename)
            if ext == '.ipynb':
                convert_notebook(path)
                os.remove(path)


if __name__ == '__main__':
    # TODO: Proper argument parsing
    convert_tree('.')
