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
    notMarriedToChildren,
    checkGenderForSpouses,
    checkDates,
    listLivingSingleAndMarried,
    uniqueDOBandName,
    deathBeforeBirth,
    fewerThanFifteen,
    listDeceased,
    orderSiblingsByAge,
    listUpcomingAniv,
    listUpcomingBday,
    checkMultipleBirths,
    checkMarriageAfterBirth,
    recentDeaths
)

path = os.path.dirname(__file__)
testFile = os.path.relpath("testGEDCOM.ged", path)


class US07Tests(unittest.TestCase):
    def testLessThan150YearsOld(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(lessThan150YearsOld(individuals))

class US38Tests(unittest.TestCase):
    def testUpcomingBday(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(listUpcomingBday(individuals))

class US14Tests(unittest.TestCase):
    def testMultBirths(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(checkMultipleBirths(individuals,families))


class US39Tests(unittest.TestCase):
    def testUpcomingAniv(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(listUpcomingAniv(families))

class US23Tests(unittest.TestCase):
    def testUniqueDOBandName(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(uniqueDOBandName(individuals))

class US30and31Tests(unittest.TestCase):
    def testListLivingMarriedandSignle(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        married, single = listLivingSingleAndMarried(individuals)
        self.assertTrue(married == ["I26"])
        self.assertTrue(single == ["I19", "I26"])


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


class US01Tests(unittest.TestCase):
    def testCheckDates(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(checkDates(individuals, families))


class US21Tests(unittest.TestCase):
    def testCheckGenderForSpouses(self):
        valid = parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(checkGenderForSpouses(individuals, families))

class US03Tests(unittest.TestCase):
    def testDeathBeforeBirth(self):
        valid=parse(testFile)
        individuals, families = getFamInfo(valid)
        self.assertTrue(deathBeforeBirth(individuals))

class US15Tests(unittest.TestCase):
    def testFewerThanFifteen(self):
        valid=parse(testFile)
        individuals, families=getFamInfo(valid)
        self.assertTrue(fewerThanFifteen(families))

class US28Tests(unittest.TestCase):
    def testOrderSiblingsByAge(self):
        valid=parse(testFile)
        individuals, families=getFamInfo(valid)
        self.assertTrue(orderSiblingsByAge(families, individuals))

class US29Tests(unittest.TestCase):
    def testListDeceased(self):
        valid=parse(testFile)
        individuals, families=getFamInfo(valid)
        self.assertTrue(listDeceased(individuals))

class US02Tests(unittest.TestCase):
    def testCheckMarriageAfterBirth(self):
        valid=parse(testFile)
        individuals, families=getFamInfo(valid)
        self.assertTrue(checkMarriageAfterBirth(individuals, families))

class US36Tests(unittest.TestCase):
    def testRecentDeaths(self):
        valid=parse(testFile)
        individuals, families=getFamInfo(valid)
        self.assertTrue(recentDeaths(individuals))


if __name__ == "__main__":
    unittest.main()  # run all tests

