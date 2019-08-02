# Author: Adam Undus
# Description: GEDCOM file parser
# Date:  6/6/19

import sys
from prettytable import PrettyTable
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
            except KeyError as ke:
                valid = "N"
                # println(level, tag, valid, args)
                continue
            if tag == "NOTE" and level == 0:
                # println(level, tag, valid, args)
                continue
            if expectedIndent == level and expectedNumArgs == len(args):
                validLines.append({"level": level, "tag": tag, "args": args})
            else:
                valid = "N"
    return validLines


def getFamInfo(validLines):
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
            families[currentFam][tag].append(args[0])
    return individuals, families


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
                    "Error: US16: Last name of {} does not match family last name of {}".format(
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
                "Error: US06: {} died on {}, so he cannot be divorced on {}".format(
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
                "Error: US06: {} died on {}, so he cannot be divorced on {}".format(
                    wife,
                    individuals[wife]["DEAT"].strftime("%Y-%m-%d"),
                    families[fam]["DIV"].strftime("%Y-%m-%d"),
                )
            )
    return True


def checkGenderForSpouses(individuals, families):
    for fam in families:
        wife = " ".join(families[fam]["WIFE"])
        husband = " ".join(families[fam]["HUSB"])
        if individuals[wife]["SEX"] == ["F"] and individuals[husband]["SEX"] == ["M"]:
            continue
        if individuals[wife]["SEX"] == ["M"]:
            print("Error: US21: in family {}: Sex of wife cannot be male".format(fam))
        if individuals[husband]["SEX"] == ["F"]:
            print(
                "Error: US21: in family {}: Sex of husband cannot be female".format(fam)
            )
    return True


def uniqueDOBandName(individuals):
    allUnique = True
    unique = set()
    for indi in individuals:
        nameDOB = " ".join(individuals[indi]["NAME"]) + individuals[indi]["BIRT"].strftime("%Y-%m-%d")
        if nameDOB in unique:
            allUnique = False
            print("Error: US23: Individual {} does not have a unique DOB and Name".format(indi))
        else:
            unique.add(nameDOB)
    return allUnique

def listLivingSingleAndMarried(individuals):
    livingSingle = []
    livingMarried = []
    for indi in individuals:
        if individuals[indi]["DEAT"] == "" and individuals[indi]["FAMS"] == "":
            livingSingle.append(indi)
        if individuals[indi]["DEAT"] == "" and individuals[indi]["FAMS"] != "":
            livingMarried.append(indi)
    print("US30: All Living Married: " + str(livingMarried))
    print("US31: All Living Single: " + str(livingSingle))
    return livingMarried, livingSingle


def checkDates(individuals, families):
    today = datetime.datetime.now()
    for fam in families:
        if families[fam]["MARR"] > today:
            print("Error: US01: Marriage date cannot come after today's date")
        if families[fam]["DIV"] == "":
            continue
        else:
            if families[fam]["DIV"] > today:
                print("Error: US01: Divorce date cannot come after today's date")
    for indi in individuals:
        if individuals[indi]["BIRT"] > today:
            print("Error: US01: Birth date cannot come after today's date")
        if individuals[indi]["DEAT"] == "":
            continue
        else:
            if individuals[indi]["DEAT"] > today:
                print("Error: US01: Death date cannot come after today's date")
    return True


def lessThan150YearsOld(individuals):
    for indi in individuals:
        today = datetime.date.today()
        born = individuals[indi]["BIRT"]
        death = individuals[indi]["DEAT"]
        if death == "":
            age = (
                (today.year)
                - born.year
                - ((today.month, today.day) < (born.month, born.day))
            )

            if age > 150:
                print("Error: US07: {} is older than 150 years old.".format(indi))
        else:
            age = (
                (death.year)
                - born.year
                - ((death.month, death.day) < (born.month, born.day))
            )
            if age > 150:
                print("Error: US07: {} is older than 150 years old.".format(indi))
    return True


def checkBirthBeforeMarriageOfParents(individuals, families):
    for fam in families:
        wife = " ".join(families[fam]["WIFE"])
        husband = " ".join(families[fam]["HUSB"])
        if families[fam]["CHIL"] != []:
            children = families[fam]["CHIL"]
        else:
            continue
        for child in children:
            if individuals[child]["BIRT"] < families[fam]["MARR"]:
                print(
                    "Error: US08: {} and {} married on {}, so {} cannot be born on {}".format(
                        husband,
                        wife,
                        families[fam]["MARR"].strftime("%Y-%m-%d"),
                        child,
                        individuals[child]["BIRT"].strftime("%Y-%m-%d"),
                    )
                )
            if families[fam]["DIV"] != "" and individuals[child]["BIRT"] > families[
                fam
            ]["DIV"] + datetime.timedelta(6 * 365 / 12):
                print(
                    "Error: US08: {} and {} divorced on {}, so {} cannot be born on {}".format(
                        husband,
                        wife,
                        families[fam]["DIV"].strftime("%Y-%m-%d"),
                        child,
                        individuals[child]["BIRT"].strftime("%Y-%m-%d"),
                    )
                )
    return True


def notMarriedToChildren(families):
    for fam in families:
        wife = " ".join(families[fam]["WIFE"])
        husband = " ".join(families[fam]["HUSB"])
        if families[fam]["CHIL"] == []:
            continue
        else:
            children = families[fam]["CHIL"]
        for child in children:
            if child == wife:
                print(
                    "Error: US17: Child {} is wife of father {}.".format(child, husband)
                )
            if child == husband:
                print(
                    "Error: US17: Child {} is husband of mother {}.".format(child, wife)
                )
    return True


def noSiblingMarriage(individuals, families):
    for fam in families:
        if families[fam]["CHIL"] == []:
            continue
        else:
            children = families[fam]["CHIL"]
            siblings = list(indiv for indiv in individuals if indiv in children)
            for sibling in siblings:
                for family in families:
                    wife = " ".join(families[family]["WIFE"])
                    husband = " ".join(families[family]["HUSB"])
                    if sibling == wife and husband in siblings:
                        print(
                            "Error: US18: Siblings {} and {} cannot be married.".format(
                                wife, husband
                            )
                        )
                    elif sibling == husband and wife in siblings:
                        print(
                            "Error: US18: Siblings {} and {} cannot be married.".format(
                                wife, husband
                            )
                        )
    return True

def deathBeforeBirth(individuals):
    for indi in individuals:
        if(individuals[indi]["DEAT"]==""):
            continue
        if(individuals[indi]["BIRT"]>individuals[indi]["DEAT"]):
            print("Error: US03: Individual {} cannot have death date come before birth date".format(indi))
    return True

def fewerThanFifteen(families):
    for fam in families:
        if (len(families[fam]["CHIL"])>=15):
            print("Error: US15: Family {} cannot have 15 or more children.".format(fam))
    return True

def listDeceased(individuals):
    for indi in individuals:
        if(individuals[indi]["DEAT"] != ""):
            print("Deceased: ", indi)
    return True

def orderSiblingsByAge(families, individuals):
    for fam in families:
        ages = []
        if families[fam]["CHIL"] == []:
            continue
        else:
            children = families[fam]["CHIL"]
            for child in children:
                today = datetime.date.today()
                born = individuals[child]["BIRT"]
                death = individuals[child]["DEAT"]
                if death == "":
                    age = (
                        (today.year)
                        - born.year
                        - ((today.month, today.day) < (born.month, born.day))
                    )
                else:
                    age = (
                        (death.year)
                        - born.year
                        - ((death.month, death.day) < (born.month, born.day))
                    )
                ages.append((child, age))
        sorted(ages, key = lambda x: x[1], reverse = True)
        print("Siblings of fam {} ordered by age:".format(fam))
        for age in ages:
            print(age[0])
    return True

def listUpcomingBday(individuals):
    upcoming = []
    today = datetime.datetime.today()
    for indi in individuals:
        if(today.month == 12 and individuals[indi]["BIRT"].month == 1):
            next_bday = individuals[indi]["BIRT"].replace(year = today.year+1)
        else:
            next_bday = individuals[indi]["BIRT"].replace(year = today.year)
        delta = next_bday - today
        if(delta.days < 30 and delta.days >= 0):
            upcoming.append(indi)
    print("Individuals with upcoming birthdays: " + str(upcoming))
    return True


def listUpcomingAniv(families):
    upcoming = []
    today = datetime.datetime.today()
    for fam in families:
        if(families[fam]["MARR"] == ''):
            continue
        if(today.month == 12 and families[fam]["MARR"].month == 1):
            next_aniv = families[fam]["MARR"].replace(year = today.year+1)
        else:
            next_aniv = families[fam]["MARR"].replace(year = today.year)
        delta = next_aniv - today
        if(delta.days < 30 and delta.days >= 0):
            upcoming.append(fam)
    print("Families with upcoming Anniversaries: " + str(upcoming))
    return True

def checkMultipleBirths(individuals, families):
    for fam in families:
        count = 0
        bdays = []
        for child in families[fam]["CHIL"]:
            if individuals[child]["BIRT"].strftime("%Y-%m-%d") in bdays:
                count += 1
            else:
                bdays.append(individuals[child]["BIRT"].strftime("%Y-%m-%d"))
        if count >= 5:
            print("Error: US14: Family {} has more than 5 childrem born on same day".format(fam))
    return True

def checkMarriageAfterBirth(individuals, families):
    for fam in families:
        wife="".join(families[fam]["WIFE"])
        husband="".join(families[fam]["HUSB"])
        marrDate=families[fam]["MARR"]
        if(individuals[wife]["BIRT"]>marrDate):
            print("Error: US02: Individual {} is married before birth".format(wife))
        if(individuals[husband]["BIRT"]>marrDate):
            print("Error: US02: Individual {} is married before birth".format(husband))
    return True

def recentDeaths(individuals):
    recent=[]
    for indi in individuals:
        if individuals[indi]["DEAT"]=="":
            continue;
        today = datetime.date.today()
        thirtyDaysAgo=today-datetime.timedelta(days=30)
        if(individuals[indi]["DEAT"].date()<=today and individuals[indi]["DEAT"].date()>=thirtyDaysAgo):
            recent.append(indi)
    print("Individuals that have died recently: "+str(recent))
    return True;

def checkBirthBeforeDeathofParents(individuals, families):
    for fam in families:
        wife = " ".join(families[fam]["WIFE"])
        husband = " ".join(families[fam]["HUSB"])
        if families[fam]["CHIL"] != []:
            children = families[fam]["CHIL"]
        else:
            continue
        for child in children:
            if individuals[wife]["DEAT"] != "":
                if individuals[child]["BIRT"] > individuals[wife]["DEAT"]:
                    print(
                    "Error: US09: {} died on {}, so {} cannot be born on {}".format(
                        wife,
                        individuals[wife]["DEAT"],
                        child,
                        individuals[child]["BIRT"].strftime("%Y-%m-%d"),
                    )
                )
            if individuals[husband]["DEAT"] != "":
                if individuals[child]["BIRT"] > individuals[husband]["DEAT"] + datetime.timedelta(6 * 365 / 12):
                    print(
                    "Error: US09: {} died on {}, so {} cannot be born on {}".format(
                        husband,
                        individuals[husband]["DEAT"],
                        child,
                        individuals[child]["BIRT"].strftime("%Y-%m-%d"),
                    )
                )         
    return True

def listRecentBirths(individuals):
    recent=[]
    for indi in individuals:
        today = datetime.date.today()
        thirtyDaysAgo = today - datetime.timedelta(days=30)
        if individuals[indi]["BIRT"].date() >= thirtyDaysAgo:
            recent.append(indi)
    print("Individuals that have died recently: "+str(recent))
    return True

def validation(individuals, families):
    checkDates(individuals, families)
    checkGenderForSpouses(individuals, families)
    checkDivorceBeforeDeath(individuals, families)
    checkMaleLastNames(individuals)
    lessThan150YearsOld(individuals)
    checkBirthBeforeMarriageOfParents(individuals, families)
    notMarriedToChildren(families)
    noSiblingMarriage(individuals, families)
    listLivingSingleAndMarried(individuals)
    uniqueDOBandName(individuals)
    deathBeforeBirth(individuals)
    fewerThanFifteen(families)
    listDeceased(individuals)
    orderSiblingsByAge(families, individuals)
    listUpcomingBday(individuals)
    listUpcomingAniv(families)
    recentDeaths(individuals)
    checkMultipleBirths(individuals,families)
    checkMarriageAfterBirth(individuals, families)
    checkBirthBeforeDeathofParents(individuals, families)


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
    individuals, families = getFamInfo(validLines)
    validation(individuals, families)
    printInfo(individuals, families)

