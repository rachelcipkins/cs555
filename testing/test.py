import unittest
from GEDCOM_parser import checkBirthBeforeMarriageOfParents, lessThan150YearsOld

path = os.path.dirname(__file__)
testFile = os.path.relpath("..\\testGEDCOM.ged", path)

class US07Tests(unittest.TestCase):

class US08Tests(unittest.TestCase):
    def testBirthBeforeMarriage(self):
        individuals, families = GEDCOMParser(testFile)
        self.assertTrue(birth_before_marriage(individuals, families))


if __name__ == "__main__":
    unittest.main() # run all tests