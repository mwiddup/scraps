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

"""
Grabs all files from all directories specified at the root location
No filtering at this stage, just a full list
"""
def get_filepaths(directory):
    file_paths = []

    for root, directories, files in walk(directory):
        for filename in files:
            filepath = join(root, filename)
            file_paths.append(filepath)

    return file_paths


"""
Returns a list of all patterns matched, cleaning them in the process by
pulling out just the file path to the object
"""
def grep_clean(file_list):
    expected = []
    pat = compile('".*\s(.*)"')
    
    for file in file_list:
         for line in open(file, 'r'):
             if search(pat, line):
                 m = search(pat, line)
                 expected.append(m.group(1))

    return expected

"""
This bit goes through those left over files and tries to identify the last
person to check them in to SVN via the SVN keyword for Author
Looks like we've got some almost identical code going on here
"""
def grep_auth(file_list):
    fileauth = []
    pat = compile('\$Author:\s+(.*)\s+\$')

    for file in file_list:
        isauth = False
        for line in open(root_path + file, 'r'):
            if search(pat, line) and not isauth:
                m = search(pat, line)
                author =  m.group(1)
                isauth = True

        if not isauth:
            author = "Author not found, fix SVN header"

        fileauth.append(file + '|' + author)

    return fileauth


"""
Returns a list of matched patterns alone, based on the previous list of
matched patterns. Second run through the installers looking for specific
file mentions. This should capture code listed in the installer that is not
using the DB2_Run command
"""
def grep_leftovers(file_list, missing_list):
    cleaned = []

    for thingy in missing_list:
        for file in file_list:
            for line in open(file, 'r'):
                if search(thingy, line):
                    cleaned.append(thingy)
                    break #one instance of a matched pattern(thingy) is enough

    return cleaned

"""
Grabs the input values
"""
root_path = str(sys.argv[1])
pattern = str(sys.argv[2])

stime = time()
full_file_paths = get_filepaths(root_path)

installers = []
objects = []

instFile = compile(".*install.*\.sh$")
junkFile = compile("^\.\w")

"""
Go through some of the gathered lists of files and filter out those that
are needed for further tests. Reject the others
"""
for f in full_file_paths:
    if match(instFile, f):
        installers.append(f)
    elif match(junkFile, f.split(root_path,1).pop()):
      """Nothing""" 
    else:
        objects.append(f.split(root_path,1).pop())

expected = grep_clean(installers)

"""
Compare two lists, the left overs are those that are missing from installers
The second list comparison runs over the remaining object through the files
to ensure their not used
"""
difference = (set(objects) - set(expected))
difference = (set(difference) - set(grep_leftovers(installers, difference)))
difference = grep_auth(difference)
etime = time() - stime


print "=== RUN   Extra Files"
if len(difference) > 0:
    print "--- FAIL: Extra Files ("+str(round(etime,2))+" seconds):The following files are in the tag, not in an installer"
    for t in sorted(difference):
        filemiss = t.split('|',1)[0]
        auth = t.split('|',1)[1]
        print '\t'+ '(' + auth + "): " +  filemiss  
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

