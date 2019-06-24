# Author: Adam Undus
# Description: GEDCOM file parser
# Date:  6/6/19

import sys
from prettytable import PrettyTable
import datetime
from dateutil.relativedelta import *

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
            except KeyError as ke:
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
    individuals = {}
    families = {}
    for lineNum in range(len(validLines)):
        tag = validLines[lineNum]["tag"]
        level = validLines[lineNum]["level"]
        args = validLines[lineNum]["args"]
        # new individual, all tags below are associated w individuals
        if tag == "DATE":
            continue
        if tag == "INDI":
            args = "".join(args)
            currentIndi = args
            individuals[args] = {
                "NAME": "",
                "SEX": "",
                "BIRT": "",
                "DEAT": "",
                "FAMC": "",
                "FAMS": "",
            }
            continue
        if tag in ["NAME", "SEX", "FAMS", "FAMC"]:
            individuals[currentIndi][tag] = args
            continue
        if tag in ["BIRT", "DEAT"]:
            date = " ".join(validLines[lineNum + 1]["args"])
            individuals[currentIndi][tag] = datetime.datetime.strptime(date, "%d %b %Y")
            continue
        # New family, tags below are associated w families
        if tag == "FAM":
            args = "".join(args)
            currentFam = args
            families[args] = {"MARR": "", "DIV": "", "HUSB": "", "WIFE": "", "CHIL": []}
            continue
        if tag == "MARR" or tag == "DIV":
            date = " ".join(validLines[lineNum + 1]["args"])
            families[currentFam][tag] = datetime.datetime.strptime(date, "%d %b %Y")
            continue
        if tag == "HUSB" or tag == "WIFE":
            families[currentFam][tag] = args
        if tag == "CHIL":
            families[currentFam][tag].append(args)
    checkDates(individuals, families)
    checkGenderForSpouses(individuals, families)
    checkDivorceBeforeDeath(individuals, families)
    checkMaleLastNames(individuals)
    lessThan150YearsOld(individuals)
    checkBirthBeforeMarriageOfParents(individuals, families)
    printInfo(individuals, families)

def checkMaleLastNames(individuals):
    familyNames = {}
    for indi in individuals:
        if " ".join(individuals[indi]["SEX"]) == "F":
            continue
        lastName = individuals[indi]["NAME"][1][1:-1]
        if " ".join(individuals[indi]["FAMS"]) == "":
            family = " ".join(individuals[indi]["FAMC"])
        else:
            family = " ".join(individuals[indi]["FAMS"])
        try:
            if lastName == familyNames[family]:
                continue
            else:
                print(
                    "Error: Last name of {} does not match family last name of {}".format(
                        indi, family
                    )
                )
        except KeyError as ke:
            familyNames[family] = lastName
    return familyNames


def checkDivorceBeforeDeath(individuals, families):
    for fam in families:
        if families[fam]["DIV"] == "":
            continue
        wife = " ".join(families[fam]["WIFE"])
        husband = " ".join(families[fam]["HUSB"])
        if individuals[husband]["DEAT"] == "" and individuals[wife]["DEAT"] == "":
            continue
        if (
            individuals[husband]["DEAT"] != ""
            and individuals[husband]["DEAT"] < families[fam]["DIV"]
        ):
            print(
                "Error: {} died on {}, so he cannot be divorced on {}".format(
                    husband,
                    individuals[husband]["DEAT"].strftime("%Y-%m-%d"),
                    families[fam]["DIV"].strftime("%Y-%m-%d"),
                )
            )
        if (
            individuals[wife]["DEAT"] != ""
            and individuals[wife]["DEAT"] < families[fam]["DIV"]
        ):
            print(
                "Error: {} died on {}, so he cannot be divorced on {}".format(
                    wife,
                    individuals[wife]["DEAT"].strftime("%Y-%m-%d"),
                    families[fam]["DIV"].strftime("%Y-%m-%d"),
                )
            )
def checkGenderForSpouses(individuals,families):
    for fam in families:
        wife = " ".join(families[fam]["WIFE"])
        husband = " ".join(families[fam]["HUSB"])
        if (individuals[wife]["SEX"]==['F'] and individuals[husband]["SEX"]==['M']):
            continue
        if(individuals[wife]["SEX"]==['M']):
            print("Error in family {}: Sex of wife cannot be male".format(fam))
        if(individuals[husband]["SEX"]==['F']):
            print("Error in family {}: Sex of husband cannot be female".format(fam))

