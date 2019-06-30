import unittest
import os
from GEDCOM_parser import (
    checkBirthBeforeMarriageOfParents,
    lessThan150YearsOld,
    parse,
    getFamInfo,
    checkMaleLastNames,
    checkDivorceBeforeDeath,
    checkGenderForSpouses,
    checkDates
)

path = os.path.dirname(__file__)
testFile = os.path.relpath("testGEDCOM.ged", path)


class US07Tests(unittest.TestCase):
    def testLessThan150YearsOld(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(lessThan150YearsOld(individuals))


class US08Tests(unittest.TestCase):
    def testBirthBeforeMarriage(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(checkBirthBeforeMarriageOfParents(individuals, families))


class US16Tests(unittest.TestCase):
    def testMaleLastName(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(checkMaleLastNames(individuals) == {"F23": "Smith"})


class US06Tests(unittest.TestCase):
    def testDivorceBeforeDeath(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(checkDivorceBeforeDeath(individuals, families))

class US01Tests(unittest.TestCase):
    def testCheckDates(self):
        valid=parse(testFile)
        individuals,families=getFamInfo(valid)
        self.assertTrue(checkDates(individuals,families))

class US21Tests(unittest.TestCase):
    def testCheckGenderForSpouses(self):
        valid=parse(testFile)
        individuals,families=getFamInfo(valid)
        self.assertTrue(checkGenderForSpouses(individuals,families))


if __name__ == "__main__":
    unittest.main()  # run all tests

