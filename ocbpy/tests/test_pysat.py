#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2017, AGB & GC
# Full license can be found in License.md
#-----------------------------------------------------------------------------
""" Tests the ocb_scaling class and functions
"""

import unittest
import numpy as np

import logbook

import ocbpy
try:
    import pysat
    import ocbpy.instruments.pysat_instruments as ocb_pysat
    no_pysat = False
except ImportError:
    no_pysat = True


@unittest.skipIf(no_pysat, "pysat not installed, cannot test routines")
class TestPysatUtils(unittest.TestCase):
    def setUp(self):
        """ Initialization performed through input """

        # Set the default function values
        self.meta = None
        self.ocb_key = 'ocb_test'
        self.pysat_key = 'dummy1'
        self.notes = None
        self.isvector = False
        self.test_inst = None;
        self.ocb = None
        self.added_keys = list()
        self.pysat_keys = list()
        self.arevectors = list(),
        self.nkeys = 0

    def tearDown(self):
        """Delete attributes"""
        del self.meta, self.ocb_key, self.pysat_key, self.notes, self.isvector
        del self.test_inst, self.ocb, self.added_keys, self.pysat_keys
        del self.arevectors, self.nkeys

    def test_ocb_metadata(self):
        """ Test that metadata was added properly
        """

        if self.meta is None:
            self.assertTrue(True)
        else:
            self.assertTrue(self.ocb_key in self.meta.keys())
            if self.pysat_key is not None:
                self.assertTrue(self.pysat_key in self.meta.keys())

            if self.isvector:
                # Test the fill value
                self.assertIsNone(self.meta[self.ocb_key][self.meta.fill_label])
            elif self.pysat_key is not None:
                # Test the elements that are identical
                for ll in [self.meta.units_label, self.meta.scale_label,
                           self.meta.min_label, self.meta.max_label,
                           self.meta.fill_label]:
                    try:
                        if np.isnan(self.meta[self.pysat_key][ll]):
                            self.assertTrue( \
                                        np.isnan(self.meta[self.ocb_key][ll]))
                        else:
                            self.assertEqual(self.meta[self.ocb_key][ll],
                                             self.meta[self.pysat_key][ll])
                    except TypeError:
                        self.assertRegexpMatches(self.meta[self.ocb_key][ll],
                                                 self.meta[self.pysat_key][ll])

            # Test the elements that have "OCB" appended to the text
            for ll in [self.meta.name_label, self.meta.axis_label,
                       self.meta.plot_label]:
                sline = self.meta[self.ocb_key][ll].split(" ")
                self.assertRegexpMatches(sline[0], "OCB")
                if not self.isvector and self.pysat_key is not None:
                    self.assertRegexpMatches(" ".join(sline[1:]),
                                             self.meta[self.pysat_key][ll])

            # Test the remaining elements
            self.assertEqual(self.meta[self.ocb_key][ \
                                self.meta.desc_label].find("Open Closed"), 0)
            if self.notes is not None:
                self.assertRegexpMatches(self.meta[self.ocb_key][ \
                                        self.meta.notes_label], self.notes)

            del ll, sline

    def test_ocb_added(self):
        """ Test if OCB data was added correctly
        """

        if self.test_inst is None:
            self.assertTrue(True)
        else:
            if len(self.arevectors) < len(self.added_keys):
                self.arevectors = [False for okey in self.added_keys]
            
            self.assertEqual(len(self.added_keys), self.nkeys)

            for i, okey in enumerate(self.added_keys):
                # Test to see that data was added
                self.assertTrue(okey in self.test_inst.data.columns)
                                
                # Test the metadata
                self.meta = self.test_inst.meta
                self.pysat_key = self.pysat_keys[i]
                self.isvector = self.arevectors[i]
                self.ocb_key = okey
                self.test_ocb_metadata()

                # Test to see that data within 10 minutes of the test OCBs has
                # OCB locations and other data is NaN
                match_data = self.test_inst[okey]
                mask_data = np.not_equal(match_data, None) \
                    if self.arevectors[i] else np.isfinite(match_data)
                match_data = match_data[mask_data]

                self.assertEqual(len(match_data), 194)
                for ii in match_data.index:
                    check_time = abs(ii - self.ocb.dtime).min().total_seconds()
                    self.assertLessEqual(check_time, 600.0)
                if self.arevectors[i]:
                    self.assertTrue(isinstance(match_data[0],
                                               ocbpy.ocb_scaling.VectorData))
                elif self.pysat_keys[i] is not None:
                    pysat_data = self.test_inst[self.pysat_keys[i]][mask_data]
                    rscale = (self.ocb.r / (90.0 - self.ocb.boundary_lat))**2
                    self.assertGreaterEqual(match_data.min(),
                                            pysat_data.min() * rscale.min())
                    self.assertGreaterEqual(pysat_data.max() * rscale.max(),
                                            match_data.max())

            del okey, match_data, mask_data, ii, check_time


