# Author: Adam Undus
# Description: GEDCOM file parser
# Date:  5/28/19

import sys


def parse(file):
    tags = {
        'INDI': {
            'indent': 0,
            'args': 1
        },
        'NAME': {
            'indent': 1,
            'args': 2
        },
        'SEX': {
            'indent': 1,
            'args': 1
        },
        'BIRT': {
            'indent': 1,
            'args': 0
        },
        'DEAT': {
            'indent': 1,
            'args': 0
        },
        'MARR': {
            'indent': 1,
            'args': 0
        },
        'FAMS': {
            'indent': 1,
            'args': 1
        },
        'FAMC': {
            'indent': 1,
            'args': 1
        },
        'FAM': {
            'indent': 0,
            'args': 1
        },
        'HUSB': {
            'indent': 1,
            'args': 1
        },
        'WIFE': {
            'indent': 1,
            'args': 1
        },
        'CHIL': {
            'indent': 1,
            'args': 1
        },
        'DIV': {
            'indent': 1,
            'args': 0
        },
        'DATE': {
            'indent': 2,
            'args': 3
        },
        'HEAD': {
            'indent': 0,
            'args': 0
        },
        'TRLR': {
            'indent': 0,
            'args': 0
        },
        'NOTE': {
            'indent': 0,
            'args': -1
        }
    }
    with open(file, 'r') as inputFile:
        for line in inputFile.readlines():
            if line == '': break
            print('--> ' + line.strip())
            arr = line.strip().split(' ')
            level = int(arr[0])
            tag = arr[1].upper()
            args = arr[2:]
            valid = 'Y'
            if len(arr) > 2:
                if arr[1] == 'INDI' or arr[1] == 'FAM':
                    valid = 'N'
                    println(level, tag, valid, args)
                    continue
                if arr[2] == 'INDI' or arr[2] == 'FAM':
                    tag = arr[2]
                    args = [arr[1]]
            try:
                expectedIndent = tags[tag]['indent']
                expectedNumArgs = tags[tag]['args']
            except:
                valid = 'N'
                println(level, tag, valid, args)
                continue
            if tag == 'NOTE' and level == 0:
                println(level, tag, valid, args)
                continue
            if expectedIndent == level and expectedNumArgs == len(args):
                println(level, tag, valid, args)
                continue
            else:
                valid = 'N'
                println(level, tag, valid, args)
                continue


def println(level, tag, valid, args):
    print('<-- ' + str(level) + '|' + tag + '|' + valid + '|' + ' '.join(args))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: GEDCOM_parser.py <file>')
        exit(1)
    else:
        file = sys.argv[1]
    parse(file)
