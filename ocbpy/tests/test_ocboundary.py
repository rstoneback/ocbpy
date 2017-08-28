#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2017, AGB & GC
# Full license can be found in License.md
#-----------------------------------------------------------------------------
""" Tests the ocboundary class and functions
"""

import ocbpy
import unittest

class TestOCBoundaryMethods(unittest.TestCase):

    def setUp(self):
        """ Initialize the OCBoundary object using the test file
        """
        from os.path import isfile

        ocb_dir = ocbpy.__file__.split("/")
        test_north = "{:s}/{:s}".format("/".join(ocb_dir[:-1]),
                                       "tests/test_data/test_north_circle")
        test_south = "{:s}/{:s}".format("/".join(ocb_dir[:-1]),
                                       "tests/test_data/test_south_circle")
        self.assertTrue(isfile(test_north))
        self.assertTrue(isfile(test_south))
        self.ocb = ocbpy.ocboundary.OCBoundary(filename=test_north)
        self.ocb_south = ocbpy.ocboundary.OCBoundary(filename=test_south,
                                                     instrument="Ampere",
                                                     hemisphere=-1)

    def tearDown(self):
        del self.ocb, self.ocb_south

    def test_nofile_init(self):
        """ Ensure that the class can be initialised without loading a file.
        """
        nofile_ocb = ocbpy.ocboundary.OCBoundary(filename=None)

        self.assertIsNone(nofile_ocb.filename)
        self.assertIsNone(nofile_ocb.dtime)
        self.assertEqual(nofile_ocb.records, 0)
        del nofile_ocb

    def test_wrong_instrument(self):
        """ Ensure that no file is loaded if user wants an instrument other
        than image, but asks for default file
        """

        nofile_ocb = ocbpy.ocboundary.OCBoundary(instrument="AMPERE")

        self.assertIsNone(nofile_ocb.filename)
        self.assertIsNone(nofile_ocb.dtime)
        self.assertEqual(nofile_ocb.records, 0)
        del nofile_ocb
        
    def test_load(self):
        """ Ensure that records from the default file were loaded and the
        default latitude boundary was set
        """
        self.assertGreater(self.ocb.records, 0)
        self.assertEquals(self.ocb.boundary_lat, 74.0)

        self.assertGreater(self.ocb_south.records, 0)
        self.assertEquals(self.ocb_south.boundary_lat, -72.0)

    def test_partial_load(self):
        """ Ensure limited sections of a file can be loaded
        """
        import datetime as dt

        stime = self.ocb.dtime[0] + dt.timedelta(seconds=1)
        etime = self.ocb.dtime[-1] - dt.timedelta(seconds=1)

        # Load all but the first and last records
        part_ocb = ocbpy.ocboundary.OCBoundary(filename=self.ocb.filename,
                                               stime=stime, etime=etime,
                                               boundary_lat=75.0)

        self.assertEquals(self.ocb.records, part_ocb.records + 2)
        self.assertEquals(part_ocb.boundary_lat, 75.0)
        del part_ocb

    def test_first_good(self):
        """ Test to see that we can find the first good point
        """
        self.ocb.rec_ind = -1
        self.ocb_south.rec_ind = -1

        self.ocb.get_next_good_ocb_ind()
        self.ocb_south.get_next_good_ocb_ind()

        self.assertGreater(self.ocb.rec_ind, -1)
        self.assertLess(self.ocb.rec_ind, self.ocb.records)

        self.assertGreater(self.ocb_south.rec_ind, -1)
        self.assertLess(self.ocb_south.rec_ind, self.ocb_south.records)

    def test_normal_coord_north(self):
        """ Test to see that the normalisation is performed properly in the
        northern hemisphere
        """
        self.ocb.rec_ind = 27
        
        ocb_lat, ocb_mlt = self.ocb.normal_coord(90.0, 0.0)
        self.assertAlmostEquals(ocb_lat, 86.8658623137)
        self.assertAlmostEquals(ocb_mlt, 17.832)

    def test_revert_coord_north(self):
        """ Test to see that the reversion to AACGM coordinates is performed
        properly
        """
        self.ocb.rec_ind = 27
        
        ocb_lat, ocb_mlt = self.ocb.normal_coord(80.0, 0.0)
        aacgm_lat, aacgm_mlt = self.ocb.revert_coord(ocb_lat, ocb_mlt)
        self.assertAlmostEquals(aacgm_lat, 80.0)
        self.assertAlmostEquals(aacgm_mlt, 0.0)

    def test_normal_coord_south(self):
        """ Test to see that the normalisation is performed properly in the
        southern hemisphere
        """
        self.ocb_south.rec_ind = 8
        
        ocb_lat, ocb_mlt = self.ocb_south.normal_coord(-90.0, 0.0)
        self.assertAlmostEquals(ocb_lat, -86.4)
        self.assertAlmostEquals(ocb_mlt, 6.0)

    def test_year_soy_to_datetime(self):
        """ Test to see that the seconds of year conversion works
        """
        import datetime as dt

        self.assertEquals(ocbpy.ocboundary.year_soy_to_datetime(2001, 0),
                          dt.datetime(2001,1,1))

    def test_convert_time(self):
        """ Test to see that the datetime construction works
        """
        import datetime as dt

        # Test the default date implimentation
        self.assertEquals(ocbpy.ocboundary.convert_time(date="2001-01-01",
                                                        tod="00:00:00"),
                          dt.datetime(2001,1,1))

        # Test the custom date implimentation
        self.assertEquals(ocbpy.ocboundary.convert_time(date="2001-01-01", \
                            tod="00-00-00", datetime_fmt="%Y-%m-%d %H-%M-%S"),
                          dt.datetime(2001,1,1))

        # Test the year-soy implimentation
        self.assertEquals(ocbpy.ocboundary.convert_time(year=2001, soy=0),
                          dt.datetime(2001,1,1))
        
    def test_match(self):
        """ Test to see that the data matching works properly
        """
        import numpy as np
        import datetime as dt
    
        # Build a array of times for a test dataset
        self.ocb.rec_ind = 27
        test_times = np.arange(self.ocb.dtime[self.ocb.rec_ind],
                               self.ocb.dtime[self.ocb.rec_ind + 5],
                               dt.timedelta(seconds=600)).astype(dt.datetime)

        # Because the array starts at the first good OCB, will return zero
        idat = ocbpy.ocboundary.match_data_ocb(self.ocb, test_times, idat=0)
        self.assertEquals(idat, 0)
        self.assertEquals(self.ocb.rec_ind, 27)

        # The next test time will cause the OCB to cycle forward to a new
        # record
        idat = ocbpy.ocboundary.match_data_ocb(self.ocb, test_times, idat=1)
        self.assertEquals(idat, 1)
        self.assertEquals(self.ocb.rec_ind, 31)
        self.assertLess(abs((test_times[idat] -
                             self.ocb.dtime[self.ocb.rec_ind]).total_seconds()),
                        600.0)

if __name__ == '__main__':
    unittest.main()