@unittest.skipIf(not no_pysat, "pysat installed, cannot test failure")
class TestPysatFailure(unittest.TestCase):
    def setUp(self):
        """ No initialization needed """
        pass

    def tearDown(self):
        """ No teardown needed"""
        pass

    def test_import_failure(self):
        """ Test pysat import failure"""

        with self.assertRaisesRegexp(ImportError, 'unable to load the pysat'):
            import ocbpy.instruments.pysat_instruments as ocb_pysat


@unittest.skipIf(no_pysat, "pysat not installed")
class TestPysatStructure(unittest.TestCase):
    def setUp(self):
        """ No setup needed"""
        pass

    def tearDown(self):
        """ No teardown needed"""
        pass

    def test_add_ocb_to_data_defaults(self):
        """ test the add_ocb_to_data function defaults"""

        defaults = ocb_pysat.add_ocb_to_data.func_defaults

        for i in [0, 1]:
            self.assertEqual(defaults[i], '')

        for i in [2, 3, 5]:
            self.assertListEqual(defaults[i], list())

        for i in [6, 7]:
            self.assertIsNone(defaults[i])

        for i, val in enumerate([600, 7, 8.0, 23.0, 10.0, 0.15]):
            self.assertEqual(defaults[i+8], val)

        self.assertDictEqual(defaults[4], dict())

    def test_add_ocb_to_metadata_defaults(self):
        """ test the add_ocb_to_metadata function defaults"""

        defaults = ocb_pysat.add_ocb_to_metadata.func_defaults

        for i in [0, 2]:
            self.assertFalse(defaults[i])

        self.assertRegexpMatches(defaults[1], '')


