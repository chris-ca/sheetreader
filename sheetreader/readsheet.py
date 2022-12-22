#!/usr/bin/env python3
#####################################################################################################################
# Script Name     : .py
# Description     :
#
#
#
# Requires        :
# Arguments       :
# Run Information : This script is run manually|via crontab.
# Author          : Chris, 2020
# Output          :
#####################################################################################################################
# define the scope

from Sheet import *
import config


# root = '/home/cw/Sync/z4ty4-ikud8'
#
# i = 0
# for f in walk_diary_filesystem(root):
#     i+=1
#     print(f.isodate())
# print(f"{i} matching files found")

logbook = Logbook(**config.logbook)

for i, e in enumerate(logbook.entries):
    print(i, MarkdownDecorator(e))
