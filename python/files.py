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
import sys
from os import walk
from os.path import join
from re import compile, match, search 
from timeit import default_timer as time

def get_filepaths(directory):
    file_paths = []

    for root, directories, files in walk(directory):
        for filename in files:
            filepath = join(root, filename)
            file_paths.append(filepath)

    return file_paths

def grep_clean(file_list):
    expected = []
    pat = compile('".*\s(.*)"')
    
    for file in installers:
         for line in open(file, 'r'):
             if search(pattern, line):
                 m = search(pat, line)
                 expected.append(m.group(1))

    return expected

root_path = str(sys.argv[1])
pattern = str(sys.argv[2])

stime = time()
full_file_paths = get_filepaths(root_path)

installers = []
objects = []

instFile = compile(".*install.*\.sh$")
junkFile = compile("^\.*svn")

for f in full_file_paths:
    if match(instFile, f):
        installers.append(f)
    elif match(junkFile, f.split(root_path,1).pop()):
      """Nothing""" 
    else:
        objects.append(f.split(root_path,1).pop())

expected = grep_clean(installers)

difference = (set(objects) - set(expected))
etime = time() - stime

print "=== RUN   Extra Files"
if len(difference) > 0:
    print "--- FAIL: Extra Files ("+str(round(etime,2))+" seconds):The following files are in the tag, not in an installer"
    for t in sorted(difference):
       print '\t' + t
    print "FAIL"
    print "exit status 1"
    print "FAIL\tExtra Files\t"+str(round(etime,3))+"s"
else:
    print "--- PASS: Extra Files ("+str(round(etime,2))+" seconds)"
    print "PASS"
    print "ok\tExtra Files\t"+str(round(etime,3))+"s"

"""
print "Number of objects: " + str(len(objects))
print "Number of installers: " + str(len(installers))
print "Number of expected: " + str(len(expected))
print "Number of difference: " + str(len(difference))
"""
