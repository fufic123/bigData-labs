#!/usr/bin/env python

import sys

sys.stdin = open("smapout.txt","r")
sys.stdout = open("redout.txt","w")

current_diena = None
current_count = 0
diena = None

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    diena, count = line.split('\t', 1)

    # convert count (currently a string) to int
    try:
        count = int(count)
    except ValueError:
        # count was not a number, so silently
        # ignore/discard this line
        continue

    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_diena == diena:
        current_count += count
    else:
        if current_diena != None:
            # write result to STDOUT
            print ('%s\t%s' % (current_diena, current_count))
        current_count = count
        current_diena = diena

# do not forget to output the last word if needed!
if current_diena != None:
    print ('%s\t%s' % (current_diena, current_count))
