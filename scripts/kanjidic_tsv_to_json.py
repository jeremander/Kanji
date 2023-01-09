#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime
import json
from math import inf
import sys

# # reference numbering systems to include
# DIC_REFS = ['sh_kk']
GROUPS = {
    'Kanji' : {
        'info' : {
            'kanji' : 'Kanji'
        },
        'extra' : {
            'jlpt' : 'JLPT',
            'grade' : 'Grade',
            'freq' : 'Rank',
            'ref_sh_kk' : 'SH KK #',
            'strokes' : 'Strokes'
        }
    },
    'On Reading' : {
        'info' : {
            "on'yomi" : 'On'
        }
    },
    'Kun Reading' : {
        'info' : {
            "kun'yomi" : 'Kun'
        }
    },
    'Meanings' : {
        'info' : {
            'meanings' : 'Meanings'
        }
    }
}

MODES = {
    'Kanji' : {
        'front' : ['Kanji'],
        'back' : ['On Reading', 'Kun Reading', 'Meanings']
    },
    'On Reading' : {
        'front' : ['On Reading'],
        'back' : ['Kanji', 'On Reading', 'Kun Reading', 'Meanings']
    },
    'Kun Reading' : {
        'front' : ['Kun Reading'],
        'back' : ['Kanji', 'On Reading', 'Kun Reading', 'Meanings']
    },
    'Meanings' : {
        'front' : ['Meanings'],
        'back' : ['Kanji', 'On Reading', 'Kun Reading']
    }
}

FILTERS = {
    'JLPT' : {
        'field' : 'jlpt',
        'values' : [4, 3, 2, 1, None]
    }
}

ALL_COLUMNS = {
    'kanji' : str,
    'strokes' : int,
    'grade' : int,
    'jlpt' : int,
    'freq' : int,
    'ref_sh_kk' : int,
    "on'yomi" : str,
    "kun'yomi" : str,
    'meanings' : str
}


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Convert kanjidic TSV into a JSON file')
    parser.add_argument('kanjidic', help = 'kanjidic TSV file')
    args = parser.parse_args()

    print(f'Reading {args.kanjidic}', file = sys.stderr)
    entries = []

    with open(args.kanjidic) as f:
        reader = csv.reader(f, delimiter = '\t')
        cols = next(reader)
        for row in reader:
            row_dict = dict(zip(cols, row, strict = True))
            entry = {}
            for (col, tp) in ALL_COLUMNS.items():
                val = row_dict[col]
                if (tp is int):
                    val = int(val) if val else None
                entry[col] = val
            entries.append(entry)

    def get_key(entry):
        jlpt = entry['jlpt'] or 0
        grade = entry['grade'] or inf
        ref_sh_kk = entry['ref_sh_kk'] or inf
        return (-jlpt, grade, ref_sh_kk)

    entries.sort(key = get_key)

    d = {
        'source' : {
            'url' : 'http://www.edrdg.org/wiki/index.php/KANJIDIC_Project',
            'time' : datetime.now().isoformat(),
        },
        'groups' : GROUPS,
        'modes' : MODES,
        'filters' : FILTERS,
        'entries' : entries
    }

    print(json.dumps(d, ensure_ascii = False, indent = 1))
