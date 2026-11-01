"""Time-at-risk tests: would fail if post-event time or late events were counted."""
import unittest
import importlib.util
from pathlib import Path

class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(Path(__file__).with_name('analysis.py').exists(), 'analysis module not implemented')
        import analysis
        self.a = analysis

    def test_event_stops_exposure(self):
        event, years = self.a.exposure('2020-01-01', True, '2021-01-01', '2022-01-01')
        self.assertEqual(event, 1)
        self.assertAlmostEqual(years, 366 / 365.25)

    def test_late_event_censored(self):
        event, years = self.a.exposure('2020-01-01', True, '2023-01-01', '2022-01-01')
        self.assertEqual(event, 0)
        self.assertAlmostEqual(years, 731 / 365.25)

    def test_invalid_dates_rejected(self):
        for start, hit, end in [('2020-01-01','2019-12-31','2022-01-01'),('2022-01-01',None,'2022-01-01')]:
            with self.assertRaises(ValueError):
                self.a.exposure(start, hit is not None, hit, end)

    def test_no_event_has_positive_upper_limit(self):
        rate, lo, hi = self.a.rate_ci(0,100)
        self.assertEqual((rate,lo),(0,0))
        self.assertAlmostEqual(hi,3.688879454,places=7)

    def test_rate_units_and_missing_exposure(self):
        self.assertAlmostEqual(self.a.rate_ci(10,250)[0],4)
        self.assertEqual(self.a.rate_ci(0,0),(None,None,None))

    def test_equivalent_road_categories(self):
        self.assertTrue(hasattr(self.a,'road_flag'),'road category normalization missing')
        for v in ['맹지','세로(불)','세로한면(불)','세로각지(불)','세각(불)']:
            self.assertEqual(self.a.road_flag(v),1,v)
        for v in ['세로(가)','세로한면(가)','세로각지(가)','세각(가)','소로한면','광대한면']:
            self.assertEqual(self.a.road_flag(v),0,v)
        for v in ['',None,'미조회','unknown']:
            self.assertIsNone(self.a.road_flag(v),v)

    def test_road_share_excludes_unknown_denominator(self):
        self.assertTrue(hasattr(self.a,'road_summary'),'explicit road denominator summary missing')
        count, known, pct = self.a.road_summary([1, 0, None, float('nan')])
        self.assertEqual((count, known, pct), (1, 2, 50.0))

    def test_road_no_data_is_distinct_from_zero_constraints(self):
        self.assertTrue(hasattr(self.a,'road_summary'),'explicit road denominator summary missing')
        self.assertEqual(self.a.road_summary([None, float('nan')]), (0, 0, None))
        self.assertEqual(self.a.road_summary([0, 0]), (0, 2, 0.0))

if __name__ == '__main__':
    unittest.main()
