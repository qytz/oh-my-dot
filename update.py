#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

BASE_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

os.chdir(BASE_PATH)
os.system('git pull')
os.system('git submodule foreach --recursive git submodule update')
os.system('git submodule foreach --recursive git pull')
