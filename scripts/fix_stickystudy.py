#!/usr/bin/env python3

import argparse

import ftfy


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Fix mojibake in CSV file exported from StickyStudy app')
    parser.add_argument('infile')
    args = parser.parse_args()

    with open(args.infile) as f:
        s = f.read()

    fixed = ftfy.fix_text(s)
    lines = fixed.splitlines()
    fixed = '\n'.join(lines[2:]) + '\n'

    header = "kanji\ton'yomi\tkun'yomi\tmeaning\tpractice_data"
    print(header)
    print(fixed)