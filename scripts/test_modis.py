#!/usr/bin/env python3
"""Tests for the MOD13Q1 VI Quality bit screen."""
import unittest
import numpy as np
from fetch_modis import good_modis_quality


class ModisQualityTests(unittest.TestCase):
    def test_good_land_pixel(self):
        self.assertTrue(bool(good_modis_quality(np.array([1 << 11], dtype=np.uint16))[0]))

    def test_cloud_is_rejected(self):
        self.assertFalse(bool(good_modis_quality(np.array([(1 << 11) | 0b10], dtype=np.uint16))[0]))

    def test_adjacent_cloud_is_rejected(self):
        self.assertFalse(bool(good_modis_quality(np.array([(1 << 11) | (1 << 8)], dtype=np.uint16))[0]))

    def test_mixed_cloud_is_rejected(self):
        self.assertFalse(bool(good_modis_quality(np.array([(1 << 11) | (1 << 10)], dtype=np.uint16))[0]))

    def test_snow_and_shadow_are_rejected(self):
        values = [(1 << 11) | (1 << 14), (1 << 11) | (1 << 15)]
        self.assertEqual(good_modis_quality(np.array(values, dtype=np.uint16)).tolist(), [False, False])

    def test_water_is_rejected(self):
        self.assertFalse(bool(good_modis_quality(np.array([0], dtype=np.uint16))[0]))

    def test_low_usefulness_is_rejected(self):
        self.assertFalse(bool(good_modis_quality(np.array([(1 << 11) | (9 << 2)], dtype=np.uint16))[0]))


if __name__ == "__main__":
    unittest.main()
