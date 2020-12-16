import os
import unittest
from datetime import datetime

from server.database import BreakagesDatabase


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.db = BreakagesDatabase("test_database.sqlite")

    def tearDown(self):
        os.remove("test_database.sqlite")

    @staticmethod
    def clear_breakages_from_id(breakages_list):
        return [breakage[1:] for breakage in breakages_list]

    def test_single_adding(self):
        place, time, description = "At station", datetime.now().timestamp(), "This is test breakage"
        self.db.add_new_breakage(place, time, description)
        self.assertIn((place, time, description),
                      DatabaseTest.clear_breakages_from_id(self.db.get_free_breakages()))

    def test_multiple_adding(self):
        breakages = [("At station", datetime.now().timestamp(), "This is test breakage"),
                     ("At the mall", datetime(1984, 7, 13, 16, 10).timestamp(), "Strange thing happened")]
        for breakage in breakages:
            self.db.add_new_breakage(*breakage)
        breakages_in_db = DatabaseTest.clear_breakages_from_id(self.db.get_free_breakages())
        self.assertEqual(len(breakages_in_db), 2, "Wrong number of breakages in database")
        for breakage in breakages:
            self.assertIn(breakage, breakages_in_db, "Added breakages not in database")

    def test_breakage_pipeline(self):
        engineer = 1
        self.assertEqual(len(self.db.get_free_breakages()), 0)
        place, time, description = "At station", datetime.now().timestamp(), "This is test breakage"
        self.db.add_new_breakage(place, time, description)
        self.assertEqual(len(self.db.get_free_breakages()), 1)
        self.assertIn((place, time, description),
                      DatabaseTest.clear_breakages_from_id(self.db.get_free_breakages()))
        breakage_id = [id_ for id_, p, t, d in self.db.get_free_breakages()
                       if p == place and t == time and d == description][0]
        self.assertTrue(self.db.take_breakage(breakage_id, engineer))
        self.assertFalse(self.db.take_breakage(breakage_id, engineer + 1))
        self.assertIn((place, time, description),
                      DatabaseTest.clear_breakages_from_id(self.db.get_engineer_breakages(engineer)))
        self.assertNotIn((place, time, description),
                         DatabaseTest.clear_breakages_from_id(self.db.get_engineer_breakages(engineer + 1)))
        self.assertNotIn((place, time, description),
                         DatabaseTest.clear_breakages_from_id(self.db.get_free_breakages()))
        self.db.report_breakage_fixed(breakage_id)
        self.assertNotIn((place, time, description),
                         DatabaseTest.clear_breakages_from_id(self.db.get_engineer_breakages(engineer)))


if __name__ == '__main__':
    unittest.main()
