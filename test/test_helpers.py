#!/usr/bin/env python

from source import helpers
import os
import unittest
# python -m unittest -v


class TestHelpers(unittest.TestCase):

    def test_check_sections_default(self):
        config_sections = ['arch', 'home', 'shared']
        argument_sections = []
        expected_yes = ['arch', 'home', 'shared']
        expected_no = []
        [yes, no] = helpers.check_sections(config_sections, argument_sections)
        self.assertEqual(yes, expected_yes)
        self.assertEqual(no, expected_no)

    def test_check_sections_args(self):
        config_sections = ['arch', 'shared']
        argument_sections = ['arch', 'home', 'other']
        expected_yes = ['arch']
        expected_no = ['home', 'other']
        [yes, no] = helpers.check_sections(config_sections, argument_sections)
        self.assertEqual(yes, expected_yes)
        self.assertEqual(no, expected_no)


if __name__ == '__main__':
    unittest.main()
