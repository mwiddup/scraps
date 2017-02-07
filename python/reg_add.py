#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 vagrant <vagrant@vagrant-ubuntu-trusty-64>
#
# Distributed under terms of the MIT license.

"""
Goes through a file and matches the regex_match pattern
replaces with whatever, in this case it is adding one to a known
number to increment all patterns. Each time you run it it will continue
to add one.
Usage:
    ./reg_add.py test.txt "(ssk.STRING_)(\d+)"
"""

import sys
import fileinput
from re import compile, match, search

pattern = str(sys.argv[2])
input_file = str(sys.argv[1])

regex_match = compile(pattern)

for line in fileinput.input(input_file, inplace=True):
    m = search(regex_match, line)
    if m:
        replace=int(m.group(2)) + 1 
        line = line.replace(m.group(0), m.group(1)+str(replace))
    print(line, end="")

