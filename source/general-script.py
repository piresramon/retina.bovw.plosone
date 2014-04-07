#!/bin/sh
import os

os.system("python low_level_script.py > stats_low_level.txt")
os.system("python create_codebooks.py > stats_codebooks.txt")
os.system("python mid_level_script.py > stats_mid_level.txt")
