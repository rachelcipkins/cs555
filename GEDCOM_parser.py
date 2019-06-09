# Author: Adam Undus
# Description: GEDCOM file parser
# Date:  6/6/19

import sys
from beautifultable import BeautifulTable
import datetime

validLines = []


def parse(file):
    tags = {
        "INDI": {"indent": 0, "args": 1},
        "NAME": {"indent": 1, "args": 2},
        "SEX": {"indent": 1, "args": 1},
        "BIRT": {"indent": 1, "args": 0},
        "DEAT": {"indent": 1, "args": 0},
        "MARR": {"indent": 1, "args": 0},
        "FAMS": {"indent": 1, "args": 1},
        "FAMC": {"indent": 1, "args": 1},
        "FAM": {"indent": 0, "args": 1},
        "HUSB": {"indent": 1, "args": 1},
        "WIFE": {"indent": 1, "args": 1},
        "CHIL": {"indent": 1, "args": 1},
        "DIV": {"indent": 1, "args": 0},
        "DATE": {"indent": 2, "args": 3},
        "HEAD": {"indent": 0, "args": 0},
        "TRLR": {"indent": 0, "args": 0},
        "NOTE": {"indent": 0, "args": -1},
    }
    # individual template:
    # {
    #     'ID':args,
    #     'NAME' : '',
    #     'SEX':'',
    #     'BIRT':'',
    #     'DEAT':'',
    #     'FAMC':'',
    #     'FAMS':''
    # }
    # Family template:
    # {"ID": '', "MARR": "", "DIV": "", "HUSB": "", "WIFE": "", "CHIL": []}
    with open(file, "r") as inputFile:
        for line in inputFile.readlines():
            if line == "":
                continue
            # print('--> ' + line.strip())
            arr = line.strip().split(" ")
            level = int(arr[0])
            tag = arr[1].upper()
            args = arr[2:]
            valid = "Y"
            if len(arr) > 2:
                if arr[1] == "INDI" or arr[1] == "FAM":
                    valid = "N"
                    println(level, tag, valid, args)
                    continue
                if arr[2] == "INDI" or arr[2] == "FAM":
                    tag = arr[2]
                    args = [arr[1]]
            try:
                expectedIndent = tags[tag]["indent"]
                expectedNumArgs = tags[tag]["args"]
            except:
                valid = "N"
                # println(level, tag, valid, args)
                continue
            if tag == "NOTE" and level == 0:
                # println(level, tag, valid, args)
                continue
            if expectedIndent == level and expectedNumArgs == len(args):
                # println(level, tag, valid, args)
                validLines.append({"level": level, "tag": tag, "args": args})
                continue
            else:
                valid = "N"
                # println(level, tag, valid, args)
                continue


def getFamInfo():
    currentFam = None
    currentIndi = None
    individuals = []
    families = []
    for lineNum in range(len(validLines)):
        tag = validLines[lineNum]["tag"]
        level = validLines[lineNum]["level"]
        args = validLines[lineNum]["args"]
        # new individual, all tags below are associated w individuals
        if tag == "DATE":
            continue
        if tag == "INDI":
            currentIndi = args
            individuals.append(
                {
                    "ID": args,
                    "NAME": "",
                    "SEX": "",
                    "BIRT": "",
                    "DEAT": "",
                    "FAMC": "",
                    "FAMS": "",
                }
            )
            continue
        if tag in ["NAME", "SEX", "FAMS", "FAMC"]:
            next(item for item in individuals if item["ID"] == currentIndi)[tag] = args
            continue
        if tag in ["BIRT", "DEAT"]:
            date = " ".join(validLines[lineNum + 1]["args"])
            next(item for item in individuals if item["ID"] == currentIndi)[
                tag
            ] = datetime.datetime.strptime(date, "%d %b %Y")
            continue
        # New family, tags below are associated w families
        if tag == "FAM":
            currentFam = args
            families.append(
                {"ID": args, "MARR": "", "DIV": "", "HUSB": "", "WIFE": "", "CHIL": []}
            )
            continue
        if tag == "MARR" or tag == "DIV":
            date = " ".join(validLines[lineNum + 1]["args"])
            next(item for item in families if item["ID"] == currentFam)[
                tag
            ] = datetime.datetime.strptime(date, "%d %b %Y")
            continue
        if tag == "HUSB" or tag == "WIFE":
            next(item for item in families if item["ID"] == currentFam)[tag] = args
        if tag == "CHIL":
            next(item for item in families if item["ID"] == currentFam)[tag].append(
                args
            )
    printInfo(individuals, families)


def printInfo(individuals, families):
    individuals = sorted(individuals, key=lambda i: i["ID"])
    families = sorted(families, key=lambda i: i["ID"])
    # Individuals
    table1 = BeautifulTable()
    table1.column_headers = [
        "ID",
        "Name",
        "Gender",
        "Birthday",
        "Age",
        "Alive",
        "Death",
        "Child",
        "Spouse",
    ]
    for indi in individuals:
        today = datetime.date.today()
        born = indi["BIRT"]
        age = (
            today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        )
        alive = False
        if indi["DEAT"] == "":
            alive = True
        else:
            age = (
                indi["DEAT"].year
                - born.year
                - ((indi["DEAT"].month, indi["DEAT"].day) < (born.month, born.day))
            )
            indi["DEAT"] = indi["DEAT"].strftime("%Y-%m-%d")
        table1.append_row(
            [
                " ".join(indi["ID"]),
                " ".join(indi["NAME"]),
                " ".join(indi["SEX"]),
                indi["BIRT"].strftime("%Y-%m-%d"),
                age,
                alive,
                indi["DEAT"],
                " ".join(indi["FAMC"]),
                " ".join(indi["FAMS"]),
            ]
        )
    # families
    table2 = BeautifulTable()
    table2.column_headers = [
        "ID",
        "Married",
        "Divorced",
        "Husband ID",
        "Husband Name",
        "Wife ID",
        "Wife Name",
        "Children",
    ]

    for fam in families:
        if fam["DIV"] == "":
            fam["DIV"] = "N/A"
        else:
            fam["DIV"] = fam["DIV"].strftime("%Y-%m-%d")
        try:
            husband = next(item for item in individuals if item["ID"] == fam["HUSB"])[
                "NAME"
            ]
        except:
            husband = ""
        try:
            wife = next(item for item in individuals if item["ID"] == fam["WIFE"])[
                "NAME"
            ]
        except:
            wife = ""
        table2.append_row(
            [
                " ".join(fam["ID"]),
                fam["MARR"].strftime("%Y-%m-%d"),
                fam["DIV"],
                " ".join(fam["HUSB"]),
                " ".join(husband),
                " ".join(fam["WIFE"]),
                " ".join(wife),
                fam["CHIL"],
            ]
        )
    print("Individuals")
    print(table1)
    print("\nFamilies")
    print(table2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: GEDCOM_parser_info.py <file>")
        exit(1)
    else:
        file = sys.argv[1]
    parse(file)
    getFamInfo()

