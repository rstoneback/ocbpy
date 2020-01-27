#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2019, AGB & GC
# Full license can be found in License.md
#-----------------------------------------------------------------------------
""" Tests the boundaries.files functions
"""
from __future__ import absolute_import, unicode_literals


import datetime as dt
import logging
import numpy as np
import os
from sys import version_info
import unittest

import ocbpy
from ocbpy.boundaries import files

class TestFilesMethods(unittest.TestCase):

    def setUp(self):
        """ Initialize the test class
        """
        self.out = None
        self.orig_file = ocbpy.__file__
        self.comp_dict = {'amp_north_radii.ocb':
                          {'instrument': 'amp', 'hemisphere': 1,
                           'stime': dt.datetime(2010, 1, 1, 0, 0),
                           'etime': dt.datetime(2017, 1, 1, 0, 0)},
                          'wic_north_circle.ocb':
                          {'instrument': 'wic', 'hemisphere': 1,
                           'stime': dt.datetime(2000, 5, 3, 0, 0),
                           'etime': dt.datetime(2002, 8, 22, 0, 0)},
                          'si12_north_circle.ocb':
                          {'instrument': 'si12', 'hemisphere': 1,
                           'stime': dt.datetime(2000, 5, 4, 0, 0),
                           'etime': dt.datetime(2002, 8, 23, 0, 0)},
                          'si13_north_circle.ocb':
                          {'instrument': 'si13', 'hemisphere': 1,
                           'stime': dt.datetime(2000, 5, 5, 0, 0),
                           'etime': dt.datetime(2002, 8, 23, 0, 0)},
                          'amp_south_radii.ocb':
                          {'instrument': 'amp', 'hemisphere': -1,
                           'stime': dt.datetime(2010, 1, 1, 0, 0),
                           'etime': dt.datetime(2017, 1, 1, 0, 0)}}
        self.short_to_long = {"amp": "ampere", "si12": "image", "si13": "image",
                              "wic": "image", "": "image",
                              "dmsp-ssj": "dmsp-ssj"}
        self.long_to_short = {"ampere": "amp", "image": "si13", "": "si13",
                              "dmsp-ssj": None}
        self.inst = {1: ['', 'si13', 'si12', 'wic', 'amp', 'image', 'ampere',
                         'dmsp-ssj'],
                     -1: ['', 'amp', 'ampere', 'dmsp-ssj']}
        self.hemi = 1

        # Remove in 2020 when dropping support for 2.7
        if version_info.major == 2:
            self.assertRegex = self.assertRegexpMatches

    def tearDown(self):
        if ocbpy.__file__ != self.orig_file:
            ocbpy.__file__ = self.orig_file

        del self.out, self.orig_file, self.comp_dict, self.short_to_long
        del self.inst, self.long_to_short, self.hemi

    def test_get_boundary_directory(self):
        """ Test the default boundary directory definition  """
        self.out = files.get_boundary_directory()
        self.assertGreater(self.out.find("boundaries"), 0)

    def test_get_boundary_directory_failure(self):
        """ Test the failure of the default boundary directory definition """
        ocbpy.__file__ = "/fake_dir/test_file"
        with self.assertRaisesRegexp(OSError, "boundary file directory"):
            files.get_boundary_directory()

    def test_get_boundary_files_unknown_boundary(self):
        """ Test get_boundary_files for an unknown boundary """
        self.out = files.get_boundary_files(bound='aaa')
        self.assertDictEqual(self.out, {})

    def test_get_boundary_files(self):
        """ Test the default implementation of get_boundary_files """
        self.out = files.get_boundary_files()

        # Test only the files included with OCBpy, allow local boundary files
        # to exist.
        for ckey in self.comp_dict.keys():
            print(ckey, self.out.keys())
            self.assertTrue(ckey in self.out.keys())
            self.assertDictEqual(self.out[ckey], self.comp_dict[ckey])

    def test_get_default_file_bad_bound(self):
        """ Test get_default_file with an unknown boundary
        """
        self.out = files.get_default_file(None, None, self.hemi, bound='aaa')

        self.assertIsNone(self.out[0])
        self.assertEqual(len(self.out[1]), 0)

    def test_get_default_file_none_north_any(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        self.out = files.get_default_file(None, None, self.hemi)

        self.assertRegex(self.out[0], 'si13_north_circle.ocb')
        self.assertRegex(self.out[1], 'image')

    @unittest.skipIf(version_info.major == 2,
                     'Python 2.7 does not support subTest')
    def test_get_default_file_none_north_all(self):
        """ Test get_default_file with no range, northern hemisphere"""

        # Cycle through all possible instrument names
        for ii in self.inst[self.hemi]:
            with self.subTest(ii=ii):
                self.out = files.get_default_file(None, None, self.hemi,
                                                  instrument=ii)

                if ii in self.long_to_short.keys():
                    if self.long_to_short[ii] is None:
                        fname = None
                    else:
                        fname = "{:s}_north".format(self.long_to_short[ii])
                else:
                    fname = "{:s}_north".format(ii)

                if ii in self.short_to_long.keys():
                    iname = self.short_to_long[ii]
                else:
                    iname = ii

                if fname is None:
                    self.assertIsNone(self.out[0])
                else:
                    self.assertRegex(self.out[0], fname)
                self.assertRegex(self.out[1], iname)

        del ii, fname, iname

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_north_any(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        ii = ''
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        if self.long_to_short[ii] is None:
            fname = None
        else:
            fname = "{:s}_north".format(self.long_to_short[ii])

        self.assertRegex(self.out[0], fname)
        self.assertRegex(self.out[1], self.short_to_long[ii])

        del ii, fname

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_north_si12(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        ii = 'si12'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        self.assertRegex(self.out[0], "{:s}_north".format(ii))
        self.assertRegex(self.out[1], self.short_to_long[ii])

        del ii

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_north_si13(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        ii = 'si13'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        self.assertRegex(self.out[0], "{:s}_north".format(ii))
        self.assertRegex(self.out[1], self.short_to_long[ii])

        del ii

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_north_wic(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        ii = 'wic'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        self.assertRegex(self.out[0], "{:s}_north".format(ii))
        self.assertRegex(self.out[1], self.short_to_long[ii])

        del ii

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_north_image(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        ii = 'image'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        fname = "{:s}_north".format(self.long_to_short[ii])

        self.assertRegex(self.out[0], fname)
        self.assertRegex(self.out[1], ii)

        del ii, fname

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_north_ampere(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        ii = 'ampere'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        fname = "{:s}_north".format(self.long_to_short[ii])

        self.assertRegex(self.out[0], fname)
        self.assertRegex(self.out[1], ii)

        del ii, fname

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_north_amp(self):
        """ Test get_default_file with no range, northern hemisphere, any inst
        """
        ii = 'amp'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        self.assertRegex(self.out[0], "{:s}_north".format(ii))
        self.assertRegex(self.out[1], self.short_to_long[ii])

        del ii

    @unittest.skipIf(version_info.major == 2,
                     'Python 2.7 does not support subTest')
    def test_get_default_file_none_south_all(self):
        """ Test get_default_file with no range, southern hemisphere"""

        # Set the southern hemisphere defaults
        self.hemi = -1
        self.long_to_short[''] = 'amp'
        self.short_to_long[''] = 'ampere'
        
        # Cycle through all possible instrument names
        for ii in self.inst[self.hemi]:
            with self.subTest(ii=ii):
                self.out = files.get_default_file(None, None, self.hemi,
                                                  instrument=ii)

                if ii in self.long_to_short.keys():
                    if self.long_to_short[ii] is None:
                        fname = None
                    else:
                        fname = "{:s}_south".format(self.long_to_short[ii])
                else:
                    fname = "{:s}_south".format(ii)

                if ii in self.short_to_long.keys():
                    iname = self.short_to_long[ii]
                else:
                    iname = ii

                if fname is None:
                    self.assertIsNone(self.out[0])
                else:
                    self.assertRegex(self.out[0], fname)
                self.assertRegex(self.out[1], iname)

        del ii, fname, iname

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_south_any(self):
        """ Test get_default_file with no range, southern hemisphere, any inst
        """
        # Set the southern hemisphere defaults
        self.hemi = -1
        self.long_to_short[''] = 'amp'
        self.short_to_long[''] = 'ampere'

        ii = ''
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        fname = "{:s}_south".format(self.long_to_short[ii])

        self.assertRegex(self.out[0], fname)
        self.assertRegex(self.out[1], self.short_to_long[ii])

        del ii, fname


    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_south_ampere(self):
        """ Test get_default_file with no range, southern hemisphere, any inst
        """
        # Set the southern hemisphere defaults
        self.hemi = -1

        ii = 'ampere'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        fname = "{:s}_south".format(self.long_to_short[ii])

        self.assertRegex(self.out[0], fname)
        self.assertRegex(self.out[1], ii)

        del ii, fname

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_none_south_amp(self):
        """ Test get_default_file with no range, southern hemisphere, any inst
        """
        # Set the southern hemisphere defaults
        self.hemi = -1
        self.long_to_short[''] = 'amp'
        self.short_to_long[''] = 'ampere'

        ii = 'amp'
        self.out = files.get_default_file(None, None, self.hemi, instrument=ii)

        self.assertRegex(self.out[0], "{:s}_south".format(ii))
        self.assertRegex(self.out[1], self.short_to_long[ii])

        del ii

    @unittest.skipIf(version_info.major == 2,
                     'Python 2.7 does not support subTest')
    def test_get_default_good_file_times(self):
        """ Test get_default_file with good ranges"""
        
        # Cycle through all possible instrument names
        for ii in ['amp_north_radii.ocb', 'si13_north_circle.ocb']:
            with self.subTest(ii=ii):
                self.out = files.get_default_file(self.comp_dict[ii]['stime'],
                                                  self.comp_dict[ii]['etime'],
                                                  self.hemi)

                if self.comp_dict[ii]['instrument'] in self.short_to_long.keys():
                    iname = self.short_to_long[self.comp_dict[ii]['instrument']]
                else:
                    iname = self.comp_dict[ii]['instrument']
    
                self.assertRegex(self.out[0], ii)
                self.assertRegex(self.out[1], iname)

        del ii, iname

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_good_file_times_ampere(self):
        """ Test get_default_file with good ranges for ampere
        """

        ii = 'amp_north_radii.ocb'
        self.out = files.get_default_file(self.comp_dict[ii]['stime'],
                                          self.comp_dict[ii]['etime'],
                                          self.hemi)

        self.assertRegex(self.out[0], ii)
        self.assertRegex(self.out[1], self.comp_dict[ii]['instrument'])

        del ii

    @unittest.skipIf(version_info.major == 3, 'Already tested, remove in 2020')
    def test_get_default_file_good_file_times_image(self):
        """ Test get_default_file with good ranges for image
        """

        ii = 'si13_north_circle.ocb'
        self.out = files.get_default_file(self.comp_dict[ii]['stime'],
                                          self.comp_dict[ii]['etime'],
                                          self.hemi)

        self.assertRegex(self.out[0], ii)
        self.assertRegex(self.out[1], 'image')

        del ii

    def test_get_default_file_bad_file_times(self):
        """ Test get_default_file with bad time ranges
        """

        ii = 'si13_north_circle.ocb'
        self.hemi = -1
        self.out = files.get_default_file(self.comp_dict[ii]['stime'],
                                          self.comp_dict[ii]['etime'],
                                          self.hemi)

        self.assertIsNone(self.out[0])
        self.assertEqual(len(self.out[1]), 0)

        del ii

if __name__ == '__main__':
    unittest.main()

