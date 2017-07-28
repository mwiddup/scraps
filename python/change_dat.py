# Hopefully this will change_dat.

"""
This will work it's way through a root folder and attempt
to change a bunch of files based on their type and specific
regex matches
"""
import my_vars
from collections import namedtuple
from os import walk
from os.path import join
from re import compile, search, sub, MULTILINE, IGNORECASE

# defining a type/tuple. Figured it should go at the top
BoolNum = namedtuple('MatchRow', ['m', 'r'])

"""
Grabs all files from all directories specified at the root location
No filtering at this stage, just a full list
"""
def get_filtered_files(directory, file_type):
    file_paths = []
    pat_file = compile (file_type)

    for root, _, files in walk(directory):
        for filename in files:
            if search(pat_file, filename):
                filepath = join(root, filename)
                file_paths.append(filepath)

    return file_paths

"""
This lil' fella will find a pattern in a multi-line string and return
a tuple of False and line-number it was found
"""
def find_pattern(input_string, pattern_ignore):
    mytup = BoolNum(True, 0)
    if pattern_ignore: # Don't filter if the string is empty
        pat_ignore = compile(pattern_ignore)
        for num, line in enumerate(input_string.splitlines(), 1):
            if search(pat_ignore, line):
                mytup = BoolNum(False, num)
                break

    return mytup

"""
Replace all the matched patterns
Opens and closes/writes files
This is doing way too many things
"""
def replace_pattern(file_list, pattern_match, pattern_replace, pattern_ignore, comment):
    for f_obj in file_list:
        with open(f_obj, 'r+') as f:
            input_str = f.read()
            if find_pattern(input_str, pattern_ignore).m: #checks to see if we should ignore the file
                i, j=0, 0
                for p_m in pattern_match:
                    pat_match = compile(p_m, MULTILINE | IGNORECASE)
                    if search(pat_match, input_str):
                        #Only write the file if a replace will happen AND the specified pattern does no exist (skip pattern)
                        input_str = sub(pat_match, pattern_replace[i], input_str, MULTILINE | IGNORECASE)
                        j += 1 #counter of successful matches
#                         print ("Match on (" + str(i) + "): " + p_m)
#                     else:  #trouble shoot few matches
#                         print ("Failed on (" + str(i) + "): " + p_m)
                    i += 1
                if j == i:
                    input_str = add_comment(input_str, comment, f_obj)
                    if find_pattern(input_str, my_vars.grant_pat_ignore).m:
                        input_str = strip_grants(input_str)
                        input_str = add_comment(input_str, my_vars.comment_grant_strip_add, f_obj)
                        input_str = append_block_grants(input_str, my_vars.grant_block_proc, my_vars.grant_block_proc_pat)
                    else:
                        print ("Permissions already exist, nothing to strip!")
                    f.seek(0)
                    f.write(input_str)
                    f.truncate()
                    print("M R(" + str(i) + "): " + f_obj)
                elif j < i and j != 0:
                    print("Looks like not all patterns were matched, file ignored\n\t" + f_obj)
                else:
                    """Nothing"""
                    #print("No matches, file skipped\n\t" + f_obj)
            else:
                print("This file is ignored due to keyword filter ("+pattern_ignore+"):\n\t" + f_obj)
            f.close()

"""
Adds a comment to the file
"""

def add_comment(mlstr, args, filename):
    new_comment = ""
    for line in mlstr.splitlines():
        if search(pat1, line):
            nme, dat, rel, des = line.upper().find("NAME"), line.upper().find("DATE"), line.upper().find("RELEASE"), line.upper().find("DESCRIPTION")
            if nme == -1:
                nme = line.upper().find("AUTHOR")

            if rel == -1 and nme >=0 and dat >=1: #Sometimes there is no Release info
                new_comment = '{0:<{nmew}} {1:<{datw}} {3:}'.format(*args, nmew=dat-1, datw=des-dat-1)
            elif nme >=0 and dat >=1:
                new_comment = '{0:<{nmew}} {1:<{datw}} {2:<{relw}} {3:}'.format(*args, nmew=dat-1, datw=rel-dat-1, relw=des-rel-1)
            else:
                new_comment = ""

    if search(pat2, mlstr) and new_comment:
        mlstr = sub(pat2, new_comment + '\\n\\1' , mlstr, MULTILINE | IGNORECASE)
    else:
        print("No comment added: " + filename)

    return mlstr

"""Appends the desired block of code to the string
This particular one is for adding grants so it does some selective lookups
The block string is more or less an expected format which includes the substitution
keywords of #SCHEMA# and #OBJECT#"""
def append_block_grants(mlstr, block, patterns):
    if find_pattern(mlstr, my_vars.load_pat_ignore).m:
        pat_m1 = compile(patterns[0], MULTILINE | IGNORECASE)
        pat_m2 = compile(patterns[1])  #backup search, uses PRODCUEDRE name
        m1 = search(pat_m1, mlstr)
        m2 = search(pat_m2, mlstr)
        if m1:
            block = block.replace("#SCHEMA#", m1.group(2).upper())
            block = block.replace("#OBJECT#", m1.group(3).upper())
            mlstr = mlstr + '\n' + block
        elif m2:
            block = block.replace("#SCHEMA#", m2.group(2).upper())
            block = block.replace("#OBJECT#", m2.group(3).upper())
            mlstr = mlstr + '\n' + block
        else:
            print ("Didn't find a schema.procname")
    else:
        print("Keyword matched! Nothing doing: " + my_vars.load_pat_ignore)

    return mlstr

def strip_grants(mlstr):
    pat_strip = compile(my_vars.strip_grants, MULTILINE | IGNORECASE)
    replace = "" #Get out of here with your eye-holes
    mlstr = sub(pat_strip, replace, mlstr, MULTILINE | IGNORECASE)

    return mlstr


def remove_all_grants_from_all(file_list):
    for f_obj in file_list:
        with open(f_obj, 'r+') as f:
            input_str = f.read()
            if find_pattern(input_str, my_vars.grant_pat_ignore).m: #checks to see if we should ignore the file
                input_str = strip_grants(input_str)
                input_str = add_comment(input_str, my_vars.comment_grant_strip, f_obj)
                f.seek(0)
                f.write(input_str)
                f.truncate()
            else:
                print("This file is ignored due to keyword filter ("+my_vars.grant_pat_ignore+"):\n\t" + f_obj)
            f.close()

"""
Grabs the input values
"""

pat1 = compile(my_vars.grant_pat_head, IGNORECASE)
pat2 = compile(my_vars.grant_pat_tail, MULTILINE | IGNORECASE)

file_type = "^di.*ddl$"

full_filtered_files = get_filtered_files(my_vars.root_path, file_type)
replace_pattern(full_filtered_files,my_vars.load_pat_match,my_vars.load_pat_replace, my_vars.load_pat_ignore, my_vars.comment_load)

file_type = ".*(ddl|sql)$" #All object creation scripts!

full_filtered_files = get_filtered_files(my_vars.root_path, file_type)
remove_all_grants_from_all(full_filtered_files)

file_type = "^tb.*ddl$"

full_filtered_files = get_filtered_files(my_vars.root_path, file_type)
replace_pattern(full_filtered_files, my_vars.tb_pat_match, my_vars.tb_pat_replace, my_vars.grant_pat_ignore, my_vars.comment_grant_add)

print("\nDONE")