def checkDates(individuals,families):
    today=datetime.datetime.now()
    for fam in families:
        if(families[fam]["MARR"]>today):
            print("Error: Marriage date cannot come after today's date")
        if(families[fam]["DIV"]==""):
            continue
        else:
            if families[fam]["DIV"]>today:
                print("Error: Divorce date cannot come after today's date")
    for indi in individuals:
        if(individuals[indi]["BIRT"]>today):
            print("Error: Birth date cannot come after today's date")
        if(individuals[indi]["DEAT"]==""):
            continue
        else:
            if(individuals[indi]["DEAT"]>today):
                print("Error: Death date cannot come after today's date")

def lessThan150YearsOld(individuals):
    for indi in individuals:
        today = datetime.date.today()
        born = individuals[indi]["BIRT"]
        death = individuals[indi]["DEAT"]
        age = (
            (today.year + 100) - born.year - ((today.month, today.day) < (born.month, born.day))
        )
        if death == "" or age > 150:
            print(
                "Error: {} is older than 150 years old.".format(
                    indi
                )
            )
        else:
            age = (
            (death.year) - born.year - ((death.month, death.day) < (born.month, born.day))
            )
            if age > 150:
                print(
                    "Error: {} is older than 150 years old.".format(
                        indi
                    )
                )


def checkBirthBeforeMarriageOfParents(individuals, families):
    for fam in families:
        wife = " ".join(families[fam]["WIFE"])
        husband = " ".join(families[fam]["HUSB"])
        if families[fam]["CHIL"] != []:
            children = families[fam]["CHIL"]
        else:
            continue
        for child in children:
            if (individuals[child[0]]["BIRT"] < families[fam]["MARR"]):
                print(
                    "Error: {} and {} married on {}, so {} cannot be born on {}".format(
                        husband,
                        wife,
                        families[fam]["MARR"].strftime("%Y-%m-%d"),
                        child[0],
                        individuals[child[0]]["BIRT"].strftime("%Y-%m-%d"),
                    )
                )
            if (families[fam]["DIV"] != "" and individuals[child[0]]["BIRT"] > families[fam]["DIV"]+relativedelta(months=+9)):
                print(
                    "Error: {} and {} divorced on {}, so {} cannot be born on {}".format(
                        husband,
                        wife,
                        families[fam]["DIV"].strftime("%Y-%m-%d"),
                        child[0],
                        individuals[child[0]]["BIRT"].strftime("%Y-%m-%d"),
                    )
                )

def printInfo(individuals, families):
    # Individuals
    table1 = PrettyTable()
    table1.field_names = [
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
        born = individuals[indi]["BIRT"]
        age = (
            today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        )
        alive = False
        if individuals[indi]["DEAT"] == "":
            alive = True
        else:
            age = (
                individuals[indi]["DEAT"].year
                - born.year
                - (
                    (individuals[indi]["DEAT"].month, individuals[indi]["DEAT"].day)
                    < (born.month, born.day)
                )
            )
            individuals[indi]["DEAT"] = individuals[indi]["DEAT"].strftime("%Y-%m-%d")
        table1.add_row(
            [
                indi,
                " ".join(individuals[indi]["NAME"]),
                " ".join(individuals[indi]["SEX"]),
                individuals[indi]["BIRT"].strftime("%Y-%m-%d"),
                age,
                alive,
                individuals[indi]["DEAT"],
                " ".join(individuals[indi]["FAMC"]),
                " ".join(individuals[indi]["FAMS"]),
            ]
        )
    # families
    table2 = PrettyTable()
    table2.field_names = [
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
        if families[fam]["DIV"] == "":
            families[fam]["DIV"] = "N/A"
        else:
            families[fam]["DIV"] = families[fam]["DIV"].strftime("%Y-%m-%d")
        try:
            husband = individuals["".join(families[fam]["HUSB"])]["NAME"]
        except KeyError as ke:
            husband = "Husband not found."
        try:
            wife = individuals["".join(families[fam]["WIFE"])]["NAME"]
        except KeyError as ke:
            wife = "Wife not Found"
        table2.add_row(
            [
                fam,
                families[fam]["MARR"].strftime("%Y-%m-%d"),
                families[fam]["DIV"],
                " ".join(families[fam]["HUSB"]),
                " ".join(husband),
                " ".join(families[fam]["WIFE"]),
                " ".join(wife),
                families[fam]["CHIL"],
            ]
        )
    print("Individuals")
    print(table1)
    print("\nFamilies")
    print(table2)


if __name__ == "__main__":
    file = None
    if len(sys.argv) != 2:
        print("Usage: GEDCOM_parser_info.py <file>")
        exit(1)
    else:
        file = sys.argv[1]
    parse(file)
    getFamInfo()