@unittest.skipIf(no_pysat, "pysat not installed")
class TestPysatMethods(unittest.TestCase):

    def setUp(self):
        """ Initialize the OCBoundary object using the test file, as well as
        the VectorData object
        """
        from os import path
        import pandas as pds
        
        ocb_dir = path.split(ocbpy.__file__)[0]
        self.test_file = path.join(ocb_dir, "tests", "test_data",
                                   "test_north_circle")
        self.assertTrue(path.isfile(self.test_file))
        self.ocb = ocbpy.OCBoundary(self.test_file)
        self.ocb.rec_ind = 27

        self.test_inst = pysat.Instrument('pysat', 'testing', tag='50400',
                                          clean_level='clean',
                                          update_files=True, \
                            file_date_range=pds.date_range(self.ocb.dtime[0],
                                                           self.ocb.dtime[-1],
                                                           freq='1D'))
        self.test_inst.load(date=self.ocb.dtime[self.ocb.rec_ind])

        self.log_handler = logbook.TestHandler()
        self.log_handler.push_thread()

        self.utils = TestPysatUtils("test_ocb_metadata")
        self.utils.setUp()

    def tearDown(self):
        self.log_handler.pop_thread()
        self.utils.tearDown()
        del self.test_file, self.log_handler, self.test_inst, self.ocb
        del self.utils

    def test_add_ocb_to_metadata(self):
        """ Test the metadata adding routine
        """
        ocb_pysat.add_ocb_to_metadata(self.test_inst, "ocb_test", "dummy1",
                                      notes="test notes")

        self.utils.meta = self.test_inst.meta
        self.utils.notes = 'test notes'
        self.utils.test_ocb_metadata()

    def test_add_ocb_to_metadata_vector(self):
        """ Test the metadata adding routine for vector data
        """
        ocb_pysat.add_ocb_to_metadata(self.test_inst, "ocb_test", "dummy1",
                                      notes="test notes", isvector=True)

        self.utils.meta = self.test_inst.meta
        self.utils.notes = 'test notes'
        self.utils.isvector = True
        self.utils.test_ocb_metadata()

    def test_no_overwrite_metadata(self):
        """ Test the overwrite block on metadata adding routine
        """
        self.test_add_ocb_to_metadata()
        ocb_pysat.add_ocb_to_metadata(self.test_inst, "ocb_test", "dummy1",
                                      notes="test notes two", overwrite=False)

        self.assertEqual(len(self.log_handler.formatted_records), 1)
        self.assertTrue(self.log_handler.formatted_records[0].find( \
                                        'OCB data already has metadata') > 0)

    def test_overwrite_metadata(self):
        """ Test the overwrite permission on metadata adding routine
        """
        self.test_add_ocb_to_metadata()
        ocb_pysat.add_ocb_to_metadata(self.test_inst, "ocb_test", "dummy1",
                                      notes="test notes two", overwrite=True)

        meta = self.test_inst.meta
        self.assertRegexpMatches(meta['ocb_test'][meta.notes_label],
                                 "test notes two")

        del meta

    def test_add_ocb_to_data_ocb_obj(self):
        """ Test adding ocb to pysat data using the loaded OCB object
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  ocb=self.ocb)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None

        self.utils.test_inst = self.test_inst
        self.utils.ocb = self.ocb
        self.utils.arevectors = [False for i in range(self.utils.nkeys)]
        self.utils.test_ocb_added()
    
        del aa

    def test_add_ocb_to_data_ocb_file(self):
        """ Test adding ocb to pysat data using the OCB file name
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  ocbfile=self.test_file)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None
        self.arevectors = [False for i in range(self.utils.nkeys)]
        self.utils.test_ocb_added()

        del aa

    def test_add_ocb_to_data_evar(self):
        """ Test adding ocb to pysat with E-field related variables
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  evar_names=['dummy1'], ocb=self.ocb)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None
        self.arevectors = [False for i in range(self.utils.nkeys)]

        self.utils.test_ocb_added()

        del aa

    def test_add_ocb_to_data_curl_evar(self):
        """ Test adding ocb to pysat with Curl E-field related variables
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  curl_evar_names=['dummy2'], ocb=self.ocb)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None

        self.utils.test_ocb_added()
        del aa

    def test_add_ocb_to_data_evar_vect(self):
        """ Test adding ocb to pysat with Curl E-field related vectors
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  evar_names=['vect_evar'],
                                  vector_names={'vect_evar':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s'}},
                                  ocb=self.ocb)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_add_ocb_to_data_curl_evar_vect(self):
        """ Test adding ocb to pysat with Curl E-field related vectors
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  curl_evar_names=['vect_cevar'],
                                  vector_names={'vect_cevar':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s'}},
                                  ocb=self.ocb)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_add_ocb_to_data_custom_vect(self):
        """ Test adding ocb to pysat with custom scaled variables
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  vector_names={'vect_cust':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s',
                                                 'scale_func': None}},
                                  ocb=self.ocb)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_add_ocb_to_data_all_types(self):
        """ Test adding ocb to pysat with E-field, Curl, and Vector data
        """

        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  evar_names=['dummy1'],
                                  curl_evar_names=['dummy2'],
                                  vector_names={'vect_cust':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s',
                                                 'scale_func': None}},
                                  ocb=self.ocb)

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_add_ocb_to_data_no_file(self):
        """ Test adding ocb to pydat data when no OCB file or data is provided
        """
        ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                  ocbfile=None)

        self.assertEqual(len(self.log_handler.formatted_records), 1)
        self.assertTrue(self.log_handler.formatted_records[0].find( \
                                        'no data in OCB file') > 0)

    def test_add_ocb_to_data_bad_mlat(self):
        """ Test failure of unknown mlat key in add_ocb_to_data
        """

        with self.assertRaisesRegexp(ValueError,
                                     'unknown magnetic latitude name: mlat'):
            ocb_pysat.add_ocb_to_data(self.test_inst, "mlat", "mlt",
                                      ocb=self.ocb)

    def test_add_ocb_to_data_bad_mlt(self):
        """ Test failure of unknown mlt key in add_ocb_to_data
        """

        with self.assertRaisesRegexp(ValueError,
                                     'unknown magnetic local time name: bad'):
            ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "bad",
                                      ocb=self.ocb)

    def test_add_ocb_to_data_bad_evar(self):
        """ Test failure of unknown E field key in add_ocb_to_data
        """

        with self.assertRaisesRegexp(ValueError,
                                     'at least one unknown E field name'):
            ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                      evar_names=["bad"], ocb=self.ocb)

    def test_add_ocb_to_data_bad_curl(self):
        """ Test failure of unknown E field key in add_ocb_to_data
        """

        with self.assertRaisesRegexp(ValueError,
                                     'at least one unknown E field name'):
            ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                      curl_evar_names=["bad"], ocb=self.ocb)

    def test_add_ocb_to_data_bad_vector_scale(self):
        """ Test failure of missing scaling function in add_ocb_to_data
        """

        with self.assertRaisesRegexp(ValueError,
                                     'missing scaling function for: bad'):
            ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                      vector_names={'bad': {'aacgm_n': 'bad_n',
                                                            'aacgm_e': 'bad_e',
                                                            'dat_name': 'bad',
                                                            'dat_units':''}},
                                     ocb=self.ocb)

    def test_add_ocb_to_data_bad_vector_name(self):
        """ Test failure of missing scaling function in add_ocb_to_data
        """

        with self.assertRaisesRegexp(ValueError,
                                     'unknown vector name: bad_n'):
            ocb_pysat.add_ocb_to_data(self.test_inst, "latitude", "mlt",
                                      evar_names=['bad'],
                                      vector_names={'bad': {'aacgm_n': 'bad_n',
                                                            'aacgm_e': 'dummy1',
                                                            'dat_name': 'bad',
                                                            'dat_units':''}},
                                     ocb=self.ocb)

            
@unittest.skipIf(no_pysat, "pysat not installed")
class TestPysatCustMethods(unittest.TestCase):

    def setUp(self):
        """ Initialize the OCBoundary object using the test file, as well as
        the VectorData object
        """
        from os import path
        import pandas as pds
        
        ocb_dir = path.split(ocbpy.__file__)[0]
        self.test_file = path.join(ocb_dir, "tests", "test_data",
                                   "test_north_circle")
        self.assertTrue(path.isfile(self.test_file))
        self.ocb = ocbpy.OCBoundary(self.test_file)
        self.ocb.rec_ind = 27

        self.test_inst = pysat.Instrument('pysat', 'testing', tag='50400',
                                          clean_level='clean',
                                          update_files=True, \
                            file_date_range=pds.date_range(self.ocb.dtime[0],
                                                           self.ocb.dtime[-1],
                                                           freq='1D'))

        self.log_handler = logbook.TestHandler()
        self.log_handler.push_thread()

        self.utils = TestPysatUtils("test_ocb_metadata")
        self.utils.setUp()

    def tearDown(self):
        self.log_handler.pop_thread()
        self.utils.tearDown()
        del self.test_file, self.log_handler, self.test_inst, self.ocb
        del self.utils

    def test_load(self):
        """ Test the pysat file loading"""
        self.test_inst.load(date=self.ocb.dtime[self.ocb.rec_ind])
        self.assertFalse(self.test_inst.empty)
        self.assertTrue('latitude' in self.test_inst.data.columns)
        self.assertTrue('mlt' in self.test_inst.data.columns)

    def test_cust_add_ocb_to_data_ocb_obj(self):
        """ Test adding ocb to pysat data with load using the loaded OCB object
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  ocb=self.ocb)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None

        self.utils.test_inst = self.test_inst
        self.utils.ocb = self.ocb
        self.utils.arevectors = [False for i in range(self.utils.nkeys)]
        self.utils.test_ocb_added()
    
        del aa

    def test_cust_add_ocb_to_data_ocb_file(self):
        """ Test adding ocb to pysat data with load using the OCB file name
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  ocbfile=self.test_file)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None
        self.arevectors = [False for i in range(self.utils.nkeys)]
        self.utils.test_ocb_added()

        del aa

    def test_cust_add_ocb_to_data_evar(self):
        """ Test adding ocb to pysat with load including E-field variables
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  evar_names=['dummy1'], ocb=self.ocb)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None
        self.arevectors = [False for i in range(self.utils.nkeys)]

        self.utils.test_ocb_added()

        del aa

    def test_cust_add_ocb_to_data_curl_evar(self):
        """ Test adding ocb to pysat with load including Curl E-field variables
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  curl_evar_names=['dummy2'], ocb=self.ocb)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = [aa.split("_ocb")[0]
                                 for aa in self.utils.added_keys]
        self.assertTrue('r_corr' in self.utils.pysat_keys)
        self.utils.pysat_keys[self.utils.pysat_keys.index("r_corr")] = None

        self.utils.test_ocb_added()
        del aa

    def test_cust_add_ocb_to_data_evar_vect(self):
        """ Test adding ocb to pysat with load including Curl E-field vectors
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  evar_names=['vect_evar'],
                                  vector_names={'vect_evar':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s'}},
                                  ocb=self.ocb)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_cust_add_ocb_to_data_curl_evar_vect(self):
        """ Test adding ocb to pysat with load including Curl E-field vectors
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  curl_evar_names=['vect_cevar'],
                                  vector_names={'vect_cevar':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s'}},
                                  ocb=self.ocb)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_cust_add_ocb_to_data_custom_vect(self):
        """ Test adding ocb to pysat with load including custom scaled variables
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  vector_names={'vect_cust':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s',
                                                 'scale_func': None}},
                                  ocb=self.ocb)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_cust_add_ocb_to_data_all_types(self):
        """ Test adding ocb to pysat with load including E-field, Curl, & vects
        """

        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  evar_names=['dummy1'],
                                  curl_evar_names=['dummy2'],
                                  vector_names={'vect_cust':
                                                {'aacgm_n': 'dummy1',
                                                 'aacgm_e': 'dummy2',
                                                 'dat_name': 'vect',
                                                 'dat_units': 'm/s',
                                                 'scale_func': None}},
                                  ocb=self.ocb)

        self.test_load()

        self.utils.added_keys = [kk for kk in self.test_inst.meta.keys()
                                 if kk.find('_ocb') > 0]
        self.utils.nkeys = len(self.utils.added_keys)
        self.utils.pysat_keys = list()
        self.utils.arevectors = list()
        for aa in self.utils.added_keys:
            pp = aa.split("_ocb")[0]
            self.utils.arevectors.append(False)
            if pp == "r_corr":
                pp = None
            elif pp not in self.test_inst.data.columns:
                pp = 'dummy1'
                self.utils.arevectors[-1] = True
            self.utils.pysat_keys.append(pp)
        
        self.utils.test_ocb_added()
        
        del aa, pp

    def test_cust_add_ocb_to_data_no_file(self):
        """ Test adding ocb to pysat with load using no OCB file or data
        """
        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  ocbfile=None)

        self.test_load()

        self.assertEqual(len(self.log_handler.formatted_records), 1)
        self.assertTrue(self.log_handler.formatted_records[0].find( \
                                        'no data in OCB file') > 0)

    def test_cust_add_ocb_to_data_bad_mlat(self):
        """ Test failure of unknown mlat key in add_ocb_to_data in custom func
        """

        with self.assertRaisesRegexp(ValueError,
                                     'unknown magnetic latitude name: mlat'):
            ocb_pysat.add_ocb_to_data(self.test_inst, "mlat", "mlt",
                                      ocb=self.ocb)

    def test_cust_add_ocb_to_data_bad_mlt(self):
        """ Test failure of unknown mlt key in add_ocb_to_data in custom func
        """
        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='bad',
                                  ocb=self.ocb)

        with self.assertRaisesRegexp(ValueError,
                                     'unknown magnetic local time name: bad'):
            self.test_load()

    def test_cust_add_ocb_to_data_bad_evar(self):
        """ Test failure of unknown E field key in custom func
        """
        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  evar_names=['bad'], ocb=self.ocb)

        with self.assertRaisesRegexp(ValueError,
                                     'at least one unknown E field name'):
            self.test_load()

    def test_cust_add_ocb_to_data_bad_curl(self):
        """ Test failure of unknown E field key in custom func
        """
        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  curl_evar_names=['bad'], ocb=self.ocb)

        with self.assertRaisesRegexp(ValueError,
                                     'at least one unknown E field name'):
            self.test_load()

    def test_cust_add_ocb_to_data_bad_vector_scale(self):
        """ Test failure of missing scaling function in custom func
        """
        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  vector_names={'bad': {'aacgm_n': 'bad_n',
                                                        'aacgm_e': 'bad_e',
                                                        'dat_name': 'bad',
                                                        'dat_units':''}},
                                  ocb=self.ocb)

        with self.assertRaisesRegexp(ValueError,
                                     'missing scaling function for: bad'):
            self.test_load()

    def test_cust_add_ocb_to_data_bad_vector_name(self):
        """ Test failure of missing scaling function in custom func
        """
        self.test_inst.custom.add(ocb_pysat.add_ocb_to_data, 'modify',
                                  mlat_name='latitude', mlt_name='mlt',
                                  evar_names=['bad'],
                                  vector_names={'bad': {'aacgm_n': 'bad_n',
                                                        'aacgm_e': 'dummy1',
                                                        'dat_name': 'bad',
                                                        'dat_units':''}},
                                  ocb=self.ocb)

        with self.assertRaisesRegexp(ValueError,
                                     'unknown vector name: bad_n'):
            self.test_load()


if __name__ == '__main__':
    unittest.main()
