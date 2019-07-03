import unittest
import os
from GEDCOM_parser import (
    checkBirthBeforeMarriageOfParents,
    lessThan150YearsOld,
    parse,
    getFamInfo,
    checkMaleLastNames,
    checkDivorceBeforeDeath,
    noSiblingMarriage,
    notMarriedToChildren
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

class US17Tests(unittest.TestCase):
    def testNoMarriageToChildren(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(notMarriedToChildren(families))

class US18Tests(unittest.TestCase):
    def testNoSiblingMarriage(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(noSiblingMarriage(individuals, families))


if __name__ == "__main__":
    unittest.main()  # run all tests

