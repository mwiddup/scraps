#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 vagrant <vagrant@vagrant-ubuntu-trusty-64>
#
# Distributed under terms of the MIT license.

"""
This will grab all files and dirs of a given root and store a list
It will then jump through the install*.sh files to grab cooresponding lists
and match. Anything inconsistant on the file path side (files exist that aren't
in the install*.sh files) are reported as an error
Output should conform to Junit standards; natively or by using go-junit-report
"""

from os import walk
from os.path import join

def get_filepaths(directory):
    file_paths = []

    for root, directories, files in walk(directory):
        for filename in files:
            filepath = join(root, filename)
            file_paths.append(filepath)

    return file_paths

full_file_paths = get_filepaths("/home/vagrant/repo/CR19321")

for f in full_file_paths:
   print f

