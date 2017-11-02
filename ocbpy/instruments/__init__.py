# -*- coding: utf-8 -*-
# Copyright (C) 2017
# Full license can be found in LICENSE.txt
"""Instrument specific Open-Closed field line Boundary (OCB) magnetic gridding

Contains
---------------------------------------------------------------------------
supermag    SuperMAG data available at: http://supermag.jhuapl.edu/
vort        SuperDARN vorticity data may be obtained from: gchi@bas.ac.uk
general     General file loading and testing routines
---------------------------------------------------------------------------
"""
import logging

# Imports
#---------------------------------------------------------------------

try:
    from ocbpy.instruments import (general)
    from ocbpy.instruments.general import (test_file)
except ImportError as e:
    logging.exception('problem importing general: ' + str(e))

try:
    from ocbpy.instruments import (supermag)
except ImportError as e:
    logging.exception('problem importing supermag: ' + str(e))

try:
    from ocbpy.instruments import (vort)
except ImportError as e:
    logging.exception('problem importing vort: ' + str(e))

try:
    from ocbpy.instruments import (pysat)
except ImportError as e:
    logging.exception('problem importing pysat: ' + str(e))
